#!/usr/bin/env python3
"""
Independent check of the PASTE BLOCK itself.

model.py proves the arithmetic. This proves the spreadsheet formulas we hand over
actually evaluate to that same arithmetic — by evaluating them the way Sheets
would: resolve A2..U2 references left to right, then compare against model.py.

Run:  python3 verify_formulas.py
"""
import re
from decimal import Decimal, getcontext
import model

getcontext().prec = 40
D = Decimal


def build_sheet():
    """Columns A..J exactly as they exist in Bob's sheet today (A-J untouched)."""
    leads, price = model.LEADS, D(str(model.PRICE))
    cells = {
        "A2": None,                       # date, not numeric
        "B2": D(leads["Dino"]),
        "C2": D(leads["Olivia"]),
        "D2": D(leads["Tyson"]),
        "E2": D(str(model.SPENT)),
    }
    cells["F2"] = cells["C2"] * price     # Rev (Olivia)  =C2*8
    cells["G2"] = cells["B2"] * price     # Rev (Dino)    =B2*8
    cells["H2"] = cells["D2"] * price     # Rev (Tyson)   =D2*8
    cells["I2"] = cells["E2"] * D("0.67")  # Actual Cost  =E2*0.67
    cells["J2"] = D(str(model.TFN))       # TFN Cost
    return cells


def evaluate(formula, cells):
    """Evaluate one Sheets formula string against the resolved cells."""
    f = formula.lstrip("=").replace("$", "")
    f = re.sub(r"ROUND\(([^,]+),\s*(\d+)\)", r"_round(\1,\2)", f)
    f = re.sub(r"\b([A-U]2)\b", r'cells["\1"]', f)

    def _round(x, n):
        return D(x).quantize(D(1).scaleb(-int(n)))

    return eval(f, {"__builtins__": {}}, {"cells": cells, "_round": _round, "D": D})


def main():
    cells = build_sheet()
    cols = [chr(c) for c in range(ord("K"), ord("U") + 1)]  # K..U

    print("Evaluating the paste block against the live A-J values:\n")
    for col, header, formula in zip(cols, model.HEADERS, model.FORMULAS):
        ref = f"{col}2"
        cells[ref] = evaluate(formula, cells) if formula.startswith("=") else D(formula)
        print(f"  {ref:<3} {header:<20} {formula:<16} = {cells[ref]}")

    # ------------------------------------------------ cross-check vs model.py
    r = model.compute()
    expect = {
        "L2": r["total_rev"], "M2": r["total_cost"], "N2": r["net"],
        "O2": r["tyson_share"], "P2": r["berry_share"],
        "Q2": r["tyson_cash"], "R2": r["berry_cash"],
        "S2": r["tyson_settle"], "T2": r["berry_settle"],
    }
    print("\nCross-check vs model.py (exact Fractions):")
    bad = 0
    for ref, want in expect.items():
        got = cells[ref]
        ok = got == D(want.numerator) / D(want.denominator)
        bad += not ok
        print(f"  {ref}  formula={got}   model={float(want)}   {'OK' if ok else 'MISMATCH'}")

    assert cells["U2"] == 0, f"self-check cell U2 must be 0, got {cells['U2']}"
    assert bad == 0, f"{bad} formula(s) disagree with the model"
    print("\nPASTE BLOCK VERIFIED — every formula matches the model, and U2 (check) = 0")


if __name__ == "__main__":
    main()
