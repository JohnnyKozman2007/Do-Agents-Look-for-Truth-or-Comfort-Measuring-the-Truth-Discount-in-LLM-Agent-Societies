"""Build the Second-Hand 2x2 (Own GO/SKIP x Partner GO/SKIP) report.

Reads results/main-gemini-3.7-flash/listeners.csv, pairs each second-hand
listener (Seats 7-12) with their first-hand partner (Seats 1-6, seat_id + 6),
preserves INVALID judgments as NaN, and outputs:
  - reports/second_hand_2x2/report.md
  - reports/second_hand_2x2/report.html
  - reports/second_hand_2x2/csv/second_hand_2x2_cells.csv
  - reports/second_hand_2x2/csv/second_hand_2x2_factorial_tests.csv
"""
from __future__ import annotations

import argparse
import html
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RESULTS = ROOT / "results" / "main-gemini-3.7-flash"
DEFAULT_OUT = ROOT / "reports" / "second_hand_2x2"

LABELS = ("FACT", "UNCERTAIN", "SKEPTICAL", "CHECKED_TRUE", "CHECKED_FALSE", "NOT_MENTIONED")
MODEL_SCOPES = (
    ("pooled", "Both Models Combined", None),
    ("deepseek_v4_flash", "DeepSeek-V4-Flash", "deepseek_v4_flash"),
    ("qwen_3_8_flash", "Qwen3.8-Flash", "qwen_3_8_flash"),
)
CELL_DEFS = (
    (1, 1, "both_checked", "Both Checked", "Own GO, Partner GO"),
    (1, 0, "sh_only", "SH Only", "Own GO, Partner SKIP"),
    (0, 1, "partner_only", "Partner Only", "Own SKIP, Partner GO"),
    (0, 0, "neither_checked", "Neither Checked", "Own SKIP, Partner SKIP"),
)


def prepare_second_hand_2x2(listeners: pd.DataFrame) -> pd.DataFrame:
    """Attach partner decision (Seat i <-> Seat i+6) and clean outcome columns."""
    df = listeners.copy()
    is_valid = df["judgment_status"] == "valid"
    is_not_mentioned = is_valid & (df["label"] == "NOT_MENTIONED")

    df["is_valid"] = is_valid
    df["belief_clean"] = np.where(is_valid & (df["mentioned"] == 1), df["belief"].astype(float), np.nan)
    df["belief_sil0"] = np.where(is_not_mentioned, 0.0, df["belief_clean"])
    df["belief_sil05"] = np.where(is_not_mentioned, 0.5, df["belief_clean"])
    for lbl in LABELS:
        df[f"lbl_{lbl}"] = np.where(is_valid, (df["label"] == lbl).astype(float), np.nan)

    fh = df[df["layer"] == "first_hand"][["run_id", "seat_id", "decision"]].rename(
        columns={"seat_id": "fh_seat_id", "decision": "partner_decision"}
    )
    fh["sh_seat_id"] = fh["fh_seat_id"] + 6

    sh = df[df["layer"] == "second_hand"].merge(
        fh[["run_id", "sh_seat_id", "partner_decision"]],
        left_on=["run_id", "seat_id"],
        right_on=["run_id", "sh_seat_id"],
        how="inner",
    )
    sh["own_go"] = (sh["decision"] == "GO").astype(int)
    sh["partner_go"] = (sh["partner_decision"] == "GO").astype(int)
    sh["truth"] = (sh["condition_type"] == "truth_twin").astype(int)
    sh["cluster_pair"] = sh["model_key"].astype(str) + "__" + sh["pair_id"].astype(str)
    return sh


