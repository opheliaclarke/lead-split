#!/usr/bin/env python3
"""
Single source of truth for the Tyson / Berry lead-split settlement.

Recomputes the row from raw inputs with exact arithmetic (Fraction, never float),
runs double-entry checks, and emits the exact TSV block to paste into the sheet
at cell K1.

Run:  python3 model.py
"""
from fractions import Fraction as F
import json

# ---------------------------------------------------------------- raw inputs
ROW_DATE = "7 August"
LEADS = {"Dino": 2, "Olivia": 4, "Tyson": 19}
PRICE = F(8)                 # $ per lead
SPENT = F(1193)              # gross campaign spend (column E)
RATE = F(67, 100)            # sheet's own factor: Actual Cost = Spent * 0.67
TFN = F(30)                  # TFN cost, paid by Berry
BERRY_OTHER = F(0)           # tech setup / routing / other, paid by Berry

# Who collects the cash from which buyer
TYSON_BUYERS = ["Tyson"]              # paid direct to Tyson
BERRY_BUYERS = ["Dino", "Olivia"]     # paid direct to Berry

SPLIT = F(1, 2)              # 50/50 partnership


# ------------------------------------------------------------------ compute
def compute():
    rev = {k: v * PRICE for k, v in LEADS.items()}
    actual_cost = SPENT * RATE

    tyson_in = sum(rev[b] for b in TYSON_BUYERS)
    berry_in = sum(rev[b] for b in BERRY_BUYERS)
    tyson_out = actual_cost                 # Tyson bears campaign cost
    berry_out = TFN + BERRY_OTHER           # Berry bears TFN + tech/routing

    total_rev = tyson_in + berry_in
    total_cost = tyson_out + berry_out
    net = total_rev - total_cost

    tyson_share = net * SPLIT
    berry_share = net * (1 - SPLIT)

    tyson_cash = tyson_in - tyson_out       # cash position before settling
    berry_cash = berry_in - berry_out

    tyson_settle = tyson_share - tyson_cash  # + = receives, - = pays
    berry_settle = berry_share - berry_cash

    # ------------------------------------------------------ double-entry checks
    assert tyson_in + berry_in == total_rev
    assert tyson_out + berry_out == total_cost
    assert tyson_cash + berry_cash == net, "cash positions must sum to net P/L"
    assert tyson_settle + berry_settle == 0, "settlements must net to zero"
    assert tyson_cash + tyson_settle == tyson_share, "Tyson must land on his share"
    assert berry_cash + berry_settle == berry_share, "Berry must land on his share"
    assert total_rev == sum(LEADS.values()) * PRICE, "revenue must equal leads x price"

    return dict(
        rev=rev, actual_cost=actual_cost,
        tyson_in=tyson_in, berry_in=berry_in,
        tyson_out=tyson_out, berry_out=berry_out,
        total_rev=total_rev, total_cost=total_cost, net=net,
        tyson_share=tyson_share, berry_share=berry_share,
        tyson_cash=tyson_cash, berry_cash=berry_cash,
        tyson_settle=tyson_settle, berry_settle=berry_settle,
    )


# ------------------------------------------------ the block to paste at K1
# Columns A-J of the sheet are left exactly as they are.
# This replaces the broken K/L/M and extends the row to U.
HEADERS = [
    "Berry Other Cost", "Total Rev", "Total Cost", "Net P/L",
    "Tyson Share (50%)", "Berry Share (50%)",
    "Tyson Cash", "Berry Cash",
    "Tyson Settlement", "Berry Settlement", "Check (must be 0)",
]
FORMULAS = [
    "0",                        # K  manual entry: tech setup / routing / other
    "=F2+G2+H2",                # L  Total Rev   (gross, TFN no longer buried in here)
    "=I2+J2+K2",                # M  Total Cost  (Actual Cost + TFN + Berry other)
    "=L2-M2",                   # N  Net P/L
    "=$N2/2",                   # O  Tyson 50% share
    "=$N2/2",                   # P  Berry 50% share
    "=H2-I2",                   # Q  Tyson cash in - cash out
    "=F2+G2-J2-K2",             # R  Berry cash in - cash out
    "=O2-Q2",                   # S  Tyson settlement (+ receives / - pays)
    "=P2-R2",                   # T  Berry settlement (+ receives / - pays)
    "=ROUND(S2+T2,6)",          # U  self-check, must read 0
]


def money(x):
    """Exact Fraction -> plain string, trimming trailing zeros."""
    s = f"{float(x):.6f}".rstrip("0").rstrip(".")
    return s if s not in ("-0", "") else "0"


def main():
    r = compute()

    print(f"=== {ROW_DATE} — recomputed from raw inputs (exact arithmetic) ===\n")
    print(f"  Leads              {sum(LEADS.values())}  "
          f"(Dino {LEADS['Dino']}, Olivia {LEADS['Olivia']}, Tyson {LEADS['Tyson']}) @ ${PRICE}")
    print(f"  TOTAL REVENUE      {money(r['total_rev'])}")
    print(f"  Actual Cost        {money(r['actual_cost'])}   (Spent {money(SPENT)} x {float(RATE)}) — Tyson pays")
    print(f"  TFN + other        {money(r['berry_out'])}   — Berry pays")
    print(f"  TOTAL COST         {money(r['total_cost'])}")
    print(f"  NET P/L            {money(r['net'])}   <-- LOSS\n")
    print(f"  Loss borne by Tyson  {money(r['tyson_share'])}")
    print(f"  Loss borne by Berry  {money(r['berry_share'])}\n")
    print(f"  Tyson cash position  {money(r['tyson_cash'])}  (in {money(r['tyson_in'])} - out {money(r['tyson_out'])})")
    print(f"  Berry cash position  {money(r['berry_cash'])}  (in {money(r['berry_in'])} - out {money(r['berry_out'])})\n")
    print(f"  SETTLEMENT: Berry pays Tyson {money(-r['berry_settle'])}")
    print(f"              (practical payment, 2dp: {float(-r['berry_settle']):.2f})\n")
    print("  All 7 double-entry checks PASSED\n")

    tsv = "\t".join(HEADERS) + "\n" + "\t".join(FORMULAS)
    with open("paste-block.tsv", "w") as f:
        f.write(tsv + "\n")
    print("=== paste this at cell K1 (2 rows x 11 cols) -> paste-block.tsv ===")
    print(tsv)

    with open("results.json", "w") as f:
        json.dump({k: (money(v) if isinstance(v, F) else
                       {kk: money(vv) for kk, vv in v.items()})
                   for k, v in r.items()}, f, indent=2)


if __name__ == "__main__":
    main()
