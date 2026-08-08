# lead-split — Tyson & Berry lead-sale settlement

**Status:** DELIVERED 2026-08-08, then **DEEP RE-VERIFIED same day** on Bob's request. Verdict
**unchanged**. Page LIVE. **Bob's sheet still NOT edited by me — no write path** (see below).

Deliverable: **https://opheliaclarke.github.io/lead-split/** (noindex + robots disallow; public repo
because Pages needs it on the free plan — flagged to Bob since it holds partner financials).

## The answer (confirmed twice, by 6 independent routes)

| | |
|---|---|
| Total revenue | **$200.00** (25 leads × $8) |
| Total cost | **$829.31** (Actual Cost 799.31 + TFN 30) |
| **Net** | **−$629.31 — a LOSS** |
| Each partner's 50% share | **−$314.655** |
| Settlement | **Berry pays Tyson $332.655** (~$332.66) |

Cash before settling: Tyson −647.31 (collected 152, paid 799.31) · Berry +18.00 (collected 48, paid 30).
Bob confirmed 2026-08-08: **Berry's cost is $30 (TFN) only for this row**; other costs come later.

## Sheet facts

Sheet `1xDqMSy_3GHNS221kkenyRowODydeOB7w2MKeVnJvdwM`, one tab `Sheet1`, ONE data row.
Columns: `Date | Leads (Dino) | Leads (Olivia) | Leads (Tyson) | Spent | Rev (Olivia) | Rev (Dino) |
Rev (Tyson) | Actual Cost | TFN Cost | Total Rev | Tyson | Berry`.

- `A2` serial 46241 = **2026-08-07** ✓ matches the "7 August" label.
- `Actual Cost = Spent*0.67` → 1193 × 0.67 = **799.31 exactly** (floats show 799.3100000000001).
  The 0.67 **writes off $393.69 (33%)** — flagged to Bob: if that's an unreceived rebate, cash owed differs.
- **Tyson collects H2 (19 leads = 152); Berry collects F2+G2 (Dino 2 + Olivia 4 = 48).** That mapping is
  encoded in the original formulas, not guessed.
- Verified absent: hidden rows/columns, threaded comments, drawings, merged cells, data validation,
  conditional formatting, extra tabs. `persons.xml` + `drawing1.xml` are empty stubs.

## ⚠ THE SHEET CHANGED between the first pull and the re-check (found by diffing snapshots)

| Cell | Before | Now |
|---|---|---|
| `M2` Berry | `=(K2/2)-(I2/2)-F2-G2` → −362.655 | `=(K2/2)-(I2/2)-F2-G2+J2` → **−332.655** ✅ CORRECT |
| `L2` Tyson | `=(K2/2)-(I2/2)-H2` → −466.655 | **unchanged — still WRONG** |
| `I4` | did not exist | `=(830-170)/2` → **330 — WRONG** |

⭐ **Someone fixed Berry's cell and got it exactly right** — `+J2` credits Berry the TFN he paid.
Proved with sympy that the new `M2` is **identical to the correct settlement formula for all inputs**
(not a coincidence at these numbers; holds even when R ≠ Fg + H).

## ⚠ What is still wrong

1. **`L2` (Tyson) is missing `+I2`** — the same "add back what you paid" term, for his $799.31.
   Proved short by **exactly `I2`** for all inputs. ⭐ **The tell: `L2 + M2` = −799.31, not 0.**
   A two-partner settlement **must be zero-sum**; the residual names the missing term.
   ⚠ **Its sign is inverted** — the cell reads −466.655 (looks like Tyson owes) when Tyson is
   **owed +332.655**. Acting on it sends money the wrong way. Note a sum-check alone will NOT catch a
   pure sign flip; only the per-partner target does.
2. **`I4` = 330 is wrong**; correct loss/partner is **314.655**. Error **+15.345**, decomposing exactly:
   **+15.000** = the $30 TFN counted **twice** (as a cost inside 830 *and* as the −30 that shrank
   revenue to 170), **+0.345** = 829.31 rounded up to 830. 330 is also not the transfer (332.655) —
   it is neither figure. Delete it.

## ⭐ THE TRAP — do not "fix" K2 alone

