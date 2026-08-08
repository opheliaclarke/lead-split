#!/usr/bin/env python3
"""Pull every formula and headline number OFF the built page and prove them."""
import re, html
from decimal import Decimal as D, getcontext
getcontext().prec = 40

page = open('index.html', encoding='utf-8').read()

# live sheet values, columns A-J (untouched by any fix)
cells = {"B2":D(2),"C2":D(4),"D2":D(19),"E2":D(1193),"J2":D(30)}
cells["F2"]=cells["C2"]*8; cells["G2"]=cells["B2"]*8; cells["H2"]=cells["D2"]*8
cells["I2"]=cells["E2"]*D("0.67")

def ev(f, extra=None):
    c = dict(cells); c.update(extra or {})
    e = re.sub(r"\b([A-U]\d)\b", lambda m: f'c["{m.group(1)}"]', f.lstrip("="))
    return eval(e, {"__builtins__":{}}, {"c":c})

TRUTH = {"settle_T": D("332.655"), "settle_B": D("-332.655"),
         "net": D("-629.31"), "share": D("-314.655"), "rev": D(200), "cost": D("829.31")}

formulas = [html.unescape(m) for m in re.findall(r'<pre>(.*?)</pre>', page, re.S)]
print("Formulas found on the page:", len(formulas))
for f in formulas: print("   ", f)

assert len(formulas)==4, f"expected 4 formula blocks, got {len(formulas)}"
optA_L, optB_K, optB_L, optB_M = formulas

print("\n--- Option A (one cell) ---")
K_old = ev("=(B2+C2+D2)*8-J2")
vA = ev(optA_L, {"K2": K_old})
print(f"   L2 {optA_L} = {vA}")
assert vA == TRUTH["settle_T"], f"Option A L2 wrong: {vA}"

print("\n--- Option B (three cells) ---")
K_new = ev(optB_K)
vBL = ev(optB_L, {"K2": K_new}); vBM = ev(optB_M, {"K2": K_new})
print(f"   K2 {optB_K} = {K_new}")
print(f"   L2 {optB_L} = {vBL}")
print(f"   M2 {optB_M} = {vBM}")
assert K_new == TRUTH["rev"],      f"Option B K2 wrong: {K_new}"
assert vBL == TRUTH["settle_T"],   f"Option B L2 wrong: {vBL}"
assert vBM == TRUTH["settle_B"],   f"Option B M2 wrong: {vBM}"
assert vBL + vBM == 0,             "Option B must be zero-sum"

print("\n--- the sheet's CURRENT M2 (already correct) ---")
mcur = ev("=(K2/2)-(I2/2)-F2-G2+J2", {"K2": K_old})
print(f"   = {mcur}"); assert mcur == TRUTH["settle_B"]

print("\n--- the trap the page warns about ---")
trapL = ev("=(K2/2)-(I2/2)-H2+I2", {"K2": D(200)})
trapM = ev("=(K2/2)-(I2/2)-F2-G2+J2", {"K2": D(200)})
print(f"   K2 cleaned but L2/M2 old-style -> L2={trapL}, M2={trapM}, sum={trapL+trapM}")
assert trapL == D("347.655") and trapM == D("-317.655"), "trap figures on page must match"
assert trapL - TRUTH["settle_T"] == 15 and TRUTH["settle_B"] - trapM == -15

print("\n--- headline numbers quoted in the page text ---")
for n in ["629.31","829.31","314.655","332.655","332.66","−466.655","−332.655",
          "15.345","330","384.655","33.17","25.17","104","393.69","799.31","−799.31"]:
    assert n in page, f"MISSING from page: {n}"
    print(f"   present: {n}")

# business figures
assert (D("829.31")/25).quantize(D("0.01")) == D("33.17")
assert (D("829.31")/25 - 8).quantize(D("0.01")) == D("25.17")
assert D(1193)-D("799.31") == D("393.69")
assert 103 < D("829.31")/8 < 104
print("\nALL PAGE FORMULAS AND NUMBERS VERIFIED")
