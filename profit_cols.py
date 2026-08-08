#!/usr/bin/env python3
"""
The two PROFIT columns, fitted to the sheet AS IT NOW STANDS.

Bob applied the 3-cell fix, so the live sheet is:
  A Date · B/C/D leads · E Spent · F/G/H Rev · I Actual Cost · J TFN
  K Total Rev  =(B2+C2+D2)*8
  L Tyson      =(K2-I2-J2)/2-(H2-I2)     <- SETTLEMENT (cash that moves)
  M Berry      =(K2-I2-J2)/2-(F2+G2-J2)  <- SETTLEMENT

L and M are settlements, NOT profit. Profit is the half-of-net term inside them.
So the profit columns are two new cells that touch nothing that already works.

  N Profit Tyson  =(K2-I2-J2)/2
  O Profit Berry  =(K2-I2-J2)/2

Run:  python3 profit_cols.py
"""
import re
from fractions import Fraction as F

PROFIT = [("N", "Profit Tyson", "=(K2-I2-J2)/2"),
          ("O", "Profit Berry", "=(K2-I2-J2)/2")]

ROWS = {
    "7 August": dict(B=2,  C=4,  D=19, E=1193, J=30),
    "8 August": dict(B=12, C=15, D=38, E=565,  J=30),
}


def sheet_row(B, C, D, E, J, rate=F(67, 100)):
    c = {"B2": F(B), "C2": F(C), "D2": F(D), "E2": F(E), "J2": F(J)}
    c["F2"] = c["C2"] * 8
    c["G2"] = c["B2"] * 8
    c["H2"] = c["D2"] * 8
    c["I2"] = c["E2"] * rate
    c["K2"] = (c["B2"] + c["C2"] + c["D2"]) * 8
    c["L2"] = (c["K2"] - c["I2"] - c["J2"]) / 2 - (c["H2"] - c["I2"])
    c["M2"] = (c["K2"] - c["I2"] - c["J2"]) / 2 - (c["F2"] + c["G2"] - c["J2"])
    for col, _lab, f in PROFIT:
        expr = re.sub(r"\b([A-O]2)\b", lambda m: f'c["{m.group(1)}"]', f.lstrip("="))
        c[col + "2"] = eval(expr, {"__builtins__": {}}, {"c": c})
    return c


def main():
    print("New columns to add (nothing existing is touched):")
    for col, lab, f in PROFIT:
        print(f"  {col}1  {lab:<14} {col}2  {f}")

    print("\n" + "=" * 72)
    tot = {}
    for name, v in ROWS.items():
        c = sheet_row(**v)
        net = c["K2"] - c["I2"] - c["J2"]
        print(f"\n{name}")
        print(f"  K Total Rev      {float(c['K2']):>10.2f}")
        print(f"  I Actual Cost    {float(c['I2']):>10.2f}   J TFN {float(c['J2']):>6.2f}")
        print(f"  Net P/L          {float(net):>10.2f}   {'PROFIT' if net > 0 else 'LOSS'}")
        print(f"  N Profit Tyson   {float(c['N2']):>10.3f}")
        print(f"  O Profit Berry   {float(c['O2']):>10.3f}")
        print(f"  L Settlement Tys {float(c['L2']):>10.3f}   M Settlement Ber {float(c['M2']):>10.3f}")
        # invariants
        assert c["N2"] == c["O2"] == net / 2, "profit must be half the net"
        assert c["N2"] + c["O2"] == net, "profits must sum to the net"
        assert c["L2"] + c["M2"] == 0, "settlements must net to zero"
        posT = c["H2"] - c["I2"]
        posB = c["F2"] + c["G2"] - c["J2"]
        assert posT + posB == net, "positions must sum to the net"
        assert posT + c["L2"] == c["N2"], "Tyson must land on his profit"
        assert posB + c["M2"] == c["O2"], "Berry must land on his profit"
        for k in ("K2", "I2", "L2", "M2", "N2", "O2"):
            tot[k] = tot.get(k, F(0)) + c[k]
        tot["net"] = tot.get("net", F(0)) + net
        tot["posT"] = tot.get("posT", F(0)) + posT
        tot["posB"] = tot.get("posB", F(0)) + posB

    print("\n" + "=" * 72)
    print("BOTH DAYS")
    print("=" * 72)
    print(f"  Revenue {float(tot['K2']):>10.2f}   Cost {float(tot['I2'] + 60):>10.2f}"
          f"   Net {float(tot['net']):>10.2f}")
    print(f"  Profit Tyson {float(tot['N2']):>9.3f}   Profit Berry {float(tot['O2']):>9.3f}")
    print(f"  Settlement so far: Berry owes Tyson {float(tot['L2']):.3f}")
    assert tot["N2"] + tot["O2"] == tot["net"]
    assert tot["L2"] + tot["M2"] == 0
    assert tot["posT"] + tot["L2"] == tot["N2"]
    assert tot["posT"] + tot["posB"] == tot["net"]
    print("\n  Column totals are safe to SUM: profits add to the net, settlements to zero,")
    print("  and the running settlement equals the sum of the daily ones.")
    print("\nALL CHECKS PASSED")


if __name__ == "__main__":
    main()