`K2 = (B2+C2+D2)*8-J2` = 170 is **mislabelled** (real revenue is 200), **but the buried J is
load-bearing**: `(K2/2)-(I2/2)` expands to exactly `(R-I-J)/2`, which is what charges the TFN to the
partnership at the right 50%. **Change K2 to 200 and leave L2/M2 alone → both partners come out exactly
`J/2` = $15 wrong** (Tyson 347.655, Berry −317.655) and they stop summing to zero. Change all three
together or none. Burying J does **not** affect the net (`K2-I2 = R-(I+J)`), only the reported revenue —
but it is the direct cause of the I4 error.

## Two verified fix options (both proved symbolically + numerically)

- **A — one cell:** `L2` → `=(K2/2)-(I2/2)-H2+I2` → +332.655. K2/M2 untouched. K2 still misreports revenue.
- **B — clean, three cells (recommended):** `K2` → `=(B2+C2+D2)*8` · `L2` → `=(K2-I2-J2)/2-(H2-I2)` ·
  `M2` → `=(K2-I2-J2)/2-(F2+G2-J2)`, then **delete I4**. Every cell then reads the model literally.

## Model

Both partners work jointly and split 50/50, so all revenue and all cost are partnership items; whose
account the money moved through is **custody, not ownership**.
**`settlement = (net / 2) − (cash collected) + (cash paid)`**, positive = receives.

⚠ Alternative tested: if each partner instead **keeps the revenue he personally sold** and only costs
are shared → **Berry pays Tyson $384.655**, exactly **$52** more = half the collections gap (152−48)/2.
Rejected because the sheet's own `K2/2` halves *total* revenue, i.e. revenue is pooled. Third reading
(own revenue, own cost) → no payment, but Tyson eats 647.31 while Berry profits on a losing day.

## ⭐ The business number (raised unprompted)

Cost per lead **$33.17** vs **$8** sold = **−$25.17 per lead**; revenue covered **24%** of cost.
Break-even on that $1,193 spend needs **104 leads**; they got 25. The split is fine — the unit
economics are the problem.

## 🛑 Could NOT edit the sheet — no write path

Sheet is public-read (CSV/xlsx export works unauthenticated) but writing needs the Sheets API:
Sheets **and** Drive APIs are **disabled on project `coolizi-gsc`** (the only SA here), and the SA
**cannot self-enable** them (403 PERMISSION_DENIED). Even enabled, it would still need Editor on the
file. See [[no-google-sheets-write-access]].

## Verification performed

- `model.py` — raw inputs → result with **`Fraction`, never float**; 7 double-entry assertions.
- `verify_formulas.py` — evaluates handed-over formulas the way Sheets would, cross-checks vs model.
- `proof.py` — **sympy**: M2 ≡ settlement_Berry for all inputs · L2 short by exactly I2 · L2+I2 is the
  exact fix · zero-sum · the K2 trap quantified as J/2 · I4 decomposition exact.
- `verify_fixes.py` — both fix options proved, plus the trap magnitude.
- `verify_page.py` — pulls formulas/numbers **off the built page** and evaluates them (catches a page
  that drifts from the verified model).
- **Two independent sub-agents**, one briefed to *refute*; all 7 figures re-derived 4 separate ways,
  **0 discrepancies**. Both independently reached "Berry owes Tyson 332.655".
- Page QA: 0 contrast failures (runtime walker compositing alpha), 0 console errors, no overflow
  desktop+mobile, all 4 copy buttons asserted to put the exact formula on the clipboard.

⚠ **My own assertion caught my own error** during this pass: I first decomposed the I4 gap against
*Actual Cost* 799.31 instead of *total cost* 829.31; the exactness assert failed and forced the fix.
Keep decomposition asserts — they're the reason the 15 + 0.345 split is trustworthy.

## Open — needs Bob

1. **Half-cent:** $314.655 isn't payable. $332.66 puts the cent on Berry, $332.65 on Tyson. Pick one.
2. **The 0.67 haircut** — confirm it's a real cost reduction already banked, not a pending rebate.
3. **50/50 confirmed?** Assumed throughout, matching the sheet's own halving.

## Files

`model.py` · `proof.py` · `verify_fixes.py` · `verify_formulas.py` · `verify_page.py` · `qa.py` ·
`index.html` · `paste-block.tsv` (full 11-col ledger, superseded by the smaller fix options) ·
`original-sheet-snapshot.csv` (first pull) · `sheet-snapshot-0808-recheck.csv/.xlsx` (post-change).