def _clustered_truth_diff(sub: pd.DataFrame, col: str) -> tuple[float, float, float, float, int]:
    s = sub.dropna(subset=[col])
    if len(s) == 0 or s["truth"].nunique() < 2:
        return float("nan"), float("nan"), float("nan"), float("nan"), 0
    mod = smf.ols(f"{col} ~ truth", data=s).fit(
        cov_type="cluster", cov_kwds={"groups": s["cluster_pair"]}
    )
    est = float(mod.params["truth"])
    se = float(mod.bse["truth"])
    p = float(mod.pvalues["truth"])
    return est, est - 1.96 * se, est + 1.96 * se, p, int(s["cluster_pair"].nunique())


def compute_cells_table(sh: pd.DataFrame) -> pd.DataFrame:
    """Compute the 4-row 2x2 summary table for Pooled, DeepSeek, and Qwen."""
    rows: list[dict] = []
    for scope_key, scope_label, model_key in MODEL_SCOPES:
        sub_m = sh if model_key is None else sh[sh["model_key"] == model_key]
        total_r = max(int((sub_m["truth"] == 0).sum()), 1)
        total_t = max(int((sub_m["truth"] == 1).sum()), 1)
        for og, pg, cell_key, cell_label, cell_detail in CELL_DEFS:
            c = sub_m[(sub_m["own_go"] == og) & (sub_m["partner_go"] == pg)]
            r = c[c["truth"] == 0]
            t = c[c["truth"] == 1]
            td, td_lo, td_hi, td_p, n_pairs = _clustered_truth_diff(c, "belief_clean")
            td_s0, _, _, _, _ = _clustered_truth_diff(c, "belief_sil0")
            td_s05, _, _, _, _ = _clustered_truth_diff(c, "belief_sil05")
            rows.append({
                "scope_key": scope_key,
                "scope_label": scope_label,
                "cell_key": cell_key,
                "cell_label": cell_label,
                "cell_detail": cell_detail,
                "own_go": og,
                "partner_go": pg,
                "n_rumor": int(len(r)),
                "share_rumor_pct": len(r) / total_r * 100.0,
                "n_truth": int(len(t)),
                "share_truth_pct": len(t) / total_t * 100.0,
                "n_pairs": n_pairs,
                "rumor_belief": float(r["belief_clean"].mean()),
                "truth_belief": float(t["belief_clean"].mean()),
                "td": td,
                "td_ci_lo": td_lo,
                "td_ci_hi": td_hi,
                "td_p": td_p,
                "td_sil0": td_s0,
                "td_sil05": td_s05,
                "rumor_fact_pct": float(r["lbl_FACT"].mean() * 100.0),
                "truth_fact_pct": float(t["lbl_FACT"].mean() * 100.0),
                "rumor_uncertain_pct": float(r["lbl_UNCERTAIN"].mean() * 100.0),
                "truth_uncertain_pct": float(t["lbl_UNCERTAIN"].mean() * 100.0),
                "rumor_skeptical_pct": float(r["lbl_SKEPTICAL"].mean() * 100.0),
                "truth_skeptical_pct": float(t["lbl_SKEPTICAL"].mean() * 100.0),
                "rumor_checked_false_pct": float(r["lbl_CHECKED_FALSE"].mean() * 100.0),
                "truth_checked_true_pct": float(t["lbl_CHECKED_TRUE"].mean() * 100.0),
                "rumor_not_mentioned_pct": float(r["lbl_NOT_MENTIONED"].mean() * 100.0),
                "truth_not_mentioned_pct": float(t["lbl_NOT_MENTIONED"].mean() * 100.0),
            })
    return pd.DataFrame(rows)


