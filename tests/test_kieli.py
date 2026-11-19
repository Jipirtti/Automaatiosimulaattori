"""Kieliversioiden testit K01–K03."""
import re
from conftest import INDEX

TYPES = ["dc", "ac", "l3", "jn", "pb", "sel", "estop", "ls", "reed", "prox", "k", "kt", "y", "lamp", "kc", "km", "ol", "qm", "mot", "mot6", "cyl", "sr", "plc"]


def _click(sim, cid):
    sim.js(f"""(() => {{const g=document.querySelector('.comp[data-id="{cid}"] .hit');const r=g.getBoundingClientRect();
        const o={{bubbles:true,clientX:r.x+r.width-3,clientY:r.y+r.height-3,pointerId:1,button:0}};
        g.dispatchEvent(new PointerEvent('pointerdown',o));document.querySelector('#cv').dispatchEvent(new PointerEvent('pointerup',o));}})()""")


def test_K01_englanninkieliset_tekstit_kattavat(sim):
    sim.call("setLang", "en")
    comps = [{"id": f"c{i+1}", "type": t, "x": 120 + (i % 8) * 200, "y": 150 + (i // 8) * 200, "rot": 0, "label": f"X{i}", "p": {}} for i, t in enumerate(TYPES)]
    sim.call("loadCircuit", {"comps": comps, "wires": [], "traces": [{"target": "c11"}, {"target": "c21"}]})
    sim.call("run", 0.05)
    for i in range(1, len(TYPES) + 1):
        _click(sim, f"c{i}")
        text = sim.js("document.querySelector('#insp').innerText")
        left = [l for l in text.split("\n") if re.search("[äöÄÖ]", l)]
        assert not left, f"K01: suomea ominaisuuspaneelissa ({TYPES[i-1]}): {left[:4]}"
    body = sim.js("document.body.innerText")
    left = [l for l in body.split("\n") if re.search("[äöÄÖ]", l) and "Seinäjoki" not in l]
    assert not left, f"K01: suomenkielistä tekstiä englanninkielisessä näkymässä: {left[:5]}"
    sim.js("document.querySelector('#helpBtn').click()")
    sim.call("setTab", "plc")
    text = sim.js("document.querySelector('#plcEd').innerText")
    left = [l for l in text.split("\n") if re.search("[äöÄÖ]", l)]
    assert not left, f"K01: suomea PLC-editorissa: {left[:4]}"
    sim.call("setTab", "td")
    body = sim.js("document.querySelector('#mbox').innerText")
    left = [l for l in body.split("\n") if re.search("[äöÄÖ]", l) and "Seinäjoki" not in l]
    assert not left, f"K01: suomea ohjeikkunassa: {left[:5]}"


def test_K02_kielen_vaihto_ei_vaikuta_toimintaan(sim):
    def ajo(l):
        sim.call("setLang", l); sim.call("loadExample", "ex4"); sim.call("hold", "S1", True)
        r = sim.call("record", ["K1", "K2", "K3"], 4)
        return r
    assert ajo("fi") == ajo("en"), "K02: kieli vaikutti toimintaan"


def test_K03_url_parametri(browser):
    page = browser.new_page()
    page.goto(INDEX.as_uri() + "?lang=en")
    page.wait_for_function("window.AutSim !== undefined")
    assert page.evaluate("AutSim.lang()") == "en"
    assert page.inner_text("#runBtn") in ("Pause", "Run")
    page.goto(INDEX.as_uri() + "?lang=fi")
    page.wait_for_function("window.AutSim !== undefined")
    assert page.evaluate("AutSim.lang()") == "fi"
    page.evaluate("localStorage.clear()")
    page.close()
