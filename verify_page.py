#!/usr/bin/env python3
"""Pull every formula off the built page and prove it against engine_v2."""
import re, html
from fractions import Fraction as F
import engine_v2 as E

page = open('index.html', encoding='utf-8').read()
blocks = [html.unescape(m) for m in re.findall(r'<pre>(.*?)</pre>', page, re.S)]
print("copy blocks:", len(blocks))
assert len(blocks) == 2, f"expected engine + instruction, got {len(blocks)}"

eng = blocks[0].strip('\n')
assert eng == open('engine-v2-block.tsv').read().rstrip('\n'), "engine block drifted from verified TSV"
rows = [r.split('\t') for r in eng.split('\n')]
assert len(rows) == 2 and all(len(r) == 12 for r in rows), [len(r) for r in rows]
print(f"  engine block byte-identical, 2x12, {eng.count(chr(9))} tabs ✓")

instr = blocks[1].strip()
assert instr == E.INSTRUCTION, "instruction cell drifted"
print("  instruction cell byte-identical ✓")

# formulas on the page must match ENGINE definition exactly
assert rows[0] == [l for _c, l, _f in E.ENGINE], "headers drifted"
assert rows[1] == [f for _c, _l, f in E.ENGINE], "formulas drifted"
print("  headers and formulas match engine_v2.ENGINE ✓")

c = E.build(2, 4, 19, 1193, 30)
want = {"M2": F(200), "N2": F(82931,100), "O2": F(-62931,100),
        "P2": F(-62931,200), "Q2": F(-62931,200),
        "R2": F(-64731,100), "S2": F(18), "T2": F(66531,200),
        "U2": F(0), "V2": F(0)}
for k, v in want.items():
    assert c[k] == v, f"{k}: {c[k]} != {v}"
print(f"  live row reproduces: net {float(c['O2'])}, settle {float(c['T2'])} ✓")
print(f"  W2 renders: {E.instruction(c['T2'])!r} ✓")

# the failure-mode numbers quoted on the page
base = c
cases = {
    "−125.000": E.build(2,4,19,1193,30, overrides={"N2": base["N2"]+125})["V2"],
    "−67.000":  E.build(2,4,19,1193,30, overrides={"F2": F(99)})["U2"],
    "+104.885": E.build(2,4,19,1193,30, overrides={"Q2": base["O2"]/3})["V2"],
}
for shown, got in cases.items():
    num = float(shown.replace("−","-").replace("+",""))
    assert float(got) == num, f"page says {shown} but engine gives {float(got)}"
print("  quoted check-fires match the engine ✓")

for lbl, ov, cost in [("Olivia 4 leads missing", {"C2":F(0)}, 16.0),
                      ("spend 1139", {"E2":F(1139)}, 18.09),
                      ("3 leads miscredited", {"D2":F(22),"C2":F(1)}, 24.0),
                      ("cost on wrong partner", {"J2":F(0),"K2":F(30)}, 30.0)]:
    d = E.build(2,4,19,1193,30, overrides=ov)
    assert d["U2"]==0 and d["V2"]==0, f"{lbl} should be silent"
    assert abs(abs(float(d["T2"]-base["T2"]))-cost) < 0.005, f"{lbl}: {float(d['T2']-base['T2'])} vs {cost}"
print("  quoted silent-error costs match the engine ✓")

# the Spent/TFN trap numbers
t = E.build(2,4,19,1193-100,30+100)
assert float(t["N2"]-base["N2"])==33.0 and float(t["P2"]-base["P2"])==-16.5
assert abs(float(t["T2"]-base["T2"])+83.5) < 1e-9 and t["U2"]==0 and t["V2"]==0
print("  Spent/TFN trap: +33 cost, −16.50 share, −83.50 payment, checks silent ✓")

for n in ["629.31","314.655","332.655","33.17","104","16.00","18.09","24.00","30.00","83.50"]:
    assert n in page, f"MISSING: {n}"
print("  all quoted numbers present ✓\nPAGE VERIFIED")

# ---------------------------------------------------- 8 August figures on the page
from fractions import Fraction as Fr
TY, AC = Fr(304), Fr(378)
net = TY - AC; prof = net/2; settle = prof - (TY - AC)
assert net == -74 and prof == -37 and settle == 37, (net, prof, settle)
for n in ["+304.00", "−378.00", "−74.00", "−37.00", "+$37.00", "253.26", "+50.74", "+$25.37", "564.18"]:
    assert n in page, f"8-Aug figure MISSING from page: {n}"
# scenario table rows
for rb, t, nt, pr in [(0,0,-74,-37),(0,30,-104,-52),(48,30,-56,-28),(160,30,56,28),(400,30,296,148)]:
    assert TY + rb - AC - t == nt, (rb, t)
    assert Fr(nt, 2) == pr, (nt, pr)
    st = pr - (TY - AC)
    assert f"${float(st):,.2f}" in page, f"scenario settlement {st} missing"
# break-even
assert AC - TY == 74 and "9 leads" in page
# the two readings really do flip direction
altc = AC * Fr(67,100); altnet = TY - altc
assert altnet > 0 and (altnet/2 - (TY-altc)) < 0, "reading B must flip the direction"
assert float(altc) == 253.26 and float(altnet) == 50.74
print("  8 August figures verified (both readings of 378) ✓")
print("  Profit columns renamed:", "Profit Tyson" in page and "Profit Berry" in page)
