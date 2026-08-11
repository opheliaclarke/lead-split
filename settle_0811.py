#!/usr/bin/env python3
"""Tyson & Berry — cumulative settlement to 11 Aug 2026, including the $500 advance.
Exact Fraction arithmetic, double-entry assertions, no floats."""
from fractions import Fraction as F

# ---- rows exactly as the live sheet computes them (formulas re-evaluated, not copied) ----
# (label, Dino, Olivia, Tyson, Spent, price, TFN)
ROWS = [
    ("7 Aug",   2,  4,  19, 1193, 8, F(30)),
    ("10 Aug", 26, 66, 148, 2475, 9, F(135)+F(25)),
    ("11 Aug",  6,  2,  25,  790, 9, F(30)),
]
HAIRCUT = F(67, 100)          # Actual Cost = Spent * 0.67
# partner-to-partner cash transfers already made (col P "Berry To Tyson", Q "Tyson To Berry")
BERRY_TO_TYSON = F(500)
TYSON_TO_BERRY = F(0)

# sheet's own displayed values, for a cross-check against our re-evaluation
SHEET = {  # label: (F, G, H, I, K, L, M, N)
    "7 Aug":  (32,  16,  152,  F("799.31"),  200, F("332.655"), F("-332.655"), F("-314.655")),
    "10 Aug": (594, 234, 1332, F("1658.25"), 2160, F("497.125"), F("-497.125"), F("170.875")),
    "11 Aug": (18,  54,  225,  F("529.3"),   297, F("173.15"),  F("-173.15"),  F("-131.15")),
}

tot_rev = tot_cost = F(0)
tyson_collected = berry_collected = F(0)
tyson_paid = berry_paid = F(0)
per_day = []

for label, dino, olivia, tyson, spent, price, tfn in ROWS:
    Fc = olivia * price          # Rev (Olivia)  -> Berry collects
    Gc = dino   * price          # Rev (Dino)    -> Berry collects
    Hc = tyson  * price          # Rev (Tyson)   -> Tyson collects
    I  = F(spent) * HAIRCUT      # Actual Cost   -> Tyson pays
    K  = (dino + olivia + tyson) * price
    assert K == Fc + Gc + Hc, f"{label}: revenue columns do not sum to Total Rev"

    net   = K - I - tfn
    share = net / 2
    s_tyson = share - (Hc - I)          # share of net - collected + paid
    s_berry = share - (Fc + Gc - tfn)
    assert s_tyson + s_berry == 0, f"{label}: settlement not zero-sum"

    sF, sG, sH, sI, sK, sL, sM, sN = SHEET[label]
    assert (Fc, Gc, Hc, I, K) == (sF, sG, sH, sI, sK), f"{label}: inputs differ from sheet"
    assert (s_tyson, s_berry, share) == (sL, sM, sN), f"{label}: settlement differs from sheet"

    tot_rev += K; tot_cost += I + tfn
    tyson_collected += Hc; berry_collected += Fc + Gc
    tyson_paid += I;       berry_paid      += tfn
    per_day.append((label, K, I + tfn, net, share, s_tyson))

# ---- cumulative, BEFORE the advance ----
net   = tot_rev - tot_cost
share = net / 2
pos_tyson = tyson_collected - tyson_paid
pos_berry = berry_collected - berry_paid
assert pos_tyson + pos_berry == net, "partition broken: a cash item is unattributed"
assert tyson_collected + berry_collected == tot_rev
assert tyson_paid + berry_paid == tot_cost

s_tyson = share - pos_tyson
s_berry = share - pos_berry
assert s_tyson + s_berry == 0
assert s_tyson == sum(d[5] for d in per_day), "additivity broken"

# ---- cumulative, AFTER the advance already paid ----
net_transfer = BERRY_TO_TYSON - TYSON_TO_BERRY      # cash that has moved Berry -> Tyson
pos_tyson_a = pos_tyson + net_transfer
pos_berry_a = pos_berry - net_transfer
assert pos_tyson_a + pos_berry_a == net, "transfer changed the pool (it must not)"
s_tyson_a = share - pos_tyson_a
s_berry_a = share - pos_berry_a
assert s_tyson_a + s_berry_a == 0
assert s_tyson_a == s_tyson - net_transfer, "advance must reduce the balance 1:1"
# each partner must land exactly on his share of the net
assert pos_tyson_a + s_tyson_a == share and pos_berry_a + s_berry_a == share

