#!/usr/bin/env python3
"""Eight independent routes to the same number. If any disagree, the script dies."""
from fractions import Fraction as F
from decimal import Decimal, getcontext
getcontext().prec = 50

# ---------- raw inputs ONLY: lead counts, spend, TFN, price. Nothing computed by the sheet. ----------
DAYS = [  # date, dino, olivia, tyson_leads, spent, tfn, price
    ("7 Aug",   2,  4,  19, 1193, 30,  8),
    ("10 Aug", 26, 66, 148, 2475, 160, 9),
    ("11 Aug",  6,  2,  25,  790, 30,  9),
]
HAIRCUT  = F(67, 100)
ADVANCE  = F(500)      # Berry -> Tyson, 7 Aug
WEIGHT   = F(1, 2)     # 50/50

# every real-world cash event: (who, +in / -out, amount)
events = []
for _, dino, olivia, tl, spent, tfn, price in DAYS:
    events += [("berry", F(dino * price)), ("berry", F(olivia * price)), ("tyson", F(tl * price))]
    events += [("tyson", -F(spent) * HAIRCUT), ("berry", -F(tfn))]

revenue = sum(a for _, a in events if a > 0)
cost    = -sum(a for _, a in events if a < 0)
net     = revenue - cost

results = {}

# ---- ROUTE 1: share minus position -------------------------------------------------
pos = {"tyson": sum(a for w, a in events if w == "tyson"),
       "berry": sum(a for w, a in events if w == "berry")}
pos_after = {"tyson": pos["tyson"] + ADVANCE, "berry": pos["berry"] - ADVANCE}
results["1 share - position"] = WEIGHT * net - pos_after["tyson"]

# ---- ROUTE 2: half the gap between the two cash positions --------------------------
results["2 half the cash gap"] = (pos_after["berry"] - pos_after["tyson"]) / 2

# ---- ROUTE 3: sum of per-day settlements, then subtract the advance ----------------
daily = []
for _, dino, olivia, tl, spent, tfn, price in DAYS:
    d_rev  = F((dino + olivia + tl) * price)
    d_cost = F(spent) * HAIRCUT + F(tfn)
    daily.append(WEIGHT * (d_rev - d_cost) - (F(tl * price) - F(spent) * HAIRCUT))
results["3 daily sum - advance"] = sum(daily) - ADVANCE

# ---- ROUTE 4: the sheet's OWN engine columns (different formula path entirely) -----
# Total Rev = F+G+H ; Total Cost = I+J ; Net = TR-TC ; Profit = Net/2
# Tyson in-out = H-I ; Settlement = Profit - (Tyson in-out)
eng = F(0)
for _, dino, olivia, tl, spent, tfn, price in DAYS:
    TR = F(olivia*price) + F(dino*price) + F(tl*price)      # NOT (leads)*price
    TC = F(spent) * HAIRCUT + F(tfn)
    eng += (TR - TC) / 2 - (F(tl*price) - F(spent)*HAIRCUT)
results["4 sheet engine path"] = eng - ADVANCE

# ---- ROUTE 5: literal bank simulation, then solve for the equalising transfer ------
def simulate(x):
    """x = dollars Berry sends Tyson at the end. Returns each partner's P&L."""
    t = b = F(0)
    for who, amt in events:
        if who == "tyson": t += amt
        else:              b += amt
    t += ADVANCE; b -= ADVANCE          # the advance actually happened
    t += x;       b -= x                # the proposed final transfer
    return t, b
# Bisection converges in BINARY and can never land exactly on a rational, so it is used
# only as a convergence check; the exact value comes from the closed form it converges to.
lo, hi = F(-100000), F(100000)
for _ in range(400):
    mid = (lo + hi) / 2
    t, b = simulate(mid)
    if t - b < 0: lo = mid
    else:         hi = mid
bisected = (lo + hi) / 2
assert abs(bisected - F("502.93")) < F(1, 10**60), f"bisection converged elsewhere: {float(bisected)}"
# exact closed form: the x that makes simulate(x) return two equal halves
t0, b0 = simulate(F(0))
results["5 bank sim (equalise)"] = (b0 - t0) / 2

# ---- ROUTE 6: solve the linear equation symbolically ------------------------------
import sympy as sp
x = sp.Rational(0); X = sp.symbols('X')
T = sp.Rational(pos["tyson"].numerator, pos["tyson"].denominator) + sp.Rational(500) + X
B = sp.Rational(pos["berry"].numerator, pos["berry"].denominator) - sp.Rational(500) - X
sol = sp.solve(sp.Eq(T, B), X)[0]
results["6 sympy solve T=B"] = F(sol.p, sol.q)

# ---- ROUTE 7: double-entry ledger, capital accounts --------------------------------
# Each partner's capital account: contributions (costs paid) - drawings (revenue kept) + share of loss
cap = {}
for who in ("tyson", "berry"):
    contributed = -sum(a for w, a in events if w == who and a < 0)   # money he put in
    drawn       =  sum(a for w, a in events if w == who and a > 0)   # money he took out
    cap[who] = contributed - drawn                                   # net capital standing
cap["tyson"] -= ADVANCE; cap["berry"] += ADVANCE
# loss is shared equally, so balance the two capital accounts
results["7 capital accounts"] = (cap["tyson"] - cap["berry"]) / 2

# ---- ROUTE 8: Decimal arithmetic, wholly separate number type ----------------------
dT = Decimal(0); dB = Decimal(0)
for _, dino, olivia, tl, spent, tfn, price in DAYS:
    dB += Decimal(dino*price) + Decimal(olivia*price) - Decimal(tfn)
    dT += Decimal(tl*price) - Decimal(spent) * Decimal("0.67")
dT += Decimal(500); dB -= Decimal(500)
dec = (Decimal(dT) + Decimal(dB)) / 2 - dT     # share - position
results["8 Decimal type"] = dec

# ---------- compare ----------
print(f"revenue {float(revenue):>10,.2f}   cost {float(cost):>10,.2f}   net {float(net):>10,.2f}")
print(f"each partner bears {float(WEIGHT*net):>.3f}\n")
target = F("502.93")
for name, val in results.items():
    v = F(str(val)) if isinstance(val, Decimal) else val
    flag = "OK " if v == target else "MISMATCH"
    print(f"  {flag} route {name:24} -> {float(v):>12,.4f}")
    assert v == target, f"{name} disagrees: {v}"

# exactness: is 502.93 a clean number or is it hiding a rounding decision?
assert target == F(50293, 100), "not exact cents"
print(f"\n502.93 is EXACT: {target.numerator}/{target.denominator} = 50293/100, no rounding applied.")
print("Per-day settlements carry half-cents (332.655, 173.15) but they cancel in the total.")

# both partners land on the identical outcome
t, b = simulate(target)
assert t == b == WEIGHT * net, (t, b)
print(f"After paying: Tyson {float(t):,.2f} = Berry {float(b):,.2f} = half the net. Equalised exactly.")
print("\nALL 8 ROUTES AGREE.")
