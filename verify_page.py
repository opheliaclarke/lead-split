#!/usr/bin/env python3
"""Pull every formula and number OFF the built page and prove them from raw inputs."""
import re, html
from fractions import Fraction as F
import engine_v2 as E
import profit_cols as PC

page = open('index.html', encoding='utf-8').read()
blocks = [html.unescape(m).strip('\n') for m in re.findall(r'<pre>(.*?)</pre>', page, re.S)]
print("copy blocks:", len(blocks))
assert len(blocks) == 3, [b[:40] for b in blocks]
profit_blk, engine_blk, instr_blk = blocks

# ---------------------------------------------------------- 1. profit columns
rows = [r.split('\t') for r in profit_blk.split('\n')]
assert rows[0] == ["Profit Tyson", "Profit Berry"], rows[0]
assert rows[1] == [f for _c, _l, f in PC.PROFIT], rows[1]
print(f"  profit block: {rows[0]} / {rows[1]} ✓")

# ---------------------------------------------------------- 2. engine + instruction
assert engine_blk == open('engine-v2-block.tsv').read().rstrip('\n'), "engine drifted"
assert instr_blk == E.INSTRUCTION, "instruction drifted"
print("  engine + instruction blocks byte-identical ✓")

# ------------------------------------------- 3. both live rows, from raw inputs
want = {
    "7 August": dict(net=F(-62931,100), prof=F(-62931,200), setl=F(66531,200),
                     rev=F(200), cost=F(82931,100)),
    "8 August": dict(net=F(11145,100),  prof=F(11145,200),  setl=F(130275,1000),
                     rev=F(520), cost=F(40855,100)),
}
tot = {"net": F(0), "setl": F(0)}
for name, v in PC.ROWS.items():
    c = PC.sheet_row(**v)
    net = c["K2"] - c["I2"] - c["J2"]
    w = want[name]
    assert net == w["net"], (name, net)
    assert c["N2"] == c["O2"] == w["prof"], (name, c["N2"])
    assert c["L2"] == w["setl"] and c["M2"] == -w["setl"], (name, c["L2"])
    assert c["K2"] == w["rev"] and c["I2"] + c["J2"] == w["cost"]
    tot["net"] += net; tot["setl"] += c["L2"]
    print(f"  {name}: net {float(net):>9.2f}  profit each {float(c['N2']):>9.3f}  "
          f"settle {float(c['L2']):>9.3f} ✓")

assert tot["net"] == F(-51786,100) and tot["setl"] == F(46293,100)
print(f"  two-day: net {float(tot['net'])}, profit each {float(tot['net']/2)}, "
      f"Berry owes Tyson {float(tot['setl'])} ✓")

# ---------------------------------------------------------- 4. quoted numbers
for n in ["520.00","378.55","408.55","+111.45","55.725","130.275","−74.55","+186.00",
          "462.93","−258.93","517.86","−629.31","332.655","$33.17","$6.29","580.14",
          "304.00","120.00","96.00","216.00"]:
    assert n in page, f"MISSING from page: {n}"
print("  all quoted figures present ✓")

# cost-per-lead claims
assert abs(float(F(82931,100)/25) - 33.17) < 0.005
assert abs(float(F(40855,100)/65) - 6.29) < 0.005
assert float((F(1193)+F(565))*(1-F(67,100))) == 580.14
print("  cost-per-lead 33.17 -> 6.29 and the 580.14 write-off verified ✓")

# no stale claims left
for stale in ["One cell in your sheet is still wrong", "What is still wrong in the sheet right now",
              "row 3 is empty", "isn't there"]:
    assert stale not in page, f"STALE TEXT still on page: {stale}"
print("  no stale 'still wrong' / 'row 3 empty' text ✓")
print("\nPAGE VERIFIED")
