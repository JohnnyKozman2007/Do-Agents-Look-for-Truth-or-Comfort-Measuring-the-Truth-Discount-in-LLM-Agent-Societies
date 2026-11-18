# Second-Hand 2×2 Report (`Own GO/SKIP × Partner GO/SKIP`)

**Judge:** Gemini 3.7 Flash (`results/main-gemini-3.7-flash`) | **Layer:** Second-Hand (Seats 7–12 paired with First-Hand Seats 1–6) | **Clustering:** Twin Pair (`pair_id`)

### Methodological & Interpretation Note
- **4-Cell Routing:** Every second-hand listener is cross-classified by their own verification decision (`Own GO` vs `Own SKIP`) and their paired first-hand partner's decision (`Partner GO` vs `Partner SKIP`, Seat `i` ↔ Seat `i+6`).
- **Missingness:** `judgment_status = invalid` rows stay `NaN` (never zero-imputed). `Belief` is over valid mentioning listeners; label `%` is over valid listeners.
- **Causal vs. Descriptive Distinction:** `Neither Checked` directly tests zero twin-to-twin leakage. However, `Own GO` and `Partner GO` are endogenous behavioral choices rather than randomized treatments, so cell shares and the small `Both Checked` vs. `SH Only` difference reflect selection/routing as well as direct checking.

---

## 1. 2×2 Second-Hand Summary Tables

### Both Models Combined

| 2×2 Cell | R N (Share) | T N (Share) | Rumor Belief | Truth Belief | Truth Discount [95% CI] | p | Sil=0.0 TD | Sil=0.5 TD | R FACT % | T FACT % | R SKEP % | T SKEP % | R NM % | T NM % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Both Checked** (Own GO, Partner GO) | 7,943 (26.5%) | 8,029 (26.8%) | 0.004 | 0.961 | **+0.956** [+0.953, +0.960] | <0.0001 | +0.956 | +0.908 | 0.03% | 8.0% | 2.0% | 1.7% | 9.69% | 0.06% |
| **SH Only** (Own GO, Partner SKIP) | 5,626 (18.8%) | 5,705 (19.0%) | 0.003 | 0.986 | **+0.984** [+0.981, +0.987] | <0.0001 | +0.984 | +0.964 | 0.02% | 5.6% | 1.9% | 0.5% | 4.03% | 0.04% |
| **Partner Only** (Own SKIP, Partner GO) | 13,182 (44.0%) | 13,118 (43.8%) | 0.052 | 0.782 | **+0.730** [+0.723, +0.737] | <0.0001 | +0.729 | +0.691 | 1.13% | 14.1% | 23.6% | 13.0% | 8.21% | 0.68% |
| **Neither Checked** (Own SKIP, Partner SKIP) | 3,201 (10.7%) | 3,100 (10.3%) | 0.047 | 0.045 | **-0.002** [-0.009, +0.005] | 0.6041 | -0.002 | -0.002 | 0.31% | 0.2% | 89.5% | 89.5% | 0.88% | 0.81% |

### DeepSeek-V4-Flash

| 2×2 Cell | R N (Share) | T N (Share) | Rumor Belief | Truth Belief | Truth Discount [95% CI] | p | Sil=0.0 TD | Sil=0.5 TD | R FACT % | T FACT % | R SKEP % | T SKEP % | R NM % | T NM % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Both Checked** (Own GO, Partner GO) | 4,291 (28.7%) | 5,077 (33.9%) | 0.006 | 0.953 | **+0.947** [+0.941, +0.952] | <0.0001 | +0.947 | +0.869 | 0.02% | 9.5% | 2.6% | 1.8% | 15.69% | 0.02% |
| **SH Only** (Own GO, Partner SKIP) | 4,999 (33.4%) | 5,085 (34.0%) | 0.003 | 0.986 | **+0.983** [+0.980, +0.986] | <0.0001 | +0.983 | +0.962 | 0.02% | 5.9% | 2.0% | 0.5% | 4.31% | 0.00% |
| **Partner Only** (Own SKIP, Partner GO) | 2,938 (19.6%) | 2,182 (14.6%) | 0.059 | 0.843 | **+0.785** [+0.771, +0.799] | <0.0001 | +0.793 | +0.724 | 0.62% | 17.9% | 23.3% | 6.1% | 13.86% | 0.00% |
| **Neither Checked** (Own SKIP, Partner SKIP) | 2,748 (18.3%) | 2,632 (17.6%) | 0.050 | 0.048 | **-0.002** [-0.010, +0.006] | 0.6204 | -0.002 | -0.002 | 0.33% | 0.2% | 89.9% | 89.8% | 0.26% | 0.27% |

