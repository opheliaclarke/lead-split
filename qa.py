from playwright.sync_api import sync_playwright
import pathlib, sys
url = "file://" + str(pathlib.Path("index.html").resolve())
fail = 0
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h in [("desktop",1280,900),("mobile",390,844)]:
        ctx = b.new_context(viewport={"width":w,"height":h},
                            permissions=["clipboard-read","clipboard-write"])
        pg = ctx.new_page(); errs=[]
        pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(400)
        ow = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth+1")
        pg.screenshot(path=f"qa-{name}.png", full_page=True)
        print(f"{name:8} overflow={ow} console_errors={errs}")
        fail += bool(ow) + bool(errs)
        if name=="desktop":
            n = pg.locator(".copybtn").count()
            print(f"  copy buttons: {n}")
            for i in range(n):
                pg.locator(".copybtn").nth(i).click(); pg.wait_for_timeout(220)
                clip = pg.evaluate("navigator.clipboard.readText()")
                lbl  = pg.locator(".copybtn").nth(i).inner_text()
                expect = pg.locator(".copybox pre").nth(i).inner_text()
                ok = clip.strip()==expect.strip() and lbl=="Copied"
                fail += not ok
                print(f"    btn{i+1}: {'OK ' if ok else 'FAIL'} -> {clip.strip()}")
        # runtime contrast walk (composites alpha + opacity)
        if name=="desktop":
            bad = pg.evaluate("""() => {
              function srgb(c){c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4)}
              function lum(r,g,b){return .2126*srgb(r)+.7152*srgb(g)+.0722*srgb(b)}
              function parse(s){const m=s.match(/[\\d.]+/g);return m?m.map(Number):null}
              function bgOf(el){let e=el;while(e){const c=parse(getComputedStyle(e).backgroundColor);
                if(c&&(c[3]===undefined||c[3]>0.99))return c;e=e.parentElement}return [255,255,255]}
              const out=[];
              document.querySelectorAll('p,li,td,th,h1,h2,h3,b,strong,code,span,div,footer,button,pre').forEach(el=>{
                const t=[...el.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
                if(!t)return; const st=getComputedStyle(el);
                if(st.visibility==='hidden'||st.display==='none'||parseFloat(st.opacity)<0.99)return;
                const fg=parse(st.color), bg=bgOf(el); if(!fg)return;
                const a=fg[3]===undefined?1:fg[3];
                const c=[0,1,2].map(i=>Math.round(fg[i]*a+bg[i]*(1-a)));
                const L1=lum(...c),L2=lum(...bg);
                const cr=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
                const fs=parseFloat(st.fontSize), bold=parseInt(st.fontWeight)>=700;
                const need=(fs>=24||(fs>=18.66&&bold))?3:4.5;
                if(cr<need) out.push({t:el.textContent.trim().slice(0,40),cr:+cr.toFixed(2),need,fs});
              });
              return out;
            }""")
            print(f"  contrast failures: {len(bad)}")
            for x in bad[:8]: print("   ", x)
            fail += len(bad)
        ctx.close()
    b.close()
print("\nQA RESULT:", "PASS" if fail==0 else f"FAIL ({fail} issues)")
sys.exit(1 if fail else 0)
