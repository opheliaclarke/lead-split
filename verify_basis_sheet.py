#!/usr/bin/env python3
"""
Prove the PROPOSED SHEET FORMULAS implement basis.py's model - for random inputs,
not just the live row. This is the step that catches a formula that happens to be
right at one set of numbers and wrong everywhere else.

Run:  python3 verify_basis_sheet.py
"""
import re
import random
from fractions import Fraction as F
from decimal import Decimal as D, getcontext

import basis

getcontext().prec = 50
random.seed(20260808)

PRICE = 8

# ------------------------------------------------------- the proposed engine
# A-J are left exactly as they already are in the sheet.
ENGINE = [
    ("K", "Total Rev",       "=F2+G2+H2"),
    ("L", "Total Cost",      "=I2+J2"),
    ("M", "Net P/L",         "=K2-L2"),
    ("N", "Share Tyson",     "=M2/2"),
    ("O", "Share Berry",     "=M2/2"),
    ("P", "Cash Tyson",      "=H2-I2"),
    ("Q", "Cash Berry",      "=F2+G2-J2"),
    ("R", "Settle Tyson",    "=N2-P2"),
    ("S", "Settle Berry",    "=O2-Q2"),
    ("T", "Check attribution", "=ROUND(P2+Q2-M2,6)"),
    ("U", "Check balances",    "=ROUND(R2+S2,6)"),
]


def evaluate(bC, cC, dC, eE, jJ, rate, num=F):
    """Build columns A-J the way the sheet already does, then run the engine."""
    c = {}
    c["B2"], c["C2"], c["D2"], c["E2"], c["J2"] = num(bC), num(cC), num(dC), num(eE), num(jJ)
    c["F2"] = c["C2"] * PRICE          # Rev (Olivia)  =C2*8
    c["G2"] = c["B2"] * PRICE          # Rev (Dino)    =B2*8
    c["H2"] = c["D2"] * PRICE          # Rev (Tyson)   =D2*8
    c["I2"] = c["E2"] * num(rate)      # Actual Cost   =E2*0.67

    def _round(x, n):
        q = num(10) ** int(n)
        return num(int(x * q + (num(1, 2) if num is F else D("0.5")) * (1 if x >= 0 else -1))) / q

    for col, _label, formula in ENGINE:
        expr = formula.lstrip("=")
        expr = re.sub(r"ROUND\(([^,]+),\s*(\d+)\)", r"_round(\1,\2)", expr)
        expr = re.sub(r"\b([A-U]2)\b", lambda m: f'c["{m.group(1)}"]', expr)
        c[col + "2"] = eval(expr, {"__builtins__": {}}, {"c": c, "_round": _round})
    return c