### Qwen3.8-Flash

| 2×2 Cell | R N (Share) | T N (Share) | Rumor Belief | Truth Belief | Truth Discount [95% CI] | p | Sil=0.0 TD | Sil=0.5 TD | R FACT % | T FACT % | R SKEP % | T SKEP % | R NM % | T NM % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Both Checked** (Own GO, Partner GO) | 3,652 (24.4%) | 2,952 (19.7%) | 0.003 | 0.974 | **+0.972** [+0.966, +0.977] | <0.0001 | +0.970 | +0.958 | 0.03% | 5.5% | 1.2% | 1.5% | 2.66% | 0.14% |
| **SH Only** (Own GO, Partner SKIP) | 627 (4.2%) | 620 (4.1%) | 0.000 | 0.989 | **+0.989** [+0.982, +0.997] | <0.0001 | +0.986 | +0.979 | 0.00% | 3.4% | 1.4% | 0.8% | 1.75% | 0.32% |
| **Partner Only** (Own SKIP, Partner GO) | 10,244 (68.4%) | 10,936 (73.0%) | 0.051 | 0.770 | **+0.719** [+0.711, +0.727] | <0.0001 | +0.716 | +0.687 | 1.28% | 13.4% | 23.6% | 14.4% | 6.59% | 0.81% |
| **Neither Checked** (Own SKIP, Partner SKIP) | 453 (3.0%) | 468 (3.1%) | 0.032 | 0.032 | **-0.000** [-0.018, +0.018] | 0.9836 | +0.000 | -0.004 | 0.22% | 0.4% | 87.2% | 87.8% | 4.64% | 3.85% |

---

## 2. 2×2 Factorial Interaction Tests (`outcome ~ truth * own_go * partner_go`, Pair-Clustered)

### Both Models Combined

