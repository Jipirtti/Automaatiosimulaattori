"""PLC:n ja tikapuukaavion validointitestit A23–A29.

Odotusarvot: ohjelman toimintalogiikka (mitä tikapuukaavion pitää tehdä) sekä ajastimien ajat
asetusarvoista. Ohjelmakierto on 10 ms, joten tulon muutos näkyy ohjelmassa enintään yhden
kierron viiveellä ja ajastimen aika on asetusarvo + enintään yksi kierto.
"""
from conftest import circuit

CYCLE = 0.010


def edges(rec, label, value=True):
    return [round(t, 4) for t, v in rec[label][1:] if v == value]


def test_A23_plc_itsepito(sim, logic):
    sim.call("loadExample", "ex9"); sim.call("run", 0.1)
    logic("A23", "Lepotila: S0 (NC) antaa tulon I0.0 = 1, H2 (seis) palaa", [sim.call("plc", "PLC1")["I"][0], sim.call("active", "H2")], [True, True])
    sim.call("press", "S1", 0.1); sim.call("run", 0.2)
    logic("A23", "S1 → Q0.0 itsepito: H1 palaa käynnistyspainikkeen vapautuksen jälkeen", [sim.call("active", "H1"), sim.call("active", "H2")], [True, False])
    sim.call("press", "S0", 0.1); sim.call("run", 0.1)
    logic("A23", "S0 pysäyttää", sim.call("active", "H1"), False)
    sim.call("press", "S1", 0.1); sim.call("run", 0.1)
    i = [w["i"] for w in sim.call("wires") if w["a"] == "S0:b"][0]
    sim.call("breakWire", i, True); sim.call("run", 0.1)
    logic("A23", "Avautuva pysäytyspainike: johtimen katkeaminen pysäyttää (vikaturvallinen)", sim.call("active", "H1"), False)


def test_A24_ajastin_ton(sim, check):
    sim.call("loadExample", "ex10"); sim.call("run", 0.05)
    prog = sim.call("prog", "PLC1")
    pt1 = prog["rungs"][0]["cells"][0][7]["pt"] / 1000; pt2 = prog["rungs"][1]["cells"][0][7]["pt"] / 1000
    sim.call("click", "S1"); t0 = sim.call("time")
    rec = sim.call("record", ["H1"], 5)
    on = edges(rec, "H1")
    check("A24", f"TON: ensimmäinen vilkahdus T1 = {pt1} s kuluttua (+ tulon lukuviive 0–10 ms + 1 ms)", on[0] - t0, pt1 + CYCLE / 2 + 0.001, (CYCLE / 2 + 0.001) / (pt1 + CYCLE / 2), "s")
    check("A24", f"Vilkkujakso T1 + T2 + 2 kiertoa (ajastimien nollaus) = {pt1 + pt2 + 2 * CYCLE:.2f} s", on[2] - on[1], pt1 + pt2 + 2 * CYCLE, 0.002, "s")


def test_A25_laskuri_ctu(sim, logic):
    sim.call("loadExample", "ex10"); sim.call("run", 0.05)
    pv = sim.call("prog", "PLC1")["rungs"][3]["cells"][0][7]["pv"]
    sim.call("click", "S1")
    rec = sim.call("record", ["H1", "H2"], 7)
    on = edges(rec, "H1"); h2 = edges(rec, "H2")
    logic("A25", f"CTU: H2 syttyy {pv}. vilkahduksen nousevalla reunalla", abs(h2[0] - on[pv - 1]) <= CYCLE + 0.002, True)
    logic("A25", "Laskuri ei nollaudu itsestään", sim.call("active", "H2"), True)
    sim.call("click", "S1"); sim.call("run", 1.2)
    sim.call("press", "S2", 0.05); sim.call("run", 0.05)
    logic("A25", "Vilkku pois ja kuittaus (R C1) nollaa laskurin", [sim.call("active", "H2"), sim.call("plc", "PLC1")["C"]["1"]["cv"]], [False, 0])


def test_A26_run_stop(sim, logic):
    sim.call("loadExample", "ex9"); sim.call("run", 0.05)
    sim.call("press", "S1", 0.1); sim.call("run", 0.1)
    sim.call("click", "PLC1"); sim.call("run", 0.05)
    logic("A26", "STOP: lähdöt pois", [sim.call("active", "H1"), sim.call("active", "H2"), any(sim.call("plc", "PLC1")["Q"])], [False, False, False])
    sim.call("click", "PLC1"); sim.call("run", 0.05)
    logic("A26", "RUN: ohjelma jatkaa (itsepitobitti Q0.0 nollautui STOP-tilassa → seis-valo)", [sim.call("active", "H1"), sim.call("active", "H2")], [False, True])


