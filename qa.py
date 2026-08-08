from playwright.sync_api import sync_playwright
import pathlib
url = "file://" + str(pathlib.Path("index.html").resolve())
with sync_playwright() as p:
    b = p.chromium.launch(args=["--allow-file-access-from-files"])
    for name, w, h in [("desktop",1280,900),("mobile",390,844)]:
        ctx = b.new_context(viewport={"width":w,"height":h},
                            permissions=["clipboard-read","clipboard-write"])
        pg = ctx.new_page()
        errs=[]; pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url); pg.wait_for_timeout(400)
        ow = pg.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth+1")
        pg.screenshot(path=f"qa-{name}.png", full_page=True)
        print(f"{name:8} overflow={ow}  console_errors={errs}")
        if name=="desktop":
            pg.click("#cbtn"); pg.wait_for_timeout(300)
            print("  button label after click:", pg.inner_text("#cbtn"))
            try:
                clip = pg.evaluate("navigator.clipboard.readText()")
                print("  clipboard tabs:", clip.count("\t"), "| lines:", len(clip.strip().split(chr(10))))
                print("  clipboard starts:", repr(clip[:60]))
            except Exception as e:
                print("  clipboard read unavailable:", e)
        ctx.close()
    b.close()