| Outcome | Term | Meaning | Estimate | SE | 95% CI | p (clustered) |
|---|---|---|---:|---:|---:|---:|
| Belief Score (0-1) | `own_go` | Own GO (Rumor baseline) | -0.0449 | 0.0028 | [-0.0504, -0.0394] | <0.0001 |
| Belief Score (0-1) | `partner_go` | Partner GO (Rumor baseline) | +0.0050 | 0.0032 | [-0.0013, +0.0112] | 0.1222 |
| Belief Score (0-1) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.0033 | 0.0033 | [-0.0097, +0.0032] | 0.3198 |
| Belief Score (0-1) | `truth:own_go` | Own GO effect on Truth Discount | +0.9858 | 0.0040 | [+0.9779, +0.9936] | <0.0001 |
| Belief Score (0-1) | `truth:partner_go` | Partner GO effect on Truth Discount | +0.7319 | 0.0052 | [+0.7216, +0.7421] | <0.0001 |
| Belief Score (0-1) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -0.7593 | 0.0057 | [-0.7706, -0.7481] | <0.0001 |
| FACT (%) | `own_go` | Own GO (Rumor baseline) | -0.2953 | 0.1007 | [-0.4926, -0.0979] | 0.0034 |
| FACT (%) | `partner_go` | Partner GO (Rumor baseline) | +0.8173 | 0.1359 | [+0.5510, +1.0836] | <0.0001 |
| FACT (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.8099 | 0.1382 | [-1.0807, -0.5390] | <0.0001 |
| FACT (%) | `truth:own_go` | Own GO effect on Truth Discount | +5.7018 | 0.3349 | [+5.0453, +6.3582] | <0.0001 |
| FACT (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +13.1268 | 0.3534 | [+12.4341, +13.8195] | <0.0001 |
| FACT (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -10.7057 | 0.5646 | [-11.8123, -9.5990] | <0.0001 |
| SKEPTICAL (%) | `own_go` | Own GO (Rumor baseline) | -87.5733 | 0.5879 | [-88.7256, -86.4211] | <0.0001 |
| SKEPTICAL (%) | `partner_go` | Partner GO (Rumor baseline) | -65.9181 | 0.6646 | [-67.2206, -64.6155] | <0.0001 |
| SKEPTICAL (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | +65.9684 | 0.7058 | [+64.5850, +67.3518] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go` | Own GO effect on Truth Discount | -1.4410 | 0.7920 | [-2.9933, +0.1112] | 0.0688 |
| SKEPTICAL (%) | `truth:partner_go` | Partner GO effect on Truth Discount | -10.5721 | 0.9026 | [-12.3412, -8.8030] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | +11.7097 | 0.9487 | [+9.8502, +13.5692] | <0.0001 |
| UNCERTAIN (%) | `own_go` | Own GO (Rumor baseline) | -8.2583 | 0.5173 | [-9.2723, -7.2443] | <0.0001 |
| UNCERTAIN (%) | `partner_go` | Partner GO (Rumor baseline) | -1.7383 | 0.5596 | [-2.8352, -0.6414] | 0.0019 |
| UNCERTAIN (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | +1.9494 | 0.5723 | [+0.8277, +3.0710] | 0.0007 |
| UNCERTAIN (%) | `truth:own_go` | Own GO effect on Truth Discount | +1.4536 | 0.7164 | [+0.0494, +2.8578] | 0.0425 |
| UNCERTAIN (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +9.6693 | 0.8012 | [+8.0989, +11.2397] | <0.0001 |
| UNCERTAIN (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -6.9395 | 0.8545 | [-8.6143, -5.2647] | <0.0001 |

### DeepSeek-V4-Flash

| Outcome | Term | Meaning | Estimate | SE | 95% CI | p (clustered) |
|---|---|---|---:|---:|---:|---:|
| Belief Score (0-1) | `own_go` | Own GO (Rumor baseline) | -0.0469 | 0.0031 | [-0.0530, -0.0408] | <0.0001 |
| Belief Score (0-1) | `partner_go` | Partner GO (Rumor baseline) | +0.0088 | 0.0046 | [-0.0002, +0.0179] | 0.0559 |
| Belief Score (0-1) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.0058 | 0.0047 | [-0.0151, +0.0035] | 0.2186 |
| Belief Score (0-1) | `truth:own_go` | Own GO effect on Truth Discount | +0.9851 | 0.0044 | [+0.9766, +0.9937] | <0.0001 |
| Belief Score (0-1) | `truth:partner_go` | Partner GO effect on Truth Discount | +0.7868 | 0.0084 | [+0.7704, +0.8033] | <0.0001 |
| Belief Score (0-1) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -0.8232 | 0.0089 | [-0.8407, -0.8057] | <0.0001 |
| FACT (%) | `own_go` | Own GO (Rumor baseline) | -0.3083 | 0.1114 | [-0.5267, -0.0899] | 0.0057 |
| FACT (%) | `partner_go` | Partner GO (Rumor baseline) | +0.2875 | 0.1816 | [-0.0684, +0.6433] | 0.1134 |
| FACT (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.2841 | 0.1841 | [-0.6450, +0.0768] | 0.1228 |
| FACT (%) | `truth:own_go` | Own GO effect on Truth Discount | +6.0307 | 0.3615 | [+5.3221, +6.7394] | <0.0001 |
| FACT (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +17.4743 | 0.8607 | [+15.7874, +19.1611] | <0.0001 |
| FACT (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -13.8650 | 1.0207 | [-15.8655, -11.8645] | <0.0001 |
| SKEPTICAL (%) | `own_go` | Own GO (Rumor baseline) | -87.8914 | 0.6291 | [-89.1244, -86.6584] | <0.0001 |
| SKEPTICAL (%) | `partner_go` | Partner GO (Rumor baseline) | -66.5255 | 0.9627 | [-68.4125, -64.6386] | <0.0001 |
| SKEPTICAL (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | +67.1594 | 1.0126 | [+65.1747, +69.1440] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go` | Own GO effect on Truth Discount | -1.4646 | 0.8439 | [-3.1186, +0.1893] | 0.0826 |
| SKEPTICAL (%) | `truth:partner_go` | Partner GO effect on Truth Discount | -17.2008 | 1.2215 | [-19.5950, -14.8067] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | +17.8936 | 1.2818 | [+15.3813, +20.4060] | <0.0001 |
| UNCERTAIN (%) | `own_go` | Own GO (Rumor baseline) | -8.6921 | 0.5764 | [-9.8219, -7.5623] | <0.0001 |
| UNCERTAIN (%) | `partner_go` | Partner GO (Rumor baseline) | -0.5382 | 0.7772 | [-2.0616, +0.9851] | 0.4886 |
| UNCERTAIN (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | +0.8799 | 0.7940 | [-0.6763, +2.4361] | 0.2678 |
| UNCERTAIN (%) | `truth:own_go` | Own GO effect on Truth Discount | +1.3311 | 0.7972 | [-0.2314, +2.8936] | 0.0950 |
| UNCERTAIN (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +10.3917 | 1.2699 | [+7.9027, +12.8808] | <0.0001 |
| UNCERTAIN (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -6.5562 | 1.3352 | [-9.1732, -3.9391] | <0.0001 |

### Qwen3.8-Flash

| Outcome | Term | Meaning | Estimate | SE | 95% CI | p (clustered) |
|---|---|---|---:|---:|---:|---:|
| Belief Score (0-1) | `own_go` | Own GO (Rumor baseline) | -0.0324 | 0.0061 | [-0.0443, -0.0205] | <0.0001 |
| Belief Score (0-1) | `partner_go` | Partner GO (Rumor baseline) | +0.0183 | 0.0063 | [+0.0059, +0.0307] | 0.0039 |
| Belief Score (0-1) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.0157 | 0.0064 | [-0.0282, -0.0033] | 0.0134 |
| Belief Score (0-1) | `truth:own_go` | Own GO effect on Truth Discount | +0.9897 | 0.0098 | [+0.9705, +1.0088] | <0.0001 |
| Belief Score (0-1) | `truth:partner_go` | Partner GO effect on Truth Discount | +0.7195 | 0.0099 | [+0.7001, +0.7389] | <0.0001 |
| Belief Score (0-1) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -0.7373 | 0.0108 | [-0.7586, -0.7161] | <0.0001 |
| FACT (%) | `own_go` | Own GO (Rumor baseline) | -0.2208 | 0.2207 | [-0.6534, +0.2119] | 0.3173 |
| FACT (%) | `partner_go` | Partner GO (Rumor baseline) | +1.0575 | 0.2476 | [+0.5722, +1.5428] | <0.0001 |
| FACT (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -1.0301 | 0.2491 | [-1.5185, -0.5418] | <0.0001 |
| FACT (%) | `truth:own_go` | Own GO effect on Truth Discount | +3.1805 | 0.8223 | [+1.5688, +4.7922] | 0.0001 |
| FACT (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +11.9015 | 0.5169 | [+10.8883, +12.9147] | <0.0001 |
| FACT (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -9.7812 | 0.9911 | [-11.7237, -7.8387] | <0.0001 |
| SKEPTICAL (%) | `own_go` | Own GO (Rumor baseline) | -85.7611 | 1.6116 | [-88.9198, -82.6024] | <0.0001 |
| SKEPTICAL (%) | `partner_go` | Partner GO (Rumor baseline) | -63.5681 | 1.5993 | [-66.7028, -60.4335] | <0.0001 |
| SKEPTICAL (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | +63.3382 | 1.6854 | [+60.0347, +66.6417] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go` | Own GO effect on Truth Discount | -1.2530 | 2.2557 | [-5.6743, +3.1683] | 0.5786 |
| SKEPTICAL (%) | `truth:partner_go` | Partner GO effect on Truth Discount | -9.8320 | 2.2464 | [-14.2349, -5.4291] | <0.0001 |
| SKEPTICAL (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | +10.7835 | 2.3360 | [+6.2050, +15.3620] | <0.0001 |
| UNCERTAIN (%) | `own_go` | Own GO (Rumor baseline) | -5.7395 | 1.0772 | [-7.8508, -3.6282] | <0.0001 |
| UNCERTAIN (%) | `partner_go` | Partner GO (Rumor baseline) | +0.7403 | 1.1065 | [-1.4284, +2.9091] | 0.5034 |
| UNCERTAIN (%) | `own_go:partner_go` | Own GO x Partner GO (Rumor baseline) | -0.3020 | 1.1116 | [-2.4807, +1.8768] | 0.7859 |
| UNCERTAIN (%) | `truth:own_go` | Own GO effect on Truth Discount | +1.7362 | 1.4847 | [-1.1738, +4.6462] | 0.2422 |
| UNCERTAIN (%) | `truth:partner_go` | Partner GO effect on Truth Discount | +10.4830 | 1.5147 | [+7.5142, +13.4518] | <0.0001 |
| UNCERTAIN (%) | `truth:own_go:partner_go` | Own GO x Partner GO interaction on Truth Discount | -9.3000 | 1.5678 | [-12.3727, -6.2272] | <0.0001 |
