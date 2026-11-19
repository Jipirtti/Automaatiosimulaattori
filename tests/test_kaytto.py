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
