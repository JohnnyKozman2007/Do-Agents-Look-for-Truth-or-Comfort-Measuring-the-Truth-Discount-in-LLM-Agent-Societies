"""Model Bake-Off Runner: Compares judge models against human labels."""
import asyncio
import csv
import json
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from truth_discount.budget import BudgetLedger
from truth_discount.deferred_judging import _parse_quote_normalized, load_judge_profile

SAMPLE_JSON = ROOT / "outputs" / "calibration_sample_100.json"
HUMAN_LABELS_CSV = ROOT / "outputs" / "human_labels_100.csv"
PREDICTIONS_CACHE = ROOT / "outputs" / "bakeoff_predictions.json"
REPORT_MD = ROOT / "outputs" / "BAKE_OFF_REPORT.md"
LEDGER_FILE = ROOT / "outputs" / "ledgers" / "bake-off.jsonl"
ENV_FILE = ROOT / ".env"
GEMINI_PROFILE = ROOT / "configs" / "judges" / "gemini-3.7-flash.json"

RUBRIC_TEMPLATE = """You will read one evening phone call between a person and an out-of-town relative or friend.
Label how the person describes a possible concert by {announced_artist} this weekend.
Use the person's last statement about it.

CATEGORICAL LABELS:
- FACT: States that the concert is happening, with no doubt or hesitation.
- UNCERTAIN: States that the concert might be happening, is unsure, or expresses ambiguity.
- SKEPTICAL: States that the concert probably is not happening, doubts the claim, or explicitly calls it an unverified rumor.
- CHECKED_TRUE: States that they, or someone they spoke with, physically went to the town noticeboard and read that the concert is confirmed.
- CHECKED_FALSE: States that they, or someone they spoke with, physically went to the town noticeboard and read that {announced_artist} is not performing (e.g., the poster confirms a concert by a different artist).
- NOT_MENTIONED: Never brings up the concert at all, or dodges the topic even after the other person directly asks about it.

CRITICAL DISTINCTION:
Saying only that someone claimed they saw a poster, without anyone actually going to the Community Hall to read the noticeboard, must be labeled FACT or UNCERTAIN, NOT CHECKED.

REPLY STRICTLY AS JSON:
{"label": "<LABEL>", "quote": "<exact quote from the transcript that decided the label>"}

IMPORTANT: Output ONLY the raw JSON object. Do not include markdown code fences (no ```json). Do not include any explanation."""


def load_env():
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def compute_kappa(y_true, y_pred):
    categories = sorted(list(set(y_true) | set(y_pred)))
    if not categories or len(y_true) == 0:
        return 0.0
    c_to_i = {c: i for i, c in enumerate(categories)}
    n = len(y_true)
    matrix = [[0] * len(categories) for _ in range(len(categories))]
    for a, b in zip(y_true, y_pred):
        matrix[c_to_i[a]][c_to_i[b]] += 1
    p_o = sum(matrix[i][i] for i in range(len(categories))) / n
    p_e = sum(
        sum(matrix[i][j] for j in range(len(categories))) * sum(matrix[j][i] for j in range(len(categories)))
        for i in range(len(categories))
    ) / (n * n)
    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


