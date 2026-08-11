# lead-split — Tyson & Berry lead-sale settlement

## ⭐ 11 AUGUST — CURRENT ANSWER: **BERRY STILL OWES TYSON $502.93**

Bob asked how much moves after Berry's **$500 advance on day 1** (and nothing since, either way).

**Sheet now has THREE rows: 7 Aug, 10 Aug, 11 Aug.** ⚠ **The 8 August row was DELETED** (it existed on
08-08: 65 leads, spent 565, net +111.45, Berry owed 130.275) — flagged to Bob on the page; if restored
the answer becomes **$633.205**. Sheet formulas `K/L/M/N/O` all verified correct on all three rows
(shared formulas `L2:L4` etc. — they inherit).

⭐ **Lead price CHANGED $8 → $9 from 10 August**, hard-coded in **four formulas per row** (F,G,H,K).
Recommended a Price column; the v2 engine's `Check rev path` also hard-codes `*8` and would read a
false error on every $9 row.

| | 7 Aug | 10 Aug | 11 Aug | **3-day** |
|---|---|---|---|---|
| Leads / price | 25 @ $8 | 240 @ $9 | 33 @ $9 | 298 |
| Revenue | 200.00 | 2,160.00 | 297.00 | **2,657.00** |
| Cost | 829.31 | 1,818.25 | 559.30 | **3,206.86** |
| Net | −629.31 | **+341.75** | −262.30 | **−549.86** |
| Each bears | −314.655 | +170.875 | −131.15 | **−274.93** |
| Berry → Tyson | 332.655 | 497.125 | 173.15 | **1,002.93** |

**1,002.93 − 500 already paid = $502.93.** Positions after: Tyson 1,709 − 2,986.86 + 500 = **−777.86**;
Berry 948 − 220 − 500 = **+228**; both land on −274.93. Additivity re-confirmed on real data.

⭐ **Bob's "$314" was the SHARE OF LOSS, not the obligation.** Day 1 Berry also held +$18 (collected 48,
paid 30), so he owed **332.655**; the $500 **overpaid by $167.345** — after day 1 Tyson owed *Berry*.

⭐ **Shipped: column `R` makes the sheet subtract transfers itself** —
`R2 =SUM($L$2:L2)-SUM($P$2:P2)+SUM($Q$2:Q2)` → −167.345 / 329.78 / **502.93**. ⚠ **`P` (Berry To
Tyson) and `Q` (Tyson To Berry) existed but NO formula read them** — the sheet still thought Berry
owed the full 1,002.93.
🛑 **The v2 engine must NOT be pasted any more** — it starts at `K1` and runs to `V`, so it would
**overwrite `P` and destroy the record of the $500**, silently. Warning added to the page.
⚠ A partner-to-partner transfer is **never** a cost: typing the $500 into `Spent`/`TFN` would invent
$500 of expense, cut reported profit $500 and move each share $250, with no check firing.

⭐ **Business (3 days): only the 240-lead day made money.** Cost/lead 33.17 → **7.58** → 16.95 vs price
8/9/9; margin on the good day is only **+$1.42/lead**; 3-day average **−$1.85/lead**. 11 Aug needed 63
leads to break even, got 33. ⚠ The `0.67` has now written off **$1,471.14** of $4,458 spend —
**asked four times, still unanswered.**

🛑 **THE 0.67 IS NOW THE BIGGEST OPEN NUMBER — $735.57 of settlement rides on it.** If the 33% is a
**pending rebate** rather than money already saved, Tyson is out the gross **$4,458**: net −2,021,
each −1,010.50, **Berry pays $1,238.50** not $502.93. Put on the page as a two-row table to force the
answer (asked four times). Honest treatment if pending = book full spend, enter the refund as its own
line when it lands.

Verified: `settle_0811.py` (exact `Fraction`, re-derived from raw lead counts not the sheet's totals,
zero-sum + lands-on-share + additivity + partition asserts, R-column, 8-Aug-restore and gross-spend
scenarios), independent refuting sub-agent — **all 10 claims CONFIRMED**, QA PASS (0 contrast
failures, 0 console errors, no overflow, 4/4 copy buttons).

⚠ **Two claims REFUTED during this pass — do not regress:**
1. The sub-agent reported rows 3–4 were **"dead hardcoded values"** whose shared-formula inheritance
   broke when the 8 Aug row was deleted. **FALSE.** An empty `<f t="shared" si="N"/>` **is a live
   formula** — it inherits the master's expression with offset refs. Parsed with `xml.etree`
   (not regex): masters are `I2:I4`, `L2:L4`, `M2:M4`, `N2:N4`, `O2:O4`, `F3:F4`, `G3:G4`, `H3:H4`,
   `K3:K4` — **every cell in rows 3–4 is live.**
