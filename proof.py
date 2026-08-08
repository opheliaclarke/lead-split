#!/usr/bin/env python3
"""
Symbolic proof that the sheet's CURRENT Berry cell already equals the settlement
model, that Tyson's cell does not, and exactly what is wrong with scratch cell I4.

Symbols
  B,C,D  lead counts (Dino, Olivia, Tyson-bucket)
  P      price per lead
  E      Spent            I = E*rate   (Actual Cost, paid by Tyson)
  J      TFN Cost                       (paid by Berry)
  R = (B+C+D)*P           gross revenue billed
  H = D*P                 cash collected by Tyson
  Fg = (B+C)*P            cash collected by Berry     (R = H + Fg)

Run:  python3 proof.py
"""
import sympy as sp

B, C, D, P, E, J, rate = sp.symbols("B C D P E J rate", real=True)

I = E * rate                      # Actual Cost
R = (B + C + D) * P               # gross revenue
H = D * P                         # Tyson collects
Fg = (B + C) * P                  # Berry collects

# ---------------------------------------------------------------- the model
net = R - (I + J)                 # true net P/L
share = net / 2                   # 50/50
tyson_cash = H - I                # collected - paid
berry_cash = Fg - J
settle_tyson = share - tyson_cash
settle_berry = share - berry_cash

# ------------------------------------------------- the sheet's actual cells
K = R - J                         # K2 = (B2+C2+D2)*8-J2   "Total Rev"
L_old = K / 2 - I / 2 - H                  # L2  (Tyson)  — unchanged in the sheet
M_new = K / 2 - I / 2 - Fg + J             # M2  (Berry)  — someone added +J2
M_old = K / 2 - I / 2 - Fg                 # M2 before that edit
L_fixed = L_old + I                        # proposed fix for Tyson

print("=" * 74)
print("1. Does the sheet's CURRENT Berry cell equal settlement_Berry?")
diff_b = sp.simplify(M_new - settle_berry)
print("   M2_new - settle_Berry  =", diff_b)
print("   =>", "IDENTICAL for all inputs" if diff_b == 0 else "NOT identical")

print("\n2. Does the sheet's Tyson cell equal settlement_Tyson?")
diff_t = sp.simplify(L_old - settle_tyson)
print("   L2_old - settle_Tyson  =", sp.simplify(diff_t))
print("   =>", "identical" if diff_t == 0 else f"WRONG, short by exactly {sp.simplify(-diff_t)}")

print("\n3. Is 'L2 + I2' the correct fix for Tyson?")
diff_f = sp.simplify(L_fixed - settle_tyson)
print("   (L2+I2) - settle_Tyson =", diff_f)
print("   =>", "YES, identical for all inputs" if diff_f == 0 else "no")

print("\n4. What was Berry's cell short by BEFORE the +J2 edit?")
print("   settle_Berry - M2_old  =", sp.simplify(settle_berry - M_old))

print("\n5. Do the two fixed cells net to zero (the money must balance)?")
print("   settle_Tyson + settle_Berry =", sp.simplify(settle_tyson + settle_berry))

print("\n6. Does burying J inside 'Total Rev' change the NET result?")
net_via_K = sp.simplify(K - I)          # what you'd get treating K as revenue, I as cost
print("   (K - I) - net =", sp.simplify(net_via_K - net),
      " -> net is UNAFFECTED; only the reported revenue figure is wrong (off by -J).")

# ---------------------------------------------------------------- numbers
vals = {B: 2, C: 4, D: 19, P: 8, E: 1193, rate: sp.Rational(67, 100), J: 30}
print("\n" + "=" * 74)
print("7. At the live values:")
for name, expr in [("gross revenue R", R), ("Actual Cost I", I), ("TFN J", J),
                   ("total cost", I + J), ("net", net), ("share each", share),
                   ("Tyson cash", tyson_cash), ("Berry cash", berry_cash),
                   ("settle Tyson", settle_tyson), ("settle Berry", settle_berry),
                   ("sheet L2 (Tyson, unfixed)", L_old),
                   ("sheet M2 (Berry, current)", M_new),
                   ("sheet L2 + I2 (fixed)", L_fixed)]:
    exact = sp.nsimplify(expr.subs(vals))
    print(f"   {name:<28} {str(exact):>14}  = {float(expr.subs(vals)):>12.4f}")

