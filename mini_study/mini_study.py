#!/usr/bin/env python3
"""Mini study: first-hand check rate P(GO) for a new agent model, without the full 64-cell x 39-seed design.

Three steps, one file, standard library only:

  build    Pick the design and harvest the EXACT first-hand prompts (persona system prompt + scripted source
           announcement + checking prompt) from saved main-study runs. Prompts are model-independent (they differ only
           in the announced artist), so this reproduces the main study's inputs without re-implementing the runner.
           Also stores the DeepSeek and Qwen decisions for the same prompts, for a like-for-like comparison.
  run      Send each prompt to an OpenAI-compatible chat endpoint (OpenAI, DeepInfra, vLLM, ...). Resumable: each
           answer is appended to results.jsonl and fsync'd immediately; reruns skip finished items.
  analyze  P(GO) overall, by reliability x closeness, by cue and by persona, with persona-cluster bootstrap CIs,
           next to the main-study models on the same prompts. Writes report.md and CSVs.

Design (default --design full): a 2^(6-1) half fraction of the six source cues (32 cells, generator: product of the
six +/-1 codes = +1, so every main effect and two-way interaction is estimable), x 3 layouts per cell chosen to cover
as many listener personas as possible, x 6 first-hand seats = 576 decisions. --design min: the 4 reliability x
closeness cells with the other cues at fixed levels, 3 layouts each = 72 decisions.
One twin per town (first-hand decisions happen before any poster, so truth/rumor does not matter); the announced
artist alternates across towns. No repetitions (at T=0 they mostly repeat the same answer).

Examples:
  python3 mini_study.py build --data SHARD0/outputs/main-owner-0 SHARD1/outputs/main-owner-1 --out runs/design_full
  export OPENAI_API_KEY=...
  python3 mini_study.py run --design-dir runs/design_full --model gpt-6.1-terra --out runs/terra --limit 5
  python3 mini_study.py run --design-dir runs/design_full --model gpt-6.1-terra --out runs/terra
  python3 mini_study.py run --design-dir runs/design_full --provider anthropic --model claude-sonnet-5-5 --out runs/sonnet
  python3 mini_study.py analyze --design-dir runs/design_full --results runs/terra
"""
import argparse
import csv
import glob
import json
import math
import os
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

RUN_RE = re.compile(r"(.+)__cell-(\d+)__layout-(\d+)__rep-(\d+)__(.+)$")
KNOBS = [  # (column, +1 level, -1 level)
    ("closeness", "close_friend", "stranger"),
    ("authority", "mayor", "citizen"),
    ("reliability", "good_record", "poor_record"),
    ("wealth", "rich", "poor"),
    ("gender", "woman", "man"),
    ("age", "old", "young"),
]
MIN_FIXED = {"authority": "citizen", "wealth": "poor", "gender": "man", "age": "young"}  # main-study pilot reference levels
FIRST_HAND = range(1, 7)


# ------------------------------------------------------------------------------------------------ build
def _knobs(t):
    k = dict(t["knobs"])
    k["gender"], k["age"] = k["identity"].split("_")
    return {c: k[c] for c, _, _ in KNOBS}


def _code(kn):
    return [1 if kn[c] == a else -1 for c, a, _ in KNOBS]