2. My own transient "stray date serial in `P3`" was a **regex artifact**: `<c r="P3" s="4"/>` is
   self-closing, so `<c r="P3"[^>]*>(.*?)</c>` ran past it and captured `A4`. **`P3` is empty.**
⇒ **Parse xlsx with an XML parser, never a regex** — self-closing tags and shared formulas both lie
to a regex, in opposite directions.

---

**Status:** DELIVERED 2026-08-08 → deep re-verified → **turned into a formal, proved ENGINE** on Bob's
third pass (*"this will be the BASIS of this sheet… use all the mathematical knowledge you have"*).
Verdict **unchanged through all three passes**. Page LIVE. **Bob's sheet still NOT edited by me — no
write path** (see below). 🛑 **Bob killed the half-cent discussion — do not raise rounding again.**

## THE ENGINE v2 (paste at K1 → K1:V2, plus W2; A–J untouched)

`K Other cost (Tyson)` **0** · `L Other cost (Berry)` **0** · `M Total Rev =F2+G2+H2` ·
`N Total Cost =I2+J2+K2+L2` · `O Net =M2-N2` · `P/Q Share =O2/2` · `R Tyson in−out =H2-I2-K2` ·
`S Berry in−out =F2+G2-J2-L2` · `T Settlement =P2-R2` · `U Check rev path =ROUND((B2+C2+D2)*8-M2,6)` ·
`V Check balance =ROUND((P2+Q2)-(R2+S2),6)` · **`W2` = plain-English "Berry pays Tyson $332.66"**
(`=IF(ROUND(T2,2)>0,…)` — in `engine-v2-instruction.txt`).

**The one rule:** `settlement = half the net − what you collected + what you paid`.

🛑 **v1 SHIPPED A WRONG CLAIM — corrected on the live page.** I told Bob the checks `P2+Q2-M2` and
`R2+S2` would catch an unattributed cost. **They are algebraic tautologies** — identically 0 for ANY
data (proved symbolically + 50,000 random rows), and `R+S ≡ −(P+Q−M)` so the pair was redundant. They
catch **formula damage only**. Money figures were never affected. See [[partner-settlement-model]].

**v2 changes, each forced by the design audit:**
1. **A free cost cell per partner** (K, L) — extending is now *typing a number*, not editing two
   formulas one of which you'd eventually forget.
2. **One settlement + a sentence** instead of a mirrored ± pair (mirrors add no information and double
   the sign-misread surface — this sheet already shipped a sign-inverted cell).
3. **Non-redundant checks:** `U` is computed by a **different path** (lead counts, not the Rev columns)
   so it catches a typed-over `F2` (−67.00) which `V` cannot; `V` catches a damaged share formula
   (+104.885) and an unattributed cost (−125.00) which `U` cannot. Both verified firing.

⚠ **Measured: what the checks CANNOT see** (all read 0, settlement still wrong by):
missing 4 leads **$16.00** · spend typed 1139 not 1193 **$18.09** · 3 leads credited to the wrong
partner **$24.00** · a cost typed against the wrong partner **$30.00** · block pasted as static values
**$332.66**. ⇒ **"0" means the formulas are intact, NOT that the numbers are right.** Only an external
tie-out (bank statement / ad invoice) validates data.

⭐ **Error-cost rule:** `Δsettlement = Δnet/2 − Δ(own position)` — a **pool** error moves the payment by
**half**, a **custody** error (wrong payer/collector) by the **full** amount.

⚠ **Trap: never move money between `Spent` and `TFN`.** "Berry reimbursed Tyson $100 of ad spend"
typed as `E2−100, J2+100` **raises total cost $33** (0.67 applies to E2 only), moves each share
−$16.50 and the payment −$83.50 — **both checks silent**. A transfer between partners is not a cost.
⚠ **Never `SUM` a check column** (+50 and −50 cancel) — use `COUNTIF(U2:U1000,"<>0")`.
⚠ **Additivity holds only while the split stays 50/50 on every row.**

⚠ **`ROUND(…,6)` is REQUIRED.** Over 100,000 random rows the raw balance check is non-zero **48.2%**
of the time, worst residue **7.3e-12**; today's row cancels to 0.0 **by luck**. A real error is ~1e9×
bigger. ⚠ My first float test used `Decimal("0.67")` — **exact**, so it proved nothing; test float
behaviour with real IEEE floats.

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

## The six proved properties (`basis.py`)

Formalised as: partners `p`, weights `w_p` (sum 1); `R`=revenue, `X`=cost, `N=R−X`; `C_p` collected,
`D_p` paid, cash `A_p=C_p−D_p`; entitlement `E_p=w_p·N`; **settlement `s_p=E_p−A_p`**.

