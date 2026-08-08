#!/usr/bin/env python3
"""
ENGINE v2 — rebuilt after the adversarial design audit.

What changed and why
--------------------
1. Restored a free cost cell for EACH partner (K = Tyson other, L = Berry other).
   v1 dropped Berry's, and Bob has said more costs are coming. It also makes cost
   attribution a real recorded fact rather than something implied by a formula.
2. ONE settlement number plus a plain-English instruction cell, instead of a
   mirrored +/- pair. The mirrored pair carried zero extra information and doubled
   the surface for a sign misread - this sheet has already shipped one.
3. Honest checks. v1 claimed two checks that are ALGEBRAIC TAUTOLOGIES: with the
   formulas written correctly they are identically 0 for every possible data entry,
   so they can never catch a typo. They catch FORMULA damage, which is the real risk
   when the sheet is extended - and that is now what they are labelled as.
4. Added a revenue check computed by a DIFFERENT PATH (from lead counts, not from
   the Rev columns), so it can catch things the attribution check provably cannot.

Run:  python3 engine_v2.py
"""
import re
from fractions import Fraction as F
import random

random.seed(20260808)
PRICE = 8

ENGINE = [
    ("K", "Other cost (Tyson)", "0"),
    ("L", "Other cost (Berry)", "0"),
    ("M", "Total Rev",          "=F2+G2+H2"),
    ("N", "Total Cost",         "=I2+J2+K2+L2"),
    ("O", "Net P/L",            "=M2-N2"),
    ("P", "Share Tyson",        "=O2/2"),
    ("Q", "Share Berry",        "=O2/2"),
    ("R", "Tyson in-out",       "=H2-I2-K2"),
    ("S", "Berry in-out",       "=F2+G2-J2-L2"),
    ("T", "Settlement",         "=P2-R2"),
    ("U", "Check rev path",     "=ROUND((B2+C2+D2)*8-M2,6)"),
    ("V", "Check balance",      "=ROUND((P2+Q2)-(R2+S2),6)"),
]

# The instruction cell is text, evaluated separately.
INSTRUCTION = ('=IF(ROUND(T2,2)>0,"Berry pays Tyson "&TEXT(ROUND(T2,2),"$#,##0.00"),'
               'IF(ROUND(T2,2)<0,"Tyson pays Berry "&TEXT(-ROUND(T2,2),"$#,##0.00"),'
               '"no payment"))')


def build(b, c, d, e, j, rate=F(67, 100), overrides=None):
    """Columns A-J as the sheet already has them, then the engine. overrides
    lets us simulate damage (a hand-typed cell, a broken formula)."""
    ov = dict(overrides or {})
    cells = {"B2": F(b), "C2": F(c), "D2": F(d), "E2": F(e), "J2": F(j)}
    # input overrides must land BEFORE the derived columns, so they propagate
    for k in ("B2", "C2", "D2", "E2", "J2"):
        if k in ov:
            cells[k] = ov.pop(k)
    cells["F2"] = cells["C2"] * PRICE
    cells["G2"] = cells["B2"] * PRICE
    cells["H2"] = cells["D2"] * PRICE
    cells["I2"] = cells["E2"] * rate
    # a hand-typed override of a DERIVED cell lands after it is computed
    for k in ("F2", "G2", "H2", "I2"):
        if k in ov:
            cells[k] = ov.pop(k)

    def _round(x, n):
        q = F(10) ** int(n)
        return F(round(x * q)) / q

    for col, _label, formula in ENGINE:
        ref = col + "2"
        if ref in ov:
            cells[ref] = ov.pop(ref)
            continue
        expr = formula.lstrip("=")
        expr = re.sub(r"ROUND\(([^,]+),\s*(\d+)\)", r"_round(\1,\2)", expr)
        expr = re.sub(r"\b([A-V]2)\b", lambda m: f'c["{m.group(1)}"]', expr)
        cells[ref] = eval(expr, {"__builtins__": {}}, {"c": cells, "_round": _round})
    assert not ov, f"unused overrides {ov}"
    return cells


def instruction(t):
    # Sheets ROUND() rounds half AWAY FROM ZERO; Python's round() is banker's.
    # Use the Sheets rule so what we print matches what the cell will show.
    from decimal import Decimal, ROUND_HALF_UP
    v = float(Decimal(t.numerator) / Decimal(t.denominator)
              if hasattr(t, "numerator") else Decimal(str(t)))
    v = float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
    if v > 0:
        return f"Berry pays Tyson ${v:,.2f}"
    if v < 0:
        return f"Tyson pays Berry ${-v:,.2f}"
    return "no payment"


