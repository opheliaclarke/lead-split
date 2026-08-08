# lead-split — Tyson & Berry lead-sale settlement

**Status:** DELIVERED 2026-08-08. Page LIVE. **Bob's sheet NOT edited by me — I have no write path** (see below).

## What this is

Bob shared a Google Sheet
(`1xDqMSy_3GHNS221kkenyRowODydeOB7w2MKeVnJvdwM`, one tab `Sheet1`, ONE data row "7 August")
and asked: total cost incurred, how much comes to each of Tyson and Berry, and if it's a loss,
how much each bears — plus **make the edits in the sheet**.

Deliverable: **https://opheliaclarke.github.io/lead-split/** (noindex + robots disallow, public repo
because Pages needs it on the free plan — flagged to Bob since it holds partner financials).

## The answer

| | |
|---|---|
| Total revenue | **$200.00** (25 leads × $8) |
| Total cost | **$829.31** (Actual Cost 799.31 + TFN 30) |
| **Net** | **−$629.31 — a LOSS** |
| Each partner's 50% share | **−$314.655** |
| Settlement | **Berry pays Tyson $332.655** (~$332.66) |

Cash before settling: Tyson −647.31 (collected 152, paid 799.31) · Berry +18.00 (collected 48, paid 30).

## Facts about the sheet (read off the xlsx export, formulas included)

- Columns: `Date | Leads (Dino) | Leads (Olivia) | Leads (Tyson) | Spent | Rev (Olivia) | Rev (Dino) |
  Rev (Tyson) | Actual Cost | TFN Cost | Total Rev | Tyson | Berry`
- `Actual Cost = Spent*0.67` → 1193 × 0.67 = **799.31 exactly** (in floats it shows 799.3100000000001).
- Buyers: **Tyson collects from his own bucket (19 leads = 152)**; **Berry collects from Dino + Olivia
  (2 + 4 = 48)**. That mapping is what the original `Tyson`/`Berry` formulas encode — not a guess.
- Bob's stated cost split: **Tyson pays campaign spend, Berry pays TFN + technical setup + routing.**

## ⚠ The bug found in the original sheet

Original: `Tyson =(K2/2)-(I2/2)-H2` → −466.655 · `Berry =(K2/2)-(I2/2)-F2-G2` → −362.655.

They sum to **−829.31**, which is neither **0** (if the cells mean "who pays whom") nor **−629.31**
(if they mean "final position") — wrong on either reading, and the two partners land **$104 apart**
despite a 50/50 split.

- **The real defect:** the formula subtracts the cash a partner *collected* but never adds back the
  cash he *paid*. `(170/2)-(799.31/2)` is already exactly −314.655 (the correct 50% share); it then
  subtracts Tyson's 152 with no credit for his 799.31. Missing term: `+ own cash paid`.
- **Secondary (cosmetic, doesn't move the total):** `Total Rev =(B2+C2+D2)*8-J2` buries the $30 TFN
  **cost** inside the **revenue** column, so revenue reads 170 when 200 was billed. Net is unaffected
  (the $30 is a cost either way) but the revenue cell is wrong for any margin/day-over-day comparison.

## 🛑 Could NOT edit the sheet — no write path

Sheet is **public-read** (CSV/xlsx export works unauthenticated) but writing needs the Sheets API:
- Only Google identity here is SA `gsc-reader@coolizi-gsc.iam.gserviceaccount.com`.
- **Sheets API AND Drive API are both DISABLED on project `coolizi-gsc` (577887090553)** → 403.
- SA **cannot self-enable** them: `serviceusage…:enable` → 403 PERMISSION_DENIED.
- Even if enabled, the SA would still need to be added as an **Editor** on the file.

⇒ Delivered as a **one-paste TSV block** instead (`paste-block.tsv`, also a copy button on the page):
paste at **K1**, fills **K1:U2**, replaces the broken `Total Rev / Tyson / Berry` columns.
To actually write it myself Bob would need to enable both APIs on that GCP project *and* share the
sheet with the SA as Editor.

## New column layout (K→U, A–J untouched)

`K Berry Other Cost (manual, 0)` · `L Total Rev =F2+G2+H2` · `M Total Cost =I2+J2+K2` ·
`N Net P/L =L2-M2` · `O/P Share =$N2/2` · `Q Tyson Cash =H2-I2` · `R Berry Cash =F2+G2-J2-K2` ·
`S Tyson Settlement =O2-Q2` · `T Berry Settlement =P2-R2` · `U Check =ROUND(S2+T2,6)` (must read 0).

Settlement sign: **positive = receives, negative = pays.**

## Verification done

- `model.py` — recomputes from raw inputs with **`Fraction`, never float**; 7 double-entry assertions
  (cash positions sum to net; settlements sum to 0; each partner's cash+settlement == his 50% share).
- `verify_formulas.py` — evaluates **the handed-over formulas themselves** the way Sheets would and
  cross-checks every cell against `model.py`. Catches a wrong formula, not just wrong arithmetic.
- Independent sub-agent verified all 7 figures via **4 separate routes** (Fraction, Decimal by a
  different algebraic path, integer milli-cent ledger, literal cash simulation) — **0 discrepancies**.
- Page QA: **15/15 WCAG contrast pass**, 0 console errors, no horizontal overflow desktop+mobile,
  copy button asserted to put **20 tabs / 2 lines** on the clipboard, and the on-page block asserted
  **byte-identical** to `paste-block.tsv` (tabs are load-bearing — spaces would break the paste).

## ⚠ Open — needs Bob

1. **Berry's technical setup + routing costs are NOT in the sheet.** Only his $30 TFN is recorded, so
   the maths currently assumes they're zero. Column `K — Berry Other Cost` exists to hold them; every
   figure moves when it's filled in.
2. **Assumed a straight 50/50** on both revenue and cost — which is what the original formula was
   reaching for (it halved both). If the real deal is a different ratio, change the `/2`.
3. **Half-cent:** $314.655 isn't payable. Decide who eats the cent and stay consistent.

## Files

`model.py` (source of truth) · `verify_formulas.py` · `paste-block.tsv` · `index.html` ·
`original-sheet-snapshot.csv` (pre-change export) · `qa.py` · `results.json`.