def compute_factorial_tests(sh: pd.DataFrame) -> pd.DataFrame:
    """Fit 2x2 factorial OLS (outcome ~ truth * own_go * partner_go), pair-clustered."""
    outcomes = (
        ("belief", "Belief Score (0-1)", "belief_clean", 1.0),
        ("FACT_pct", "FACT (%)", "lbl_FACT", 100.0),
        ("SKEPTICAL_pct", "SKEPTICAL (%)", "lbl_SKEPTICAL", 100.0),
        ("UNCERTAIN_pct", "UNCERTAIN (%)", "lbl_UNCERTAIN", 100.0),
    )
    terms = (
        ("own_go", "Own GO (Rumor baseline)"),
        ("partner_go", "Partner GO (Rumor baseline)"),
        ("own_go:partner_go", "Own GO x Partner GO (Rumor baseline)"),
        ("truth:own_go", "Own GO effect on Truth Discount"),
        ("truth:partner_go", "Partner GO effect on Truth Discount"),
        ("truth:own_go:partner_go", "Own GO x Partner GO interaction on Truth Discount"),
    )
    rows: list[dict] = []
    for scope_key, scope_label, model_key in MODEL_SCOPES:
        sub_m = sh if model_key is None else sh[sh["model_key"] == model_key]
        for out_key, out_label, col, scale in outcomes:
            s = sub_m.dropna(subset=[col]).copy()
            s["y"] = s[col].astype(float) * scale
            mod = smf.ols("y ~ truth * own_go * partner_go", data=s).fit(
                cov_type="cluster", cov_kwds={"groups": s["cluster_pair"]}
            )
            n_obs = int(len(s))
            n_pairs = int(s["cluster_pair"].nunique())
            for term, term_label in terms:
                est = float(mod.params[term])
                se = float(mod.bse[term])
                p = float(mod.pvalues[term])
                rows.append({
                    "scope_key": scope_key,
                    "scope_label": scope_label,
                    "outcome_key": out_key,
                    "outcome_label": out_label,
                    "term": term,
                    "term_label": term_label,
                    "estimate": est,
                    "se": se,
                    "ci_lo": est - 1.96 * se,
                    "ci_hi": est + 1.96 * se,
                    "p": p,
                    "n_obs": n_obs,
                    "n_pairs": n_pairs,
                })
    return pd.DataFrame(rows)


def _fmt_p(p: float) -> str:
    if np.isnan(p):
        return "—"
    if p < 0.0001:
        return "<0.0001"
    return f"{p:.4f}"


