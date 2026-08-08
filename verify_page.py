#!/usr/bin/env python3
"""Pull every formula and number OFF the built page and prove them independently."""
import re, html
from fractions import Fraction as F
import basis

page = open('index.html', encoding='utf-8').read()
blocks = [html.unescape(m) for m in re.findall(r'<pre>(.*?)</pre>', page, re.S)]
print("copy blocks on page:", len(blocks))

# 1) the engine block must be byte-identical to the verified generated TSV
disk = open('engine-block.tsv').read().rstrip('\n')
engine = blocks[0].strip('\n')
assert engine == disk, "PAGE ENGINE BLOCK DIFFERS FROM THE VERIFIED TSV"
rows = [r.split('\t') for r in engine.split('\n')]
assert len(rows) == 2 and all(len(r) == 11 for r in rows), f"must be 2x11, got {[len(r) for r in rows]}"
print(f"  engine block: byte-identical to engine-block.tsv, {engine.count(chr(9))} tabs, 2x11 ✓")

# 2) evaluate the engine formulas straight off the page
cells = {"B2":F(2),"C2":F(4),"D2":F(19),"E2":F(1193),"J2":F(30)}
cells["F2"]=cells["C2"]*8; cells["G2"]=cells["B2"]*8; cells["H2"]=cells["D2"]*8
cells["I2"]=cells["E2"]*F(67,100)
def _round(x,n): q=F(10)**int(n); return F(round(x*q))/q
cols = [chr(c) for c in range(ord('K'), ord('U')+1)]
for col, f in zip(cols, rows[1]):
    e = re.sub(r"ROUND\(([^,]+),\s*(\d+)\)", r"_round(\1,\2)", f.lstrip('='))
    e = re.sub(r"\b([A-U]2)\b", lambda m: f'c["{m.group(1)}"]', e)
    cells[col+"2"] = eval(e, {"__builtins__":{}}, {"c":cells,"_round":_round})

m = basis.settle({"T":F(152),"B":F(48)}, {"T":F(1193)*F(67,100),"B":F(30)},
                 {"T":F(1,2),"B":F(1,2)})
want = {"K2":m["R"],"L2":m["X"],"M2":m["N"],"N2":m["E"]["T"],"O2":m["E"]["B"],
        "P2":m["A"]["T"],"Q2":m["A"]["B"],"R2":m["s"]["T"],"S2":m["s"]["B"],
        "T2":F(0),"U2":F(0)}
for k,v in want.items():
    assert cells[k]==v, f"{k}: page gives {cells[k]}, model says {v}"
    print(f"  {k:<3} = {float(cells[k]):>11.4f}  matches model ✓")

# 3) the two extension formulas shown on the page
ext = [b.strip() for b in blocks[1:]]
assert ext == ["=I2+J2+V2", "=F2+G2-J2-V2"], f"extension formulas changed: {ext}"
c2 = dict(cells); c2["V2"]=F(125)
L = c2["I2"]+c2["J2"]+c2["V2"]; Q = c2["F2"]+c2["G2"]-c2["J2"]-c2["V2"]
M = c2["K2"]-L; P = c2["H2"]-c2["I2"]
assert (M/2-P)+(M/2-Q)==0, "extension must stay zero-sum"
assert P+Q==M, "extension must stay attributed"
print(f"  extension formulas verified (added 125 of Berry cost -> still balances) ✓")

# 4) headline numbers present
for n in ["629.31","829.31","314.655","332.655","−466.655","330","15","33.17","25.17","104","200.00"]:
    assert n in page, f"MISSING: {n}"
print("  all headline numbers present ✓")
print("\nPAGE VERIFIED")
