#!/usr/bin/env python3
"""Verify BOTH candidate fixes, symbolically and numerically, before recommending either."""
import sympy as sp

B,C,D,P,E,J,rate = sp.symbols("B C D P E J rate", real=True)
I  = E*rate;  R = (B+C+D)*P;  H = D*P;  Fg = (B+C)*P
net = R-(I+J); share = net/2
setT = share-(H-I); setB = share-(Fg-J)
vals = {B:2,C:4,D:19,P:8,E:1193,rate:sp.Rational(67,100),J:30}

def check(name, K_expr, L_expr, M_expr):
    okT = sp.simplify(L_expr-setT)==0
    okM = sp.simplify(M_expr-setB)==0
    zero= sp.simplify(L_expr+M_expr)==0
    print(f"\n{name}")
    print(f"   K2 -> {float(K_expr.subs(vals)):>10.4f}   (true gross revenue is {float(R.subs(vals))})")
    print(f"   L2 -> {float(L_expr.subs(vals)):>10.4f}   == settle_Tyson? {okT}")
    print(f"   M2 -> {float(M_expr.subs(vals)):>10.4f}   == settle_Berry? {okM}")
    print(f"   L2+M2 = {float((L_expr+M_expr).subs(vals)):.10f}  zero-sum? {zero}")
    assert okT and okM and zero, f"{name} FAILED"
    return True

# OPTION A — one cell: leave K2 alone (J stays buried), just add +I2 to Tyson
Ka = R-J
check("OPTION A  (1 cell: L2 += I2; K2 and M2 untouched)",
      Ka, Ka/2-I/2-H+I, Ka/2-I/2-Fg+J)

# OPTION B — clean: K2 becomes true revenue, both partner cells read the model literally
Kb = R
check("OPTION B  (3 cells: K2 true revenue, L2/M2 rewritten)",
      Kb, (Kb-I-J)/2-(H-I), (Kb-I-J)/2-(Fg-J))

# THE TRAP — clean K2 but forget to rewrite L2/M2
Ktrap = R
Ltrap = Ktrap/2-I/2-H+I
Mtrap = Ktrap/2-I/2-Fg+J
print("\nTRAP  (K2 cleaned to 200 but L2/M2 left in the old style)")
print(f"   L2 -> {float(Ltrap.subs(vals)):>10.4f}  (should be {float(setT.subs(vals))})")
print(f"   M2 -> {float(Mtrap.subs(vals)):>10.4f}  (should be {float(setB.subs(vals))})")
print(f"   each wrong by exactly J/2 = {float((Ltrap-setT).subs(vals))}")
assert sp.simplify(Ltrap-setT)==sp.simplify(J/2), "trap magnitude must be J/2"

print("\n" + "="*66)
print("BOTH OPTIONS VERIFIED. Trap magnitude confirmed as exactly J/2 = 15.00 each.")