def main():
    print("=" * 76)
    print("ENGINE v2  (columns K-V, plus one instruction cell). A-J unchanged.")
    print("=" * 76)
    for col, label, f in ENGINE:
        print(f"  {col}2  {label:<20} {f}")
    print(f"  W2  Who pays whom     {INSTRUCTION[:58]}...")

    print("\n" + "=" * 76)
    print("1. The live row")
    print("=" * 76)
    c = build(2, 4, 19, 1193, 30)
    for col, label, _f in ENGINE:
        print(f"  {col}2  {label:<20} {float(c[col+'2']):>12.4f}")
    print(f"  W2  Who pays whom     {instruction(c['T2'])}")
    assert c["M2"] == 200 and c["N2"] == F(82931, 100) and c["O2"] == F(-62931, 100)
    assert c["P2"] == c["Q2"] == F(-62931, 200)
    assert c["T2"] == F(66531, 200)
    assert c["U2"] == 0 and c["V2"] == 0
    print("\n  net -629.31, share -314.655 each, settlement +332.655 to Tyson  CONFIRMED")

    print("\n" + "=" * 76)
    print("2. Equivalence with v1 when the new cost cells are zero")
    print("=" * 76)
    for _ in range(2000):
        b, cc, d = (random.randint(0, 300) for _ in range(3))
        e = F(random.randint(0, 40000), random.choice([1, 10, 100]))
        j = F(random.randint(0, 900), random.choice([1, 2, 10]))
        cv = build(b, cc, d, e, j)
        net = (b + cc + d) * PRICE - (e * F(67, 100) + j)
        assert cv["O2"] == net
        assert cv["T2"] == net / 2 - (d * PRICE - e * F(67, 100))
        assert cv["U2"] == 0 and cv["V2"] == 0
    print("  2,000 random rows: net, shares and settlement all match the model  PASS")

    print("\n" + "=" * 76)
    print("3. HONEST test - what the checks actually catch")
    print("=" * 76)
    base = build(2, 4, 19, 1193, 30)

    def probe(name, **kw):
        try:
            d = build(2, 4, 19, 1193, 30, **kw)
        except Exception as ex:
            print(f"  {name:<52} build error {ex}")
            return
        u, v = d["U2"], d["V2"]
        fired = "FIRES" if (u != 0 or v != 0) else "silent"
        delta = float(d["T2"] - base["T2"])
        print(f"  {name:<52} {fired:<7} settlement moves {delta:+9.3f}")
        return d

    print("\n  -- DATA errors (typing). Checks CANNOT see these: --")
    probe("Olivia's 4 leads never entered", overrides={"C2": F(0)})
    probe("spend typed 1139 instead of 1193", overrides={"E2": F(1139)})
    probe("3 leads credited to Tyson, Berry collected", overrides={"D2": F(22), "C2": F(1)})
    probe("TFN paid by Tyson but typed in J2 (Berry)", overrides={"J2": F(0), "K2": F(30)})

    print("\n  -- FORMULA / STRUCTURE damage. This is what they are for: --")
    probe("cost added to Total Cost, not attributed", overrides={"N2": base["N2"] + 125})
    probe("someone types over Rev (Olivia)", overrides={"F2": F(99)})
    probe("a share formula edited to /3", overrides={"Q2": base["O2"] / 3})
    probe("whole block pasted as static values", overrides={"T2": F(0)})

    print("\n  => The checks guard the FORMULAS. They are identically zero for every")
    print("     possible DATA entry, so a typo can never move them. Only a tie-out")
    print("     against the bank/ad-invoice can catch bad data.")

    print("\n" + "=" * 76)
    print("4. The two checks are NOT redundant (v1's pair were)")
    print("=" * 76)
    d1 = build(2, 4, 19, 1193, 30, overrides={"F2": F(99)})
    d2 = build(2, 4, 19, 1193, 30, overrides={"Q2": base["O2"] / 3})
    d3 = build(2, 4, 19, 1193, 30, overrides={"N2": base["N2"] + 125})
    print(f"  typed-over F2        -> rev-path {float(d1['U2']):+9.3f}   balance {float(d1['V2']):+9.3f}")
    print(f"  share formula /3     -> rev-path {float(d2['U2']):+9.3f}   balance {float(d2['V2']):+9.3f}")
    print(f"  cost in pool only    -> rev-path {float(d3['U2']):+9.3f}   balance {float(d3['V2']):+9.3f}")
    assert d1["U2"] != 0 and d1["V2"] == 0, "only the rev-path check sees a typed-over Rev cell"
    assert d2["V2"] != 0, "balance check must catch a damaged share formula"
    assert d3["V2"] != 0, "balance check must catch an unattributed cost"
    print("  rev-path catches what balance cannot; balance catches two distinct")
    print("  formula failures on its own  PASS")

    print("\n" + "=" * 76)
    print("5. The instruction cell removes the sign risk")
    print("=" * 76)
    for label, row in [("loss day (today)", (2, 4, 19, 1193, 30)),
                       ("profit day", (40, 40, 40, 200, 30)),
                       ("Berry owed instead", (2, 4, 19, 20, 900))]:
        cc = build(*row)
        print(f"  {label:<20} settlement {float(cc['T2']):>+10.3f}  ->  {instruction(cc['T2'])}")

    print("\n" + "=" * 76)
    print("6. Extension now needs NO formula edit at all")
    print("=" * 76)
    ext = build(2, 4, 19, 1193, 30, overrides={"L2": F(125)})
    print(f"  Berry's other cost 125 typed into L2 -> net {float(ext['O2']):.2f}, "
          f"settlement {float(ext['T2']):+.3f}, checks {float(ext['U2'])}/{float(ext['V2'])}")
    assert ext["O2"] == base["O2"] - 125
    assert ext["U2"] == 0 and ext["V2"] == 0
    tys = build(2, 4, 19, 1193, 30, overrides={"K2": F(60)})
    print(f"  Tyson's other cost 60 typed into K2  -> net {float(tys['O2']):.2f}, "
          f"settlement {float(tys['T2']):+.3f}, checks {float(tys['U2'])}/{float(tys['V2'])}")
    assert tys["O2"] == base["O2"] - 60
    print("  -> v1 required editing TWO formulas by hand and would silently mis-state")
    print("     the split if you forgot one. v2 needs only a number typed in a cell.")

    print("\n" + "=" * 76)
    print("ENGINE v2 VERIFIED")
    print("=" * 76)


if __name__ == "__main__":
    main()