def cmd_build(a):
    towns = defaultdict(list)  # (cell, layout) -> [run dirs]
    for d in a.data:
        for r in os.listdir(d):
            m = RUN_RE.match(r)
            if m and os.path.isfile(os.path.join(d, r, "town.json")):
                towns[(int(m[2]), int(m[3]))].append(os.path.join(d, r))
    if not towns:
        sys.exit("no run folders found under --data")
    cell_info, layout_seating = {}, {}
    for (cell, layout), runs in sorted(towns.items()):
        t = json.load(open(os.path.join(runs[0], "town.json")))
        cell_info[cell] = _knobs(t)
        layout_seating[(cell, layout)] = {int(k): v for k, v in t["seating_assignment"].items()}
    cells = sorted(cell_info)
    if a.design == "full":
        chosen = [c for c in cells if math.prod(_code(cell_info[c])) == 1]
    else:
        chosen = [c for c in cells if all(cell_info[c][k] == v for k, v in MIN_FIXED.items())]
    print(f"{len(chosen)} cells in the '{a.design}' design (of {len(cells)} available)")

    items, art_toggle = [], 0
    for cell in chosen:
        avail = sorted(l for (c, l) in towns if c == cell)
        picked, covered = [], set()
        for _ in range(min(a.layouts, len(avail))):  # greedy: add the layout that brings the most new first-hand personas
            best = max((l for l in avail if l not in picked),
                       key=lambda l: (len({layout_seating[(cell, l)][s] for s in FIRST_HAND} - covered), -l))
            picked.append(best)
            covered |= {layout_seating[(cell, best)][s] for s in FIRST_HAND}
        for layout in picked:
            runs = towns[(cell, layout)]
            # one prompt set per town; alternate the announced artist across towns to keep it balanced
            by_artist = defaultdict(list)
            for r in runs:
                by_artist[json.load(open(os.path.join(r, "town.json")))["announced_artist"]].append(r)
            artists = sorted(by_artist)
            artist = artists[art_toggle % len(artists)]
            art_toggle += 1
            src = sorted(by_artist[artist])[0]
            t = json.load(open(os.path.join(src, "town.json")))
            hist = json.load(open(os.path.join(src, "agent_histories.json")))
            # baseline decisions from every saved run with the same prompt (same cell, layout, announced artist)
            base = defaultdict(list)
            for r in by_artist[artist]:
                tr = json.load(open(os.path.join(r, "town.json")))
                for x in tr["scene_2_first_hand_decisions"]:
                    base[(tr["model_key"], x["seat_id"])].append(x["decision"])
            for seat in FIRST_HAND:
                h = hist[str(seat)]
                i = next(k for k, m in enumerate(h) if m["role"] == "assistant")
                items.append(dict(
                    item_id=f"c{cell:02d}_l{layout:02d}_s{seat:02d}", cell_id=cell, layout_id=layout, seat=seat,
                    persona_id=layout_seating[(cell, layout)][seat], announced_artist=t["announced_artist"],
                    source_run=os.path.basename(src), **cell_info[cell], messages=h[:i],
                    baseline={m: [v for (mm, s), vs in base.items() if mm == m and s == seat for v in vs]
                              for m in sorted({mm for mm, _ in base})}))
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "design.jsonl"), "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    pers = Counter(it["persona_id"] for it in items)
    meta = dict(design=a.design, cells=chosen, layouts_per_cell=a.layouts, items=len(items), personas=len(pers),
                persona_counts=dict(sorted(pers.items())), artists=dict(Counter(it["announced_artist"] for it in items)),
                data=[os.path.abspath(d) for d in a.data])
    json.dump(meta, open(os.path.join(a.out, "design_meta.json"), "w"), indent=1)
    print(f"{len(items)} prompts -> {a.out}/design.jsonl | personas covered: {len(pers)} | artists: {meta['artists']}")


# ------------------------------------------------------------------------------------------------ run
def parse_decision(text):
    """Same rule as the main-study runner (truth_discount.runner.parse_check_decision), plus an ambiguity flag."""
    up = (text or "").strip().upper()
    m = re.search(r"\b(GO|SKIP)\b", up)
    both = bool(re.search(r"\bGO\b", up)) and bool(re.search(r"\bSKIP\b", up))
    return (m.group(1) if m else "SKIP"), ("valid" if m else "malformed_fallback_skip"), both


def _post(url, body, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers)
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r), None
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:400]
            if e.code in (408, 409, 429, 500, 502, 503, 504, 529) and attempt < 5:
                time.sleep(min(60, 2 ** attempt * 2))
                continue
            return None, f"HTTP {e.code}: {msg}"
        except Exception as e:  # network errors, timeouts
            if attempt < 5:
                time.sleep(min(30, 2 ** attempt))
                continue
            return None, repr(e)