def render_markdown(cells_df: pd.DataFrame, tests_df: pd.DataFrame) -> str:
    lines = [
        "# Second-Hand 2×2 Report (`Own GO/SKIP × Partner GO/SKIP`)",
        "",
        "**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Layer:** Second-Hand (Seats 7–12 paired with First-Hand Seats 1–6) | **Clustering:** Twin Pair (`pair_id`)",
        "",
        "### Methodological & Interpretation Note",
        "- **4-Cell Routing:** Every second-hand listener is cross-classified by their own verification decision (`Own GO` vs `Own SKIP`) and their paired first-hand partner's decision (`Partner GO` vs `Partner SKIP`, Seat `i` ↔ Seat `i+6`).",
        "- **Missingness:** `judgment_status = invalid` rows stay `NaN` (never zero-imputed). `Belief` is over valid mentioning listeners; label `%` is over valid listeners.",
        "- **Causal vs. Descriptive Distinction:** `Neither Checked` directly tests zero twin-to-twin leakage. However, `Own GO` and `Partner GO` are endogenous behavioral choices rather than randomized treatments, so cell shares and the small `Both Checked` vs. `SH Only` difference reflect selection/routing as well as direct checking.",
        "",
        "---",
        "",
        "## 1. 2×2 Second-Hand Summary Tables",
        "",
    ]

    for scope_key, scope_label, _ in MODEL_SCOPES:
        sub = cells_df[cells_df["scope_key"] == scope_key]
        lines.extend([
            f"### {scope_label}",
            "",
            "| 2×2 Cell | R N (Share) | T N (Share) | Rumor Belief | Truth Belief | Truth Discount [95% CI] | p | Sil=0.0 TD | Sil=0.5 TD | R FACT % | T FACT % | R SKEP % | T SKEP % | R NM % | T NM % |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ])
        for _, r in sub.iterrows():
            lines.append(
                f"| **{r['cell_label']}** ({r['cell_detail']}) | "
                f"{int(r['n_rumor']):,} ({r['share_rumor_pct']:.1f}%) | "
                f"{int(r['n_truth']):,} ({r['share_truth_pct']:.1f}%) | "
                f"{r['rumor_belief']:.3f} | {r['truth_belief']:.3f} | "
                f"**{r['td']:+.3f}** [{r['td_ci_lo']:+.3f}, {r['td_ci_hi']:+.3f}] | "
                f"{_fmt_p(r['td_p'])} | {r['td_sil0']:+.3f} | {r['td_sil05']:+.3f} | "
                f"{r['rumor_fact_pct']:.2f}% | {r['truth_fact_pct']:.1f}% | "
                f"{r['rumor_skeptical_pct']:.1f}% | {r['truth_skeptical_pct']:.1f}% | "
                f"{r['rumor_not_mentioned_pct']:.2f}% | {r['truth_not_mentioned_pct']:.2f}% |"
            )
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 2. 2×2 Factorial Interaction Tests (`outcome ~ truth * own_go * partner_go`, Pair-Clustered)",
        "",
    ])
    for scope_key, scope_label, _ in MODEL_SCOPES:
        sub_t = tests_df[tests_df["scope_key"] == scope_key]
        lines.extend([
            f"### {scope_label}",
            "",
            "| Outcome | Term | Meaning | Estimate | SE | 95% CI | p (clustered) |",
            "|---|---|---|---:|---:|---:|---:|",
        ])
        for _, r in sub_t.iterrows():
            lines.append(
                f"| {r['outcome_label']} | `{r['term']}` | {r['term_label']} | "
                f"{r['estimate']:+.4f} | {r['se']:.4f} | [{r['ci_lo']:+.4f}, {r['ci_hi']:+.4f}] | {_fmt_p(r['p'])} |"
            )
        lines.append("")

    return "\n".join(lines)


