#!/usr/bin/env python3
"""Sanity tests for the statistical helpers, using simulated data with known answers. Run: python3 test_t3lib.py"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))
import t3lib  # noqa: E402


def test_holm():
    adj = t3lib.holm([0.01, 0.04, 0.03, 0.005])
    assert np.allclose(adj, [0.03, 0.06, 0.06, 0.02]), adj


def test_norm_isf():
    assert abs(t3lib.norm_isf(0.025) - 1.959964) < 1e-4
    assert abs(t3lib.norm_isf(0.2) - 0.841621) < 1e-4


def test_pair_table():
    rows = []
    for pid, (r_scores, t_scores) in {"p1": ([0, 0.5, 1], [1, 1, 0.5]), "p2": ([0], [np.nan])}.items():
        for cond, sc in (("rumor", r_scores), ("truth_twin", t_scores)):
            for i, v in enumerate(sc):
                rows.append(dict(pair_id=pid, condition=cond, layer="first_hand", score=v, go=0, **{k: "x" for k in t3lib.PAIR_ATTRS}))
    pt = t3lib.pair_table(pd.DataFrame(rows), "score", "first_hand").set_index("pair_id")
    assert abs(pt.loc["p1", "rumor_mean"] - 0.5) < 1e-9 and abs(pt.loc["p1", "truth_mean"] - 5 / 6) < 1e-9
    assert abs(pt.loc["p1", "td"] - (5 / 6 - 0.5)) < 1e-9
    assert np.isnan(pt.loc["p2", "td"])  # truth twin has no valid score


def test_fit_contrasts_recovers_planted_effects():
    rng = np.random.default_rng(1)
    n = 6000
    pt = pd.DataFrame({k: rng.choice([a, b], n) for k, a, b, _ in t3lib.KNOBS})
    pt["pair_id"] = range(n)
    x = {k: t3lib.code_pm(pt[k], a) for k, a, _, _ in t3lib.KNOBS}
    truth = {"closeness": -0.10, "reliability": 0.25, "x:closeness:reliability": 0.20, "age": 0.0}
    pt["td"] = (0.3 + truth["closeness"] * x["closeness"] + truth["reliability"] * x["reliability"]
                + truth["x:closeness:reliability"] * x["closeness"] * x["reliability"] + rng.normal(0, 0.3, n))
    t, _ = t3lib.fit_contrasts(pt)
    by = t.set_index("id")
    for cid, want in ((1, -0.10), (4, 0.25), (5, 0.20), (10, 0.0)):
        r = by.loc[cid]
        assert abs(r.estimate - want) < 3.5 * r.se, (cid, r.estimate, want, r.se)
    assert by.loc[4, "significant_holm_05"] and not by.loc[10, "significant_holm_05"]
    # a difference-in-differences coefficient must equal the cell-mean DiD
    m = pt.groupby(["closeness", "reliability"]).td.mean()
    did = (m[("close_friend", "good_record")] - m[("stranger", "good_record")]) - (m[("close_friend", "poor_record")] - m[("stranger", "poor_record")])
    assert abs(did - by.loc[5, "estimate"]) < 0.02, (did, by.loc[5, "estimate"])


def test_icc_recovery():
    rng = np.random.default_rng(2)
    G, m = 400, 6
    g = np.repeat(np.arange(G), m)
    y = rng.normal(0, np.sqrt(0.3), G)[g] + rng.normal(0, np.sqrt(0.7), G * m)
    icc, lo, hi, groups, nbar, deff = t3lib.icc_anova(y, g, B=100)
    assert abs(icc - 0.3) < 0.05 and lo < icc < hi and groups == G and abs(deff - (1 + 5 * icc)) < 1e-9
    y0 = rng.normal(0, 1, G * m)
    assert abs(t3lib.icc_anova(y0, g)[0]) < 0.05  # no clustering -> about 0


def test_boot_mean_covers_truth():
    rng = np.random.default_rng(3)
    hits = 0
    for s in range(60):
        x = rng.normal(0.4, 1, 200)
        _, lo, hi, _ = t3lib.boot_mean(x, B=400, seed=s)
        hits += lo <= 0.4 <= hi
    assert 50 <= hits <= 60, hits  # nominal 95%


def test_read_labels_tolerates_torn_jsonl(tmp="/tmp/_t3_labels.jsonl"):
    with open(tmp, "w") as f:
        f.write('{"run_id": "a", "seat_id_private": 1, "label": "fact"}\n{"run_id": "b", "seat": 2, "label": "NOPE"}\n{"run_id": "c", "se')
    lab = t3lib.read_labels([tmp])
    assert len(lab) == 1 and lab.label.iloc[0] == "FACT" and lab.seat.iloc[0] == 1
    os.remove(tmp)


def test_kappa_known_table():
    # textbook 2x2: [[20, 5], [10, 15]] -> po = 0.70, pe = 0.50, kappa = 0.40
    a = np.array([0] * 25 + [1] * 25)
    b = np.array([0] * 20 + [1] * 5 + [0] * 10 + [1] * 15)
    k, _, _, agree, n = t3lib.kappa_stats(a, b)
    assert abs(k - 0.4) < 1e-9 and abs(agree - 0.7) < 1e-9 and n == 50
    assert t3lib.kappa_stats(a, a)[0] == 1.0


def test_swap_test_calibration():
    rng = np.random.default_rng(5)
    rej_null = sum(t3lib.swap_test(rng.multinomial(10, [.3, .3, .4], size=150), rng.multinomial(10, [.3, .3, .4], size=150), B=400, seed=s)[1] < 0.05 for s in range(60))
    rej_alt = sum(t3lib.swap_test(rng.multinomial(10, [.3, .3, .4], size=150), rng.multinomial(10, [.2, .3, .5], size=150), B=400, seed=s)[1] < 0.05 for s in range(20))
    assert rej_null <= 9, rej_null      # nominal 5% of 60 = 3
    assert rej_alt >= 19, rej_alt       # real difference is detected


def test_flag_rate_ci_handles_empty_subset():
    df = pd.DataFrame({"pair_id": [1, 2], "go": [0, 1], "f": [0, 1]})
    assert np.isnan(t3lib.flag_rate_ci(df, "f", np.array([False, False]))[0])
    assert t3lib.SCHEMES["primary (1 / 0.5 / 0)"] == t3lib.SCORE


if __name__ == "__main__":
    n = 0
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            n += 1
            print("ok", name)
    print(f"{n} tests passed")