def call_anthropic(a, key, messages):
    """Anthropic Messages API. Returns an OpenAI-shaped response so the rest of the code is shared."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    body = {"model": a.model, "max_tokens": a.max_tokens or 2000,
            "messages": [m for m in messages if m["role"] != "system"]}
    if system:
        body["system"] = system
    if a.temperature is not None:
        body["temperature"] = a.temperature
    if a.thinking:
        body["thinking"] = {"type": "adaptive"}
        if a.reasoning_effort:
            body["output_config"] = {"effort": a.reasoning_effort}
    base = (a.base_url if a.base_url != "https://api.openai.com/v1" else os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")).rstrip("/")
    resp, err = _post(base + "/v1/messages", body, {"x-api-key": key, "anthropic-version": "2023-06-01",
                                                     "content-type": "application/json"}, a.timeout)
    if err:
        return None, err
    text = "".join(b.get("text", "") for b in resp.get("content", []) if b.get("type") == "text")
    u = resp.get("usage") or {}
    return {"choices": [{"message": {"content": text}, "finish_reason": resp.get("stop_reason")}],
            "usage": {"prompt_tokens": (u.get("input_tokens") or 0) + (u.get("cache_read_input_tokens") or 0) + (u.get("cache_creation_input_tokens") or 0),
                      "completion_tokens": u.get("output_tokens"),
                      "prompt_tokens_details": {"cached_tokens": u.get("cache_read_input_tokens")}}}, None


def call_chat(a, key, messages):
    if a.provider == "anthropic":
        return call_anthropic(a, key, messages)
    body = {"model": a.model, "messages": messages}
    if a.max_tokens:
        body[a.max_tokens_field] = a.max_tokens
    if a.temperature is not None:
        body["temperature"] = a.temperature
    if a.reasoning_effort:
        body["reasoning_effort"] = a.reasoning_effort
    return _post(a.base_url.rstrip("/") + "/chat/completions", body,
                 {"Authorization": "Bearer " + key, "Content-Type": "application/json"}, a.timeout)


def _done(path):
    out = {}
    if os.path.exists(path):
        for line in open(path):
            try:
                r = json.loads(line)
                out[r["item_id"]] = r
            except Exception:
                pass  # torn last line from a crash
    return out


def cmd_run(a):
    env = a.api_key_env or ("ANTHROPIC_API_KEY" if a.provider == "anthropic" else "OPENAI_API_KEY")
    key = os.environ.get(env) or sys.exit(f"${env} is not set")
    items = [json.loads(l) for l in open(os.path.join(a.design_dir, "design.jsonl"))]
    random.Random(13).shuffle(items)  # partial runs stay balanced
    os.makedirs(a.out, exist_ok=True)
    res_path, err_path = os.path.join(a.out, "results.jsonl"), os.path.join(a.out, "errors.jsonl")
    done = _done(res_path)
    todo = [it for it in items if it["item_id"] not in done][: a.limit or None]
    print(f"{len(items)} items | {len(done)} done | {len(todo)} to run with {a.model}")
    if not todo:
        return
    json.dump({k: v for k, v in vars(a).items()}, open(os.path.join(a.out, "run_args.json"), "w"), indent=1)
    for p in (res_path, err_path):  # end a torn line before appending
        if os.path.exists(p) and os.path.getsize(p) and open(p, "rb").read()[-1:] != b"\n":
            open(p, "ab").write(b"\n")
    lock, stats = threading.Lock(), Counter()
    rf, ef = open(res_path, "a"), open(err_path, "a")

    def one(it):
        resp, err = call_chat(a, key, it["messages"])
        text, usage, finish = None, {}, None
        if resp:
            try:
                ch = resp["choices"][0]
                text, finish, usage = ch["message"].get("content") or "", ch.get("finish_reason"), resp.get("usage") or {}
            except Exception as e:
                err = f"bad response: {e!r}"
        with lock:
            if err:
                ef.write(json.dumps(dict(item_id=it["item_id"], error=err, ts=time.time())) + "\n"); ef.flush()
                stats["err"] += 1
                return
            dec, status, both = parse_decision(text)
            det = usage.get("completion_tokens_details") or {}
            rec = dict(item_id=it["item_id"], decision=dec, parse_status=status, ambiguous_both_words=both,
                       raw_response=text, finish_reason=finish, model=a.model,
                       prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"),
                       reasoning_tokens=det.get("reasoning_tokens"), cached_tokens=(usage.get("prompt_tokens_details") or {}).get("cached_tokens"),
                       ts=time.time())
            rf.write(json.dumps(rec) + "\n"); rf.flush(); os.fsync(rf.fileno())
            stats[dec] += 1
            stats["malformed"] += status != "valid"
            n = stats["GO"] + stats["SKIP"]
            if n % 50 == 0:
                print(f"  {n}/{len(todo)}  GO {stats['GO']}  SKIP {stats['SKIP']}  malformed {stats['malformed']}  errors {stats['err']}", flush=True)

    try:
        with ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(one, todo))
    except KeyboardInterrupt:
        print("interrupted; finished answers are saved, rerun to resume")
    finally:
        rf.close(); ef.close()
    print(f"done: GO {stats['GO']}  SKIP {stats['SKIP']}  malformed {stats['malformed']}  errors {stats['err']} -> {res_path}")
    if stats["err"]:
        print("some calls failed (see errors.jsonl); rerun the same command to retry them")


# ------------------------------------------------------------------------------------------------ analyze
def _boot(groups, B=2000, seed=0):
    """Cluster bootstrap over groups (lists of 0/1); returns (rate, lo, hi)."""
    groups = [g for g in groups if g]
    n = sum(len(g) for g in groups)
    if not n:
        return float("nan"), float("nan"), float("nan")
    p = sum(sum(g) for g in groups) / n
    rng, sims = random.Random(seed), []
    for _ in range(B):
        s = [groups[rng.randrange(len(groups))] for _ in groups]
        m = sum(len(g) for g in s)
        sims.append(sum(sum(g) for g in s) / m)
    sims.sort()
    return p, sims[int(0.025 * B)], sims[int(0.975 * B) - 1]


def _rate(rows, key, B):
    by = defaultdict(list)
    for r in rows:
        by[r["persona_id"]].append(r[key])
    return _boot(list(by.values()), B)


def _diff(rows, key, sel, B, seed=0):
    by = defaultdict(lambda: ([], []))
    for r in rows:
        by[r["persona_id"]][0 if sel(r) else 1].append(r[key])
    groups = list(by.values())
    def stat(gs):
        a = [v for g in gs for v in g[0]]; b = [v for g in gs for v in g[1]]
        return (sum(a) / len(a) - sum(b) / len(b)) if a and b else float("nan")
    est = stat(groups)
    rng, sims = random.Random(seed), []
    for _ in range(B):
        v = stat([groups[rng.randrange(len(groups))] for _ in groups])
        if v == v:
            sims.append(v)
    sims.sort()
    return est, (sims[int(0.025 * len(sims))] if sims else float("nan")), (sims[int(0.975 * len(sims)) - 1] if sims else float("nan"))


def pct(x):
    return "n/a" if x != x else f"{100 * x:.1f}%"


def cmd_analyze(a):
    items = {json.loads(l)["item_id"]: json.loads(l) for l in open(os.path.join(a.design_dir, "design.jsonl"))}
    res = _done(os.path.join(a.results, "results.jsonl"))
    name = a.name or next(iter(res.values()), {}).get("model", "new model")
    rows = []
    for iid, it in items.items():
        r = dict({k: it[k] for k in ("item_id", "cell_id", "layout_id", "seat", "persona_id", "announced_artist")},
                 **{c: it[c] for c, _, _ in KNOBS})
        if iid in res:
            r["new"] = int(res[iid]["decision"] == "GO")
            r["new_malformed"] = int(res[iid]["parse_status"] != "valid")
        for m, decs in it["baseline"].items():
            if decs:
                r[m] = sum(d == "GO" for d in decs) / len(decs)  # share of saved runs that went
        rows.append(r)
    have = [r for r in rows if "new" in r]
    if not have:
        sys.exit("no results yet")
    models = [("new", name)] + [(m, m) for m in sorted({k for it in items.values() for k in it["baseline"]})]
    B = a.boot
    L = [f"# Mini study: first-hand check rate\n",
         f"Model under test: **{name}**. Answered {len(have)} of {len(rows)} prompts; "
         f"malformed (counted as SKIP, as in the main study): {sum(r['new_malformed'] for r in have)}.\n",
         "Main-study models are shown on the same prompts (share of their saved runs that chose GO). "
         "95% CIs are bootstrap over listener personas.\n"]

    def table(title, groups):
        out = [f"\n## {title}\n", "| group | n | " + " | ".join(n for _, n in models) + " |", "|---|---|" + "---|" * len(models)]
        csv_rows = []
        for gname, sel in groups:
            sub = [r for r in have if sel(r)]
            cells = []
            for key, mname in models:
                s = [r for r in sub if key in r]
                p, lo, hi = _rate(s, key, B)
                cells.append(f"{pct(p)} [{pct(lo)}, {pct(hi)}]")
                csv_rows.append(dict(table=title, group=gname, model=mname, n=len(s), go_rate=p, lo=lo, hi=hi))
            out.append(f"| {gname} | {len(sub)} | " + " | ".join(cells) + " |")
        return out, csv_rows

    all_csv = []
    o, c = table("Overall P(GO)", [("all", lambda r: True)]); L += o; all_csv += c
    grid = [(f"{rel.split('_')[0]} record, {clo.replace('_', ' ')}", (lambda rel, clo: lambda r: r["reliability"] == rel and r["closeness"] == clo)(rel, clo))
            for rel in ("good_record", "poor_record") for clo in ("close_friend", "stranger")]
    o, c = table("P(GO) by reliability x closeness", grid); L += o; all_csv += c

    L += ["\n## Cue effects (P(GO) difference, first level minus second)\n",
          "| cue | " + " | ".join(n for _, n in models) + " |", "|---|" + "---|" * len(models)]
    for col, hi_, lo_ in KNOBS:
        cells = []
        for key, mname in models:
            s = [r for r in have if key in r]
            d, l, h = _diff(s, key, lambda r, col=col, hi_=hi_: r[col] == hi_, B)
            cells.append(f"{d * 100:+.1f} pp [{l * 100:+.1f}, {h * 100:+.1f}]" if d == d else "n/a")
            all_csv.append(dict(table="cue effects", group=f"{col}: {hi_} - {lo_}", model=mname, n=len(s), go_rate=d, lo=l, hi=h))
        L.append(f"| {col}: {hi_} vs {lo_} | " + " | ".join(cells) + " |")
    inter = []
    for key, mname in models:
        s = [r for r in have if key in r]
        def g(rel, clo):
            v = [r[key] for r in s if r["reliability"] == rel and r["closeness"] == clo]
            return sum(v) / len(v) if v else float("nan")
        poor = g("poor_record", "close_friend") - g("poor_record", "stranger")
        good = g("good_record", "close_friend") - g("good_record", "stranger")
        inter.append(f"{mname}: closeness effect {poor * 100:+.1f} pp with a poor record vs {good * 100:+.1f} pp with a good record")
    L += ["\nCloseness x reliability (point estimates): " + "; ".join(inter) + "\n"]

    pers = sorted({r["persona_id"] for r in have})
    o, c = table("P(GO) by listener persona", [(f"persona {p}", (lambda p: lambda r: r["persona_id"] == p)(p)) for p in pers])
    L += o; all_csv += c

    res_rows = list(res.values())
    toks = [r.get("completion_tokens") or 0 for r in res_rows]
    rtoks = [r.get("reasoning_tokens") or 0 for r in res_rows]
    ptoks = [r.get("prompt_tokens") or 0 for r in res_rows]
    L += ["\n## Run diagnostics\n",
          f"- Answers: {len(res_rows)}; finish reasons: {dict(Counter(r.get('finish_reason') for r in res_rows))}",
          f"- Malformed (no GO/SKIP found): {sum(r['parse_status'] != 'valid' for r in res_rows)}; answers containing both GO and SKIP: {sum(bool(r.get('ambiguous_both_words')) for r in res_rows)}",
          f"- Tokens: prompt {sum(ptoks):,}, completion {sum(toks):,} (of which reasoning {sum(rtoks):,})",
          f"- Example raw answers: {[r['raw_response'][:60] for r in res_rows[:5]]}"]
    if a.price_in is not None and a.price_out is not None:
        cost = sum(ptoks) / 1e6 * a.price_in + sum(toks) / 1e6 * a.price_out
        L.append(f"- Estimated cost at ${a.price_in}/M input, ${a.price_out}/M output: ${cost:.2f}")
    L += ["\n## Caveats\n",
          "- Main-study models answered at T=0 with a 5-token cap. If the new model ran with other settings (reasoning, higher cap), say so when comparing.",
          "- The design covers 32 (or 4) of 64 cells and 3 layouts per cell, one twin, no repetitions. Main-study numbers above are restricted to the same prompts, not the full study.",
          "- Second-hand checking and belief (truth discount) are not measured here."]
    out = os.path.join(a.results, "report.md")
    open(out, "w").write("\n".join(L) + "\n")
    with open(os.path.join(a.results, "summary.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["table", "group", "model", "n", "go_rate", "lo", "hi"]); w.writeheader(); w.writerows(all_csv)
    with open(os.path.join(a.results, "decisions.csv"), "w", newline="") as f:
        keys = sorted({k for r in rows for k in r})
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    print("\n".join(L[:14]))
    print(f"\n-> {out}, summary.csv, decisions.csv")


# ------------------------------------------------------------------------------------------------ price variants
FARE_SENTENCE = "a short bus ride that costs $5, about the price of a donut and a coffee."
FARE_QUESTION = "You can take the $5 bus across town"
PRICE_TEXT = {  # price -> (system sentence, question phrase); everyday comparisons kept neutral
    0: ("a short bus ride that is free.", "You can take the free bus across town"),
    1: ("a short bus ride that costs $1, about the price of a pack of gum.", "You can take the $1 bus across town"),
    5: (FARE_SENTENCE, FARE_QUESTION),
    15: ("a short bus ride that costs $15, about the price of a sit-down lunch.", "You can take the $15 bus across town"),
    35: ("a short bus ride that costs $35, about the price of a nice dinner out.", "You can take the $35 bus across town"),
}


def cmd_price(a):
    """Copy a design with the bus fare changed. Fails loudly unless every prompt has exactly one of each fare phrase."""
    if a.price not in PRICE_TEXT:
        sys.exit(f"--price must be one of {sorted(PRICE_TEXT)}")
    sent, ques = PRICE_TEXT[a.price]
    items = [json.loads(l) for l in open(os.path.join(a.design_dir, "design.jsonl"))]
    for it in items:
        n_s = sum(m["content"].count(FARE_SENTENCE) for m in it["messages"])
        n_q = sum(m["content"].count(FARE_QUESTION) for m in it["messages"])
        if (n_s, n_q) != (1, 1):
            sys.exit(f"{it['item_id']}: expected one fare sentence and one fare question, found {n_s} and {n_q}")
        for m in it["messages"]:
            m["content"] = m["content"].replace(FARE_SENTENCE, sent).replace(FARE_QUESTION, ques)
        it["price"] = a.price
        it["baseline"] = it["baseline"] if a.price == 5 else {}  # main-study answers only exist at $5
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "design.jsonl"), "w") as f:
        for it in items:
            f.write(json.dumps(it) + "\n")
    meta = json.load(open(os.path.join(a.design_dir, "design_meta.json")))
    meta.update(price=a.price, derived_from=os.path.abspath(a.design_dir))
    json.dump(meta, open(os.path.join(a.out, "design_meta.json"), "w"), indent=1)
    print(f"{len(items)} prompts at price ${a.price} -> {a.out}/design.jsonl")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="choose the design and harvest prompts from saved runs")
    b.add_argument("--data", nargs="+", required=True, help="folders holding main-study run directories")
    b.add_argument("--out", required=True)
    b.add_argument("--design", choices=["full", "min"], default="full", help="full = 32-cell half fraction; min = 4 reliability x closeness cells")
    b.add_argument("--layouts", type=int, default=3, help="layouts per cell")
    r = sub.add_parser("run", help="query the new model")
    r.add_argument("--design-dir", required=True)
    r.add_argument("--model", required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--base-url", default="https://api.openai.com/v1", help="any OpenAI-compatible endpoint (DeepInfra, vLLM, ...)")
    r.add_argument("--provider", choices=["openai", "anthropic"], default="openai",
                   help="openai = any OpenAI-compatible chat endpoint; anthropic = Anthropic Messages API (uses $ANTHROPIC_BASE_URL if set)")
    r.add_argument("--api-key-env", default=None, help="default OPENAI_API_KEY or ANTHROPIC_API_KEY by provider")
    r.add_argument("--thinking", action="store_true", help="anthropic only: enable adaptive extended thinking")
    r.add_argument("--max-tokens", type=int, default=2000, help="main study used 5; reasoning models need room to think")
    r.add_argument("--max-tokens-field", default="max_completion_tokens", help="use max_tokens for older/compatible servers")
    r.add_argument("--temperature", type=float, default=None, help="main study used 0.0; omit for models that reject it")
    r.add_argument("--reasoning-effort", default=None, help="e.g. low / medium / high, for reasoning models")
    r.add_argument("--workers", type=int, default=8)
    r.add_argument("--timeout", type=int, default=120)
    r.add_argument("--limit", type=int, default=0, help="run at most N new items (smoke test)")
    v = sub.add_parser("price", help="copy a design with a different bus fare")
    v.add_argument("--design-dir", required=True)
    v.add_argument("--price", type=int, required=True, help="0, 1, 5, 15 or 35")
    v.add_argument("--out", required=True)
    z = sub.add_parser("analyze", help="summarize results")
    z.add_argument("--design-dir", required=True)
    z.add_argument("--results", required=True)
    z.add_argument("--name", default=None, help="display name for the new model")
    z.add_argument("--boot", type=int, default=2000)
    z.add_argument("--price-in", type=float, default=None, help="$ per million input tokens, for a cost line")
    z.add_argument("--price-out", type=float, default=None)
    a = ap.parse_args()
    {"build": cmd_build, "run": cmd_run, "analyze": cmd_analyze, "price": cmd_price}[a.cmd](a)


if __name__ == "__main__":
    main()