1. **Conservation** — `sum(s_p) = 0` always.
2. **Lands on share** — `A_p + s_p = E_p`.
3. **Partition** — `sum(A_p) = N`. ⭐ This is the load-bearing condition: **every revenue and every
   cost must be attributed to exactly one partner.** T2 tests precisely this.
4. **Uniqueness** — `s` is the only vector with those properties, so there is no rival "fairer" number.
5. ⭐ **Additivity** — `s` is linear in the inputs ⇒ **summing daily settlements = settling once on
   period totals.** Settle daily/weekly/monthly, identical answer. Matters for a multi-row sheet.
6. ⭐ **Invariance** — moving a cost between partners changes **neither the net nor either share**,
   only the transfer. Mis-tagging who paid cannot corrupt the P&L.

Proved for all inputs, then property-tested on **4,000 randomised cases** (profits, losses, 2/3/5
partners, exact `Fraction`). Engine formulas separately checked against the model on **3,000 more
random rows** — the step that catches a formula accidentally right at today's numbers.

⭐ **What the checks CATCH:** unattributed cost/revenue, double-attributed cost, the dropped
"+ what you paid" term — and **the residual equals the size of the error**.
⭐ **What they DO NOT catch:** a wrong split ratio that still sums to 1 (60/40 → check still 0), a
mistyped lead count or spend, and **sending the transfer the wrong way** (an execution error, not a
sheet error). Those need the eye: read the Share columns, obey the sign.

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

1. 🛑 **Half-cent: CLOSED.** Bob: *"FORGET THE HALF CENTS!!!"* Never raise rounding again.
2. **The 0.67 haircut** — confirm it's a real cost reduction already banked, not a pending rebate
   ($393.69, 33% of spend). Asked twice, not yet answered.
3. **50/50 confirmed?** Assumed throughout, matching the sheet's own halving.

## Files

`model.py` · `proof.py` · `verify_fixes.py` · `verify_formulas.py` · `verify_page.py` · `qa.py` ·
`basis.py` (the formal system + 6 theorems) · `verify_basis_sheet.py` (engine vs model, 3,000 rows) ·
`engine-block.tsv` (the paste block) · `index.html` · `paste-block.tsv` (earlier ledger, superseded) ·
`original-sheet-snapshot.csv` (first pull) · `sheet-snapshot-0808-recheck.csv/.xlsx` (post-change).

## 8 AUGUST — LANDED (Bob had pasted into the wrong file first)

⭐ **Bob applied Option B himself**, so the LIVE sheet is now CORRECT and `I4` is deleted:
`K =(B2+C2+D2)*8` · `L =(K2-I2-J2)/2-(H2-I2)` · `M =(K2-I2-J2)/2-(F2+G2-J2)`.
Verified from the raw XML that row 3 **inherits** these as *shared formulas* (`ref="L2:L3"`) — the fix
carries to new rows, it wasn't retyped. `L` is positive on both days = correct sign (Tyson receives).

**Row 3 (2026-08-08):** Dino 12 · Olivia 15 · Tyson 38 = **65 leads** · Spent **565** →
Actual **378.55** · TFN 30.
**Revenue 520 · cost 408.55 · NET +111.45 (a PROFIT) · profit +55.725 EACH · Berry pays Tyson 130.275.**
Positions: Tyson 304−378.55 = −74.55 · Berry 216−30 = +186.
⭐ **This answered the earlier ambiguity: 378 was the ACTUAL cost** (Spent 565 × 0.67), i.e. reading A.

**TWO-DAY RUNNING:** revenue 720 · cost 1,237.86 · **net −517.86 · profit −258.93 each ·
Berry owes Tyson 462.93.** ⭐ **Additivity confirmed on real data:** 332.655 + 130.275 = 462.93, and
settling once on the summed totals gives the identical figure.

⭐ **PROFIT COLUMNS — added as N and O, fitted to his CURRENT sheet** (not the v2 engine):
`N1 Profit Tyson` / `O1 Profit Berry`, both **`=(K2-I2-J2)/2`**. Touches nothing that works.
⚠ **His `L`/`M` are SETTLEMENTS, not profit** — he asked for profit and did not have it. Both new
columns are safe to `SUM` down the page (profits sum to the net; settlements sum to zero).
⚠ The v2 engine also pastes at K1 and would **overwrite** N/O — flagged on the page as an
alternative, not an addition. His current 3 formulas + N/O are correct as they stand.

⭐ **The real story of the two days: cost per lead $33.17 → $6.29.** Spend fell 1,193 → 565 while leads
rose 25 → 65. That single change turned a $629 loss into a $111 profit — not the split.
⚠ The `0.67` has now written off **$580.14** across two days and Bob has still not said whether it is
banked or a pending rebate. Asked three times.

Independent sub-agent re-derived all 13 claims (both days + cumulative + additivity): **0 discrepancies**.