def m(x): return f"${float(x):,.2f}"
print("PER DAY".ljust(10), "revenue".rjust(10), "cost".rjust(10), "net".rjust(11), "each".rjust(11), "B->T".rjust(11))
for label, K, C, n, sh, st in per_day:
    print(label.ljust(10), m(K).rjust(10), m(C).rjust(10), m(n).rjust(11), m(sh).rjust(11), m(st).rjust(11))
print()
print("TOTAL revenue      ", m(tot_rev))
print("TOTAL cost         ", m(tot_cost), f"(actual cost {m(tyson_paid)} + TFN {m(berry_paid)})")
print("NET                ", m(net), "LOSS" if net < 0 else "PROFIT")
print("each partner's 50% ", m(share))
print()
print("Cash position (collected - paid), before the advance")
print("  Tyson  collected", m(tyson_collected), " paid", m(tyson_paid), " =", m(pos_tyson))
print("  Berry  collected", m(berry_collected), " paid", m(berry_paid), " =", m(pos_berry))
print()
print("Settlement BEFORE the advance :  Berry -> Tyson", m(s_tyson))
print("Advance already paid          :  Berry -> Tyson", m(net_transfer))
print("STILL OWED                    :  Berry -> Tyson", m(s_tyson_a))
print()
print("After that payment each partner has borne exactly", m(share))
print("  Tyson", m(pos_tyson_a), "+", m(s_tyson_a), "=", m(pos_tyson_a + s_tyson_a))
print("  Berry", m(pos_berry_a), "+", m(s_berry_a), "=", m(pos_berry_a + s_berry_a))
print()
print("day-1 check: Berry's obligation that day was", m(per_day[0][5]),
      "-> the $500 overpaid it by", m(BERRY_TO_TYSON - per_day[0][5]))
print("ALL ASSERTIONS PASSED")

# ---- proposed sheet column R: "Berry still owes" running balance ----
# R{n} = SUM($L$2:L{n}) - SUM($P$2:P{n}) + SUM($Q$2:Q{n})
L = [d[5] for d in per_day]                 # settlement per day (col L)
P = [BERRY_TO_TYSON, F(0), F(0)]            # col P, Berry -> Tyson
Q = [F(0), F(0), TYSON_TO_BERRY]            # col Q, Tyson -> Berry
running = [sum(L[:i+1]) - sum(P[:i+1]) + sum(Q[:i+1]) for i in range(3)]
assert running == [F("-167.345"), F("329.78"), F("502.93")], running
assert running[-1] == s_tyson_a, "R column must equal the settlement after the advance"
print("col R running balance:", [m(x) for x in running])

# ---- what if the deleted 8 August row were restored (65 leads @ $8, spent 565, TFN 30) ----
aug8_rev, aug8_cost = F(65*8), F(565)*HAIRCUT + F(30)
aug8_share = (aug8_rev - aug8_cost) / 2
aug8_settle = aug8_share - (F(38*8) - F(565)*HAIRCUT)
assert aug8_settle == F("130.275"), aug8_settle
restored = s_tyson_a + aug8_settle
assert restored == F("633.205"), restored
print("if 8 Aug restored     : Berry -> Tyson", m(restored))

# ---- the 0.67 haircut, three days ----
spent = F(1193 + 2475 + 790)
assert spent * HAIRCUT == tyson_paid
print("0.67 writes off       :", m(spent - tyson_paid), "of", m(spent), "spend")
print("SECOND BLOCK PASSED")

# ---- exposure if the 0.67 is a PENDING rebate, not cash already saved ----
gross_spent = F(4458)
gross_cost  = gross_spent + berry_paid          # TFN unaffected by the haircut
gross_net   = tot_rev - gross_cost
gross_share = gross_net / 2
gross_tyson = gross_share - (tyson_collected - gross_spent)
gross_after = gross_tyson - net_transfer
assert gross_share == F("-1010.5"), gross_share
assert gross_after == F("1238.5"), gross_after
print("if 0.67 is a PENDING rebate: Berry -> Tyson", m(gross_after),
      " swing", m(gross_after - s_tyson_a))
print("THIRD BLOCK PASSED")