def test_A27_askelketju(sim, check, logic):
    sim.call("loadExample", "ex11"); sim.call("run", 0.05)
    pt = sim.call("prog", "PLC1")["rungs"][1]["cells"][0][7]["pt"] / 1000
    sim.call("press", "S1", 0.1)
    rec = sim.call("record", ["B1", "B2", "B3", "B4"], 6)
    ev = sorted([(t, m) for lab, m in (("B2", "A+"), ("B4", "B+"), ("B1", "A−"), ("B3", "B−")) for t in edges(rec, lab)])
    logic("A27", "Askelketju: liikejärjestys A+ B+ A− B−", [m for _, m in ev], ["A+", "B+", "A−", "B−"])
    t_b2 = edges(rec, "B2")[0]; t_b3_off = edges(rec, "B3", False)[0]
    check("A27", f"Odotusaika A ulkona → B lähtee (TON {pt} s + tulon lukuviive 0–10 ms)", t_b3_off - t_b2, pt + CYCLE / 2, 0.012, "s")


def test_A28_reunaehto(sim, logic):
    sim.call("loadExample", "ex11"); sim.call("run", 0.05)
    sim.call("hold", "S1", True)
    rec = sim.call("record", ["B2"], 9)
    sim.call("hold", "S1", False)
    logic("A28", "Nouseva reuna (P): pohjassa pidetty S1 käynnistää vain yhden jakson", len(edges(rec, "B2")), 1)


def test_A29_plc_ilman_syottoa(sim, logic):
    sim.call("loadExample", "ex9"); sim.call("run", 0.05)
    sim.call("press", "S1", 0.1); sim.call("run", 0.1)
    i = [w["i"] for w in sim.call("wires") if w["b"] == "PLC1:Lp"][0]
    sim.call("breakWire", i, True); sim.call("run", 0.05)
    logic("A29", "PLC ilman syöttöä: lähdöt pois ja varoitus", [sim.call("active", "H1"), "plc_syotto" in sim.call("warningCodes")], [False, True])


def test_A30_rinnakkaishaara_ja_set_reset(sim, logic):
    rg = lambda: {"k": "", "rows": 2, "cells": [[None] * 8 for _ in range(4)], "v": [[False] * 8 for _ in range(4)]}
    r1 = rg(); r1["cells"][0][0] = {"t": "no", "a": "I0.0"}; r1["cells"][1][0] = {"t": "no", "a": "I0.1"}; r1["v"][0][1] = True
    for c in range(1, 7): r1["cells"][0][c] = {"t": "h"}
    r1["cells"][0][7] = {"t": "s", "a": "M0.0"}
    r2 = rg(); r2["rows"] = 1; r2["cells"][0][0] = {"t": "no", "a": "I0.2"}
    for c in range(1, 7): r2["cells"][0][c] = {"t": "h"}
    r2["cells"][0][7] = {"t": "r", "a": "M0.0"}
    r3 = rg(); r3["rows"] = 1; r3["cells"][0][0] = {"t": "no", "a": "M0.0"}
    for c in range(1, 7): r3["cells"][0][c] = {"t": "h"}
    r3["cells"][0][7] = {"t": "coil", "a": "Q0.0"}
    comps = [("c1", "dc", {"U": 24}, "G1"), ("c2", "plc", {"prog": {"rungs": [r1, r2, r3]}}, "PLC1"),
             ("c3", "sel", {}, "S1"), ("c4", "sel", {}, "S2"), ("c5", "sel", {}, "S3"), ("c6", "lamp", {}, "H1")]
    wires = [("c1:p", "c2:Lp"), ("c1:n", "c2:M"), ("c1:p", "c3:a"), ("c3:b", "c2:i0"), ("c1:p", "c4:a"), ("c4:b", "c2:i1"),
             ("c1:p", "c5:a"), ("c5:b", "c2:i2"), ("c2:q0", "c6:x1"), ("c6:x2", "c1:n")]
    sim.call("loadCircuit", circuit(comps, wires)); sim.call("run", 0.05)
    sim.call("click", "S2"); sim.call("run", 0.05); sim.call("click", "S2"); sim.call("run", 0.05)
    logic("A30", "Rinnakkaishaara (I0.0 TAI I0.1) asettaa M0.0:n, joka pysyy asetettuna", sim.call("active", "H1"), True)
    sim.call("click", "S3"); sim.call("run", 0.05)
    logic("A30", "Nollaus (R M0.0)", sim.call("active", "H1"), False)