# ------------------------------------------------- scratch cell I4 forensics
print("\n" + "=" * 74)
print("8. Scratch cell I4 = (830-170)/2")
I4 = sp.Rational(830 - 170, 2)
correct = ((I + J) - R).subs(vals) / 2          # loss per partner, positive form
print(f"   I4 says              {I4}")
print(f"   correct loss/partner {sp.nsimplify(correct)} = {float(correct):.4f}")
gap = sp.nsimplify(I4 - correct)
print(f"   GAP                  {gap} = {float(gap):.4f} too much, per partner")
tfn_double = sp.Rational(30, 2)                              # J counted on both sides, then halved
rounding = (sp.Rational(830) - sp.Rational(82931, 100)) / 2  # 830 vs the true 829.31, then halved
print(f"     - TFN counted twice (once as -J inside 170, once inside 830): {tfn_double}")
print(f"     - total cost 829.31 rounded up to 830:                        {rounding} = {float(rounding)}")
print(f"     - components sum:                                             {sp.nsimplify(tfn_double + rounding)}")
assert sp.simplify(tfn_double + rounding - gap) == 0, "I4 decomposition must be exact"
print("   decomposition EXACT")

assert diff_b == 0 and diff_f == 0 and sp.simplify(settle_tyson + settle_berry) == 0
print("\nALL SYMBOLIC ASSERTIONS PASSED")

# ------------------------------------------------------------------ the trap
print("\n" + "=" * 74)
print("9. TRAP: the sheet's share term only works BECAUSE J is buried in K2")
share_from_sheet = K / 2 - I / 2                     # what (K2/2)-(I2/2) really is
print("   (K2/2)-(I2/2) simplifies to:", sp.simplify(share_from_sheet))
print("   correct share is           :", sp.simplify(share))
print("   equal?", sp.simplify(share_from_sheet - share) == 0)

K_clean = R                                          # if someone 'fixes' K2 to true revenue
share_if_K_cleaned = K_clean / 2 - I / 2
print("\n   If K2 is changed to true revenue (=F2+G2+H2) but L2/M2 are left alone:")
print("     share term becomes:", sp.simplify(share_if_K_cleaned),
      " -> off by", sp.simplify(share_if_K_cleaned - share))
print(f"     numerically: {float(share_if_K_cleaned.subs(vals)):.4f} instead of "
      f"{float(share.subs(vals)):.4f}  (WRONG by {float((share_if_K_cleaned-share).subs(vals)):.4f} each)")
print("   => Do NOT clean K2 on its own. Either leave it, or move to the full ledger.")

# ------------------------------------------------- minimal one-cell fix check
print("\n" + "=" * 74)
print("10. Minimal fix: symmetric 'subtract what you collected, add what you paid'")
L_min = K / 2 - I / 2 - H + I          # =(K2/2)-(I2/2)-H2+I2
M_cur = K / 2 - I / 2 - Fg + J         # =(K2/2)-(I2/2)-F2-G2+J2   (already in the sheet)
print("   L2 =(K2/2)-(I2/2)-H2+I2      ->", float(L_min.subs(vals)),
      "| equals settle_Tyson?", sp.simplify(L_min - settle_tyson) == 0)
print("   M2 =(K2/2)-(I2/2)-F2-G2+J2   ->", float(M_cur.subs(vals)),
      "| equals settle_Berry?", sp.simplify(M_cur - settle_berry) == 0)
print("   sum:", float((L_min + M_cur).subs(vals)), "| symbolically:", sp.simplify(L_min + M_cur))
assert sp.simplify(L_min - settle_tyson) == 0
assert sp.simplify(M_cur - settle_berry) == 0
assert sp.simplify(L_min + M_cur) == 0
print("   MINIMAL FIX VERIFIED — one cell (L2) is all that is still wrong.")