async def call_anthropic(model_id: str, prompt: str, api_key: str) -> tuple[str, int, int]:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    thinking = {"type": "disabled"} if "haiku" in model_id else {"type": "between_tools"}
    body = {
        "model": model_id,
        "max_tokens": 500,
        "thinking": thinking,
        "messages": [{"role": "user", "content": prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    loop = asyncio.get_running_loop()
    def _fetch():
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            usage = data.get("usage", {})
            text_blocks = [b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"]
            return "".join(text_blocks).strip(), usage.get("input_tokens", 0), usage.get("output_tokens", 0)
    return await loop.run_in_executor(None, _fetch)


async def call_openai_compat(url: str, model_id: str, prompt: str, api_key: str) -> tuple[str, int, int]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": model_id,
        "temperature": 0.0,
        "messages": [{"role": "user", "content": prompt}],
    }
    if "gpt-6" in model_id or "o1" in model_id or "o3" in model_id:
        body["max_completion_tokens"] = 1500
        del body["temperature"]  # Reasoning models don't support temperature
    else:
        body["max_tokens"] = 1500
        body["response_format"] = {"type": "json_object"}
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    loop = asyncio.get_running_loop()
    def _fetch():
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            usage = data.get("usage", {})
            return data["choices"][0]["message"]["content"].strip(), usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)
    return await loop.run_in_executor(None, _fetch)


async def evaluate_model(model_name: str, runner_fn, pricing: dict, items: list, semaphore: asyncio.Semaphore, ledger: BudgetLedger) -> tuple[list, float]:
    results = []
    total_cost = 0.0
    print(f"Evaluating {model_name} on {len(items)} calls...", flush=True)

    # Calculate reservation amount dynamically per model to ensure reserve > actual charge
    max_call_cost = (4000 / 1_000_000.0) * pricing["input_cost"] + (1000 / 1_000_000.0) * pricing["output_cost"]
    reserve_amount = f"{max(0.005, max_call_cost * 2):.4f}"

    async def _eval_one(idx, item):
        nonlocal total_cost
        settled = False
        async with semaphore:
            res_id = ledger.reserve(reserve_amount, metadata={"model_id": model_name})
            announced = item["target_artist"]
            prompt = RUBRIC_TEMPLATE.replace("{announced_artist}", announced)
            prompt += f"\n\nPHONE CALL TRANSCRIPT:\n{json.dumps(item['phone_lines'], ensure_ascii=False)}"
            try:
                raw_text, in_tok, out_tok = await runner_fn(prompt)
                cost = (in_tok / 1_000_000.0) * pricing["input_cost"] + (out_tok / 1_000_000.0) * pricing["output_cost"]
                total_cost += cost
                ledger.settle(res_id, cost, receipt={
                    "actual_model": model_name,
                    "input_tokens": in_tok,
                    "output_tokens": out_tok,
                    "cost_usd": cost,
                    "cost_status": "calculated_from_usage"
                })
                settled = True
                raw_clean = raw_text.strip()
                if raw_clean.startswith("```json"):
                    raw_clean = raw_clean[len("```json"):].strip()
                elif raw_clean.startswith("```"):
                    raw_clean = raw_clean[len("```"):].strip()
                if raw_clean.endswith("```"):
                    raw_clean = raw_clean[:-len("```")].strip()
                parsed = _parse_quote_normalized(raw_clean, item["phone_lines"])
                return {
                    "item_id": item["id"],
                    "raw": raw_text,
                    "status": parsed.get("status"),
                    "label": parsed.get("label") or "MALFORMED",
                    "quote": parsed.get("quote"),
                    "error": parsed.get("error"),
                }
            except Exception as e:
                if not settled:
                    try:
                        ledger.settle(res_id, 0.0, receipt={
                            "actual_model": model_name,
                            "error_code": "provider_error",
                            "cost_usd": 0.0,
                            "cost_status": "calculated_from_usage"
                        })
                    except Exception:
                        pass
                return {
                    "item_id": item["id"],
                    "raw": str(e),
                    "status": "error",
                    "label": "ERROR",
                    "quote": None,
                    "error": str(e),
                }

    tasks = [_eval_one(i, it) for i, it in enumerate(items)]
    results = await asyncio.gather(*tasks)
    return results, total_cost


async def main():
    load_env()
    if not SAMPLE_JSON.exists():
        print(f"Error: {SAMPLE_JSON} missing. Run prepare_bakeoff_sample.py first.")
        return

    items = json.loads(SAMPLE_JSON.read_text(encoding="utf-8"))
    human_labels = {}
    if HUMAN_LABELS_CSV.exists():
        with open(HUMAN_LABELS_CSV, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("human_label"):
                    human_labels[r["item_id"]] = r["human_label"]

    print(f"Loaded {len(items)} test calls. Found {len(human_labels)} human ground truth labels.")

    models_to_test = {}
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    openai_key = os.environ.get("OPENAI_API_KEY")
    deepinfra_key = os.environ.get("DEEPINFRA_API_KEY")

    if anthropic_key:
        models_to_test["Claude Haiku 5.5"] = (
            lambda prompt: call_anthropic("claude-haiku-5-5", prompt, anthropic_key),
            {"input_cost": 0.10, "output_cost": 0.50}
        )
        models_to_test["Claude Sonnet 5.5"] = (
            lambda prompt: call_anthropic("claude-sonnet-5-5", prompt, anthropic_key),
            {"input_cost": 3.00, "output_cost": 15.00}
        )
    if openai_key:
        models_to_test["GPT-4o"] = (
            lambda prompt: call_openai_compat("https://api.openai.com/v1/chat/completions", "gpt-4o", prompt, openai_key),
            {"input_cost": 2.50, "output_cost": 10.00}
        )
        models_to_test["GPT-5 Sol"] = (
            lambda prompt: call_openai_compat("https://api.openai.com/v1/chat/completions", "gpt-6-sol", prompt, openai_key),
            {"input_cost": 1.50, "output_cost": 6.00}
        )
    if deepinfra_key:
        profile = load_judge_profile(GEMINI_PROFILE)
        route = profile["provider_manifest"]["routes"][profile["model_key"]]
        models_to_test["Gemini 3.7 Flash"] = (
            lambda prompt: call_openai_compat(route["endpoint"], route["model_id"], prompt, deepinfra_key),
            {"input_cost": route["input_usd_per_million"], "output_cost": route["output_usd_per_million"]},
        )

    if not models_to_test:
        print("No API keys found in .env! Please add ANTHROPIC_API_KEY, OPENAI_API_KEY, or DEEPINFRA_API_KEY.")
        return

    print(f"Models queued for bake-off: {list(models_to_test.keys())}")
    sem = asyncio.Semaphore(5)  # 5 parallel requests
    model_evaluations = {}
    model_costs = {}

    use_cache = PREDICTIONS_CACHE.exists() and "--no-cache" not in sys.argv
    if use_cache:
        print(f"Loading cached model evaluations from {PREDICTIONS_CACHE} (pass --no-cache to re-run API calls)...")
        cache_data = json.loads(PREDICTIONS_CACHE.read_text(encoding="utf-8"))
        model_evaluations = cache_data.get("evaluations", {})
        model_costs = cache_data.get("costs", {})
    else:
        LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
        with BudgetLedger(LEDGER_FILE, limit_usd="25.00") as ledger:
            print(f"Opened budget ledger at {LEDGER_FILE} with $25.00 limit.")
            for name, (fn, pricing) in models_to_test.items():
                evals, cost = await evaluate_model(name, fn, pricing, items, sem, ledger)
                model_evaluations[name] = evals
                model_costs[name] = cost

            summary = ledger.summary()
            chk = ledger.checkpoint()
            print(f"\nLedger Audit Summary:")
            print(f"  Total Settled Spend: ${summary['settled_usd']:.4f} USD")
            print(f"  Total Reservations: {summary['reservation_count']}")
            print(f"  Total Ledger Events: {chk['event_count']}")
            print(f"  Ledger ID: {chk['ledger_id']}")

        PREDICTIONS_CACHE.write_text(json.dumps({
            "evaluations": model_evaluations,
            "costs": model_costs,
        }, indent=2), encoding="utf-8")

    report_lines = [
        "# Judge Model Bake-Off Report",
        "",
        f"**Date:** Sat Nov 14 2026",
        f"**Sample Size:** {len(items)} calls from the supplied bake-off sample",
        f"**Human Labels Available:** {len(human_labels)}",
        f"**Parser Version:** `quote-normalized-v1` (Smart-quote normalized)",
        f"**Ledger Path:** `{LEDGER_FILE}`",
        "",
        "## Summary Results",
        "",
        "| Model | Valid Labels | Malformed % | Agreement w/ Human | Cohen's Kappa (κ) | Recorded Cost | Est. Cost / 100k calls |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |",
    ]

    print("\n" + "="*80)
    print(" BAKE-OFF RESULTS SUMMARY")
    print("="*80)

    for name, evals in model_evaluations.items():
        valid_count = sum(1 for e in evals if e["status"] == "valid")
        malformed_pct = (len(evals) - valid_count) / len(evals) * 100

        agreed = 0
        y_true, y_pred = [], []
        for e in evals:
            iid = e["item_id"]
            if iid in human_labels:
                y_true.append(human_labels[iid])
                y_pred.append(e["label"])
                if human_labels[iid] == e["label"]:
                    agreed += 1

        agreement_pct = (agreed / len(y_true) * 100) if y_true else 0.0
        kappa = compute_kappa(y_true, y_pred) if y_true else 0.0
        cost_est = (
            "$17" if "Haiku" in name else
            "$350" if "Sonnet" in name else
            "$250" if "GPT-4o" in name else
            "$120" if "Sol" in name or "Luna" in name else
            "Reprice from raw usage" if "Gemini" in name else
            "$20"
        )
        actual_cost = model_costs.get(name, 0.0)

        row = f"| **{name}** | {valid_count}/{len(evals)} | {malformed_pct:.1f}% | {agreement_pct:.1f}% ({agreed}/{len(y_true)}) | **{kappa:.3f}** | ${actual_cost:.4f} | {cost_est} |"
        report_lines.append(row)
        print(f"Model: {name:20s} | Valid: {valid_count}/{len(evals)} | Malformed: {malformed_pct:.1f}% | Kappa: {kappa:.3f} | Agreement: {agreement_pct:.1f}% | Cost: ${actual_cost:.4f}")

    report_lines.extend([
        "",
        "Cached predictions retain the costs recorded when they were generated. Use the original token usage and the current route rates to update estimates.",
        "",
        "## Selection Rule Applied",
        "> **Rule:** The cheapest judge within 0.05 kappa (κ) of the best wins. Haiku wins ties.",
        ""
    ])

    REPORT_MD.write_text("\n".join(report_lines), encoding="utf-8")
    print("\n" + "="*80)
    print(f"Report written to: {REPORT_MD}")
    print("="*80)


if __name__ == "__main__":
    asyncio.run(main())