def render_html(cells_df: pd.DataFrame, tests_df: pd.DataFrame) -> str:
    pooled = cells_df[cells_df["scope_key"] == "pooled"].set_index("cell_key")
    kpis = [
        ("Neither Checked TD", f"{pooled.loc['neither_checked', 'td']:+.3f}"),
        ("Partner Only TD", f"{pooled.loc['partner_only', 'td']:+.3f}"),
        ("SH Only TD", f"{pooled.loc['sh_only', 'td']:+.3f}"),
        ("Both Checked TD", f"{pooled.loc['both_checked', 'td']:+.3f}"),
    ]
    kpi_html = "".join(
        f'<div class="kpi"><b>{html.escape(v)}</b><span>{html.escape(k)}</span></div>'
        for k, v in kpis
    )

    sections = []
    for scope_key, scope_label, _ in MODEL_SCOPES:
        sub = cells_df[cells_df["scope_key"] == scope_key]
        rows_html = "".join(
            "<tr>"
            f"<td><b>{html.escape(r['cell_label'])}</b><br><small>{html.escape(r['cell_detail'])}</small></td>"
            f"<td>{int(r['n_rumor']):,} ({r['share_rumor_pct']:.1f}%)</td>"
            f"<td>{int(r['n_truth']):,} ({r['share_truth_pct']:.1f}%)</td>"
            f"<td>{r['rumor_belief']:.3f}</td>"
            f"<td>{r['truth_belief']:.3f}</td>"
            f"<td><b>{r['td']:+.3f}</b> [{r['td_ci_lo']:+.3f}, {r['td_ci_hi']:+.3f}]</td>"
            f"<td>{_fmt_p(r['td_p'])}</td>"
            f"<td>{r['rumor_fact_pct']:.2f}% / {r['truth_fact_pct']:.1f}%</td>"
            f"<td>{r['rumor_skeptical_pct']:.1f}% / {r['truth_skeptical_pct']:.1f}%</td>"
            f"<td>{r['rumor_not_mentioned_pct']:.2f}% / {r['truth_not_mentioned_pct']:.2f}%</td>"
            "</tr>"
            for _, r in sub.iterrows()
        )
        sub_t = tests_df[(tests_df["scope_key"] == scope_key) & (tests_df["term"] == "truth:own_go:partner_go")]
        t_rows = "".join(
            "<tr>"
            f"<td>{html.escape(r['outcome_label'])}</td>"
            f"<td><code>{html.escape(r['term'])}</code></td>"
            f"<td>{r['estimate']:+.4f}</td>"
            f"<td>{r['se']:.4f}</td>"
            f"<td>[{r['ci_lo']:+.4f}, {r['ci_hi']:+.4f}]</td>"
            f"<td>{_fmt_p(r['p'])}</td>"
            "</tr>"
            for _, r in sub_t.iterrows()
        )
        sections.append(
            f"<h2>{html.escape(scope_label)}</h2>"
            "<table><thead><tr>"
            "<th>2×2 Cell</th><th>R N (%)</th><th>T N (%)</th><th>R Belief</th><th>T Belief</th>"
            "<th>Truth Discount [95% CI]</th><th>p</th><th>R / T FACT %</th><th>R / T SKEP %</th><th>R / T NM %</th>"
            f"</tr></thead><tbody>{rows_html}</tbody></table>"
            "<h3>2×2 Interaction (`truth × own_go × partner_go`, Pair-Clustered)</h3>"
            "<table><thead><tr><th>Outcome</th><th>Term</th><th>Estimate</th><th>SE</th><th>95% CI</th><th>p</th></tr></thead>"
            f"<tbody>{t_rows}</tbody></table>"
        )

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Second-Hand 2×2 Report</title>
<style>
body{{font-family:system-ui,-apple-system,sans-serif;margin:2rem auto;max-width:1200px;padding:0 1rem;color:#1a1a1a;line-height:1.5}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin:1.5rem 0}}
.kpi{{background:#f5f7fa;border:1px solid #e1e6ed;border-radius:8px;padding:1rem}}
.kpi b{{display:block;font-size:1.4rem}}
table{{width:100%;border-collapse:collapse;margin:1rem 0 2rem;font-size:.9rem}}
th,td{{border:1px solid #dde2e8;padding:.45rem .6rem;text-align:left}}
th{{background:#f2f5f9}}
</style></head><body>
<h1>Second-Hand 2×2 Report (Own GO/SKIP × Partner GO/SKIP)</h1>
<p><b>Judge:</b> Gemini 3.7 Flash | <b>Layer:</b> Second-Hand (Seats 7–12 paired with First-Hand Seats 1–6) | <b>Clustering:</b> Twin Pair (<code>pair_id</code>)</p>
<div class="kpis">{kpi_html}</div>
{''.join(sections)}
</body></html>"""


def build_report(results_dir: Path, out_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    listeners = pd.read_csv(results_dir / "listeners.csv")
    sh = prepare_second_hand_2x2(listeners)
    cells_df = compute_cells_table(sh)
    tests_df = compute_factorial_tests(sh)

    out_dir.mkdir(parents=True, exist_ok=True)
    csv_dir = out_dir / "csv"
    csv_dir.mkdir(parents=True, exist_ok=True)

    cells_df.to_csv(csv_dir / "second_hand_2x2_cells.csv", index=False)
    tests_df.to_csv(csv_dir / "second_hand_2x2_factorial_tests.csv", index=False)
    (out_dir / "report.md").write_text(render_markdown(cells_df, tests_df), encoding="utf-8")
    (out_dir / "report.html").write_text(render_html(cells_df, tests_df), encoding="utf-8")
    return cells_df, tests_df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    build_report(args.results_dir, args.out_dir)
    print(f"Wrote Second-Hand 2x2 report to {args.out_dir}")


if __name__ == "__main__":
    main()
