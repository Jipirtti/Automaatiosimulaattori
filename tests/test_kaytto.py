"""Käyttöliittymän testit U01–U06."""
import json


def _box(sim, cid):
    return sim.js(f"(()=>{{const r=document.querySelector('.comp[data-id=\"{cid}\"] .hit').getBoundingClientRect();return [r.x,r.y,r.width,r.height];}})()")


def _ptr(sim, kind, x, y, shift=False, target="cv"):
    el = f"document.elementFromPoint({x},{y})" if target == "pt" else "document.querySelector('#cv')"
    sim.js(f"(() => {{{el}.dispatchEvent(new PointerEvent('{kind}',{{bubbles:true,pointerId:1,button:0,pointerType:'mouse',shiftKey:{str(shift).lower()},clientX:{x},clientY:{y}}}));}})()")


def test_U01_painike_hiirella(sim):
    sim.call("loadExample", "ex1"); sim.call("pause"); sim.call("run", 0.05)
    x, y, w, h = _box(sim, "c5")          # S2: käyttölaite vasemmassa reunassa
    _ptr(sim, "pointerdown", x + 6, y + h / 2, target="pt")
    assert sim.call("state", "S2")["on"] is True, "U01: painike ei mennyt pohjaan"
    sim.call("run", 0.1)
    _ptr(sim, "pointerup", x + 6, y + h / 2)
    assert sim.call("state", "S2")["on"] is False, "U01: palautuva painike ei palautunut"
    sim.call("run", 0.1)
    assert sim.call("active", "K1") is True, "U01: itsepito ei toiminut hiirellä painettaessa"


def test_U02_hataseis_klikkaus(sim):
    sim.call("loadExample", "ex8"); sim.call("pause")
    x, y, w, h = _box(sim, "c9")
    _ptr(sim, "pointerdown", x + w / 2, y + h / 2, target="pt"); _ptr(sim, "pointerup", x + w / 2, y + h / 2)
    assert sim.call("state", "S0")["on"] is True, "U02: hätäseis ei mennyt pohjaan klikkauksesta"


def test_U03_tallennus_ja_lataus(sim):
    sim.call("loadExample", "ex7")
    s = sim.call("serialize")
    sim.call("loadCircuit", json.loads(s))
    assert sim.call("serialize") == s, "U03: tallennus ja lataus eivät tuota samaa piiriä"
    d = json.loads(s)
    assert len(d["traces"]) == 7 and d["td"]["win"] == 10


def test_U04_aikakaavioon(sim):
    sim.call("loadExample", "ex1"); sim.call("pause")
    n = len(sim.call("traces"))
    sim.js("document.querySelector('[data-tool=T]').click()")
    x, y, w, h = _box(sim, "c8")
    _ptr(sim, "pointerdown", x + w / 2, y + h / 2, target="pt"); _ptr(sim, "pointerup", x + w / 2, y + h / 2)
    assert len(sim.call("traces")) == n + 1, "U04: signaalia ei lisätty aikakaavioon"
    assert sim.js("document.querySelector('#sctl').innerText").count("K1") >= 2


def test_U05_releen_nimen_muutos_paivittaa_koskettimet(sim):
    sim.call("loadExample", "ex1"); sim.call("pause")
    x, y, w, h = _box(sim, "c7")
    _ptr(sim, "pointerdown", x + w / 2, y + h / 2, target="pt"); _ptr(sim, "pointerup", x + w / 2, y + h / 2)
    sim.js("(()=>{const i=document.querySelector('#lblIn');i.value='K9';i.dispatchEvent(new Event('change',{bubbles:true}));})()")
    labels = sim.call("labels")
    assert "K9" in labels and "K9.13" in labels and "K9.23" in labels, f"U05: {labels}"
    sim.call("press", "S2", 0.2); sim.call("run", 0.1)
    assert sim.call("active", "K9") is True


def test_U06_johtimen_katkaisu(sim):
    sim.call("loadExample", "ex1"); sim.call("pause")
    i = [w["i"] for w in sim.call("wires") if w["a"] == "S1:b"][0]
    sim.call("breakWire", i, True); sim.call("press", "S2", 0.2); sim.call("run", 0.1)
    assert sim.call("active", "K1") is False, "U06: katkennut johdin johti"
    d = json.loads(sim.call("serialize"))
    assert any(w.get("broken") for w in d["wires"])


def test_U07_tikapuueditori(sim):
    """PLC-editori: elementin lisäys työkalulla, osoitteen tarkistus, pystyyhteys, kumoa."""
    sim.call("loadExample", "ex9"); sim.call("pause"); sim.call("setTab", "plc")
    n0 = len(sim.call("prog", "PLC1")["rungs"])
    sim.js("document.querySelector('#ldAddRung').click()")
    assert len(sim.call("prog", "PLC1")["rungs"]) == n0 + 1, "U07: askelta ei lisätty"
    ri = n0

    def cell(r, c):
        sim.js(f"document.querySelector('svg.rung[data-ri=\"{ri}\"] .ldcell[data-r=\"{r}\"][data-c=\"{c}\"]').dispatchEvent(new MouseEvent('click',{{bubbles:true}}))")

    def tool(t):
        sim.js(f"document.querySelector('[data-ldt=\"{t}\"]').click()")

    def addr(a):
        sim.js(f"(()=>{{const i=document.querySelector('#ldAddr');i.value='{a}';i.dispatchEvent(new Event('change',{{bubbles:true}}));}})()")

    tool("no"); addr("I0.1"); cell(0, 0)
    tool("coil"); addr("Q0.2"); cell(0, 7)
    tool("coil"); cell(0, 3)
    assert "oikeanpuoleiseen sarakkeeseen" in sim.js("document.querySelector('#warns').innerText")
    tool("no"); addr("X9.9"); cell(0, 1)
    assert "Virheellinen osoite" in sim.js("document.querySelector('#warns').innerText")
    tool("h")
    for c in range(1, 7): cell(0, c)
    R = sim.call("prog", "PLC1")["rungs"][ri]
    assert R["cells"][0][0] == {"t": "no", "a": "I0.1"} and R["cells"][0][7] == {"t": "coil", "a": "Q0.2"}
    sim.call("press", "S1", 0.1); sim.call("run", 0.05)
    assert sim.call("plc", "PLC1")["Q"][2] is False   # S1 vapautettu → Q0.2 pois
    sim.call("hold", "S1", True); sim.call("run", 0.05)
    assert sim.call("plc", "PLC1")["Q"][2] is True, "U07: lisätty askel ei ohjaa lähtöä"
    sim.call("hold", "S1", False)
    sim.js("document.querySelector('.ldr:last-child [data-ldr=addrow]').click()")
    tool("v"); cell(0, 1)
    assert sim.call("prog", "PLC1")["rungs"][ri]["v"][0][1] is True
    sim.js("document.body.dispatchEvent(new KeyboardEvent('keydown',{key:'z',ctrlKey:true,bubbles:true}))")
    assert sim.call("prog", "PLC1")["rungs"][ri]["v"][0][1] is False, "U07: kumoa ei palauttanut ohjelmaa"


def test_U08_plc_ohjelma_tallentuu(sim):
    sim.call("loadExample", "ex11")
    s = sim.call("serialize")
    sim.call("loadCircuit", json.loads(s))
    assert sim.call("serialize") == s
    assert len(json.loads(s)["comps"][3]["p"]["prog"]["rungs"]) == 10