def main():
    print("=" * 78)
    print("Proposed engine (columns K-U). Columns A-J stay exactly as they are.")
    print("=" * 78)
    for col, label, formula in ENGINE:
        print(f"  {col}2  {label:<18} {formula}")

    # ------------------------------------------------ live row, exact
    print("\n" + "=" * 78)
    print("1. The live row - engine vs model")
    print("=" * 78)
    c = evaluate(2, 4, 19, 1193, 30, F(67, 100))
    model = basis.settle(
        {"T": F(19 * PRICE), "B": F((2 + 4) * PRICE)},
        {"T": F(1193) * F(67, 100), "B": F(30)},
        {"T": F(1, 2), "B": F(1, 2)},
    )
    pairs = [("K2", model["R"]), ("L2", model["X"]), ("M2", model["N"]),
             ("N2", model["E"]["T"]), ("O2", model["E"]["B"]),
             ("P2", model["A"]["T"]), ("Q2", model["A"]["B"]),
             ("R2", model["s"]["T"]), ("S2", model["s"]["B"])]
    for cell, want in pairs:
        got = c[cell]
        flag = "OK" if got == want else "MISMATCH"
        print(f"  {cell:<3} = {float(got):>12.4f}   model {float(want):>12.4f}   {flag}")
        assert got == want, (cell, got, want)
    assert c["T2"] == 0 and c["U2"] == 0
    print(f"  T2 (attribution check) = {float(c['T2'])}      U2 (balance check) = {float(c['U2'])}")

    # ------------------------------------------------ randomised equivalence
    print("\n" + "=" * 78)
    print("2. 3,000 randomised rows - engine must equal the model every time")
    print("=" * 78)
    mix = {"profit": 0, "loss": 0}
    for _ in range(3000):
        b, cc, d = (random.randint(0, 400) for _ in range(3))
        e = F(random.randint(0, 30000), random.choice([1, 10, 100]))
        j = F(random.randint(0, 900), random.choice([1, 2, 10]))
        rate = F(random.randint(1, 100), 100)
        cells = evaluate(b, cc, d, e, j, rate)
        m = basis.settle(
            {"T": F(d * PRICE), "B": F((b + cc) * PRICE)},
            {"T": e * rate, "B": j},
            {"T": F(1, 2), "B": F(1, 2)},
        )
        mix["profit" if m["N"] > 0 else "loss"] += 1
        assert cells["K2"] == m["R"], "Total Rev"
        assert cells["L2"] == m["X"], "Total Cost"
        assert cells["M2"] == m["N"], "Net"
        assert cells["N2"] == m["E"]["T"] and cells["O2"] == m["E"]["B"], "shares"
        assert cells["P2"] == m["A"]["T"] and cells["Q2"] == m["A"]["B"], "cash"
        assert cells["R2"] == m["s"]["T"] and cells["S2"] == m["s"]["B"], "settlements"
        assert cells["R2"] + cells["S2"] == 0, "must balance"
        assert cells["P2"] + cells["Q2"] == cells["M2"], "attribution"
    print(f"  3,000/3,000 rows match exactly  ({mix['profit']} profit, {mix['loss']} loss)")
    print("  -> the engine is correct for profits as well as losses, and for any")
    print("     lead counts, any spend, any rate and any TFN value.")

    # ------------------------------------------------ float-noise robustness
    print("\n" + "=" * 78)
    print("3. Float noise - Sheets stores 1193*0.67 as 799.3100000000001")
    print("=" * 78)
    # Sheets uses IEEE-754 binary floats, so reproduce it with real floats.
    fI = 1193 * 0.67
    fK = 32.0 + 16.0 + 152.0
    fL = fI + 30.0
    fM = fK - fL
    fN = fM / 2; fO = fM / 2
    fP = 152.0 - fI; fQ = 32.0 + 16.0 - 30.0
    fR = fN - fP; fS = fO - fQ
    print(f"  1193*0.67 in floats            : {fI!r}")
    assert fI != 799.31, "float really is inexact here"
    print(f"  raw R2+S2 on TODAY's row       : {(fR + fS)!r}  <- cancels by luck, not design")

    # so measure how often it does NOT cancel, over random rows
    rnd = random.Random(7)
    nz = 0, 0
    worst = [0.0, 0.0]
    TRIALS = 100000
    for _ in range(TRIALS):
        b, cc, d = (rnd.randint(0, 500) for _ in range(3))
        e = rnd.uniform(0, 50000); j = rnd.uniform(0, 2000); rt = rnd.uniform(0.01, 1.0)
        I2 = e * rt; F2 = cc * 8.0; G2 = b * 8.0; H2 = d * 8.0
        K2 = F2 + G2 + H2; L2 = I2 + j; M2 = K2 - L2
        P2 = H2 - I2; Q2 = F2 + G2 - j
        bal = (M2 / 2 - P2) + (M2 / 2 - Q2)
        att = P2 + Q2 - M2
        nz = (nz[0] + (bal != 0.0), nz[1] + (att != 0.0))
        worst[0] = max(worst[0], abs(bal)); worst[1] = max(worst[1], abs(att))
    print(f"  over {TRIALS:,} random rows: balance non-zero {nz[0]/TRIALS:.1%} of the time, "
          f"attribution {nz[1]/TRIALS:.1%}")
    print(f"  worst residue seen: {max(worst):.2e}   (one cent is {0.01/max(worst):.1e}x bigger)")
    assert max(worst) < 1e-9, "residue must stay far below a cent"
    assert round(fR + fS, 6) == 0 and round(fP + fQ - fM, 6) == 0
    print("  -> ROUND(...,6) is REQUIRED: without it the check cell shows things like")
    print("     3.6e-12 on roughly half of all rows and looks broken.")
    print(f"  -> 6 dp tolerance (5e-7) clears the worst residue by ~{5e-7/max(worst):.0e}x,")
    print("     while any real error (cents) is still caught.")

    # ------------------------------------------------ extension rule
    print("\n" + "=" * 78)
    print("4. Adding Berry's future costs - which cells must change")
    print("=" * 78)
    print("  Put a new cost in a new column (say V2), paid by Berry. Then EXACTLY two")
    print("  cells change:   L2 -> =I2+J2+V2      Q2 -> =F2+G2-J2-V2")
    extra = F(125)
    c2 = evaluate(2, 4, 19, 1193, F(30) + extra, F(67, 100))   # same as folding it into J
    m2 = basis.settle({"T": F(152), "B": F(48)},
                      {"T": F(1193) * F(67, 100), "B": F(30) + extra},
                      {"T": F(1, 2), "B": F(1, 2)})
    assert c2["R2"] == m2["s"]["T"] and c2["S2"] == m2["s"]["B"]
    assert c2["R2"] + c2["S2"] == 0
    print(f"  simulated +{float(extra):.0f} of Berry cost -> Tyson {float(c2['R2']):+.3f}, "
          f"Berry {float(c2['S2']):+.3f}, check still 0")
    print("  -> If you add the cost to L2 but FORGET Q2, the check cell goes non-zero")
    print("     by exactly the amount you forgot. That is the whole point of it.")

    print("\n" + "=" * 78)
    print("ENGINE VERIFIED AGAINST THE MODEL ON 3,000+ INDEPENDENT CASES")
    print("=" * 78)


if __name__ == "__main__":
    main()
