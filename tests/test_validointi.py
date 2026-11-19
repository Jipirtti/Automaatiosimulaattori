"""Toimintalogiikan validointitestit A01–A22.

Odotusarvot tulevat kytkentäkaaviosta (mitä releen, ajastimen tai turvareleen pitää tehdä) tai
käsinlaskusta komponenttien parametreista (ajat, lämpöreleen laukeamisaika). Testi ei käytä
simulaattorin omia välituloksia odotusarvona, paitsi lämpömallin alkutilaa h0, joka luetaan
ennen ylikuorman alkua ja syötetään kaavaan.
"""
import json
import math
from conftest import circuit

TAU = 100.0        # lämpömallin aikavakio (s), dokumentoitu VALIDOINTI.md:ssä
H_TRIP = 1.2 ** 2  # laukeaa, kun lämpenemä saavuttaa pysyvän tilan arvon virralla 1,2·Ir


def t_trip(r, h0=0.0):
    """Lämpöreleen laukeamisaika virtasuhteella r = I/Ir: h(t) = r² + (h0 − r²)·e^(−t/τ) = 1,44."""
    return -TAU * math.log((r * r - H_TRIP) / (r * r - h0))


def edges(rec, label):
    return [round(t, 4) for t, _ in rec[label][1:]]


# ---------- releet ja ajastimet ----------

def test_A01_itsepito(sim, logic):
    sim.call("loadExample", "ex1"); sim.call("run", 0.05)
    sim.call("press", "S2", 0.2); sim.call("run", 0.5)
    logic("A01", "Itsepito: K1 jää vetäneeksi, kun käynnistyspainike S2 vapautetaan", sim.call("active", "K1"), True)
    logic("A01", "Itsepito: merkkilamppu H1 palaa K1:n koskettimen 23–24 kautta", sim.call("active", "H1"), True)
    sim.call("press", "S1", 0.2); sim.call("run", 0.5)
    logic("A01", "Itsepito: pysäytyspainike S1 (NC) katkaisee pidon", sim.call("active", "K1"), False)


def test_A02_releen_ja_kontaktorin_vetoaika(sim, check):
    sim.call("loadExample", "ex1"); sim.call("run", 0.05)
    t0 = sim.call("time"); sim.call("hold", "S2", True)
    t = sim.call("runUntil", "K1", 1)
    check("A02", "Apureleen vetoaika (kelan ohjauksesta koskettimien vaihtoon)", t - t0, 0.010, 0.11, "s")
    sim.call("loadExample", "ex2"); sim.call("run", 0.05)
    t0 = sim.call("time"); sim.call("hold", "S1", True)
    t = sim.call("runUntil", "K1", 1)
    check("A02", "Kontaktorin vetoaika", t - t0, 0.025, 0.05, "s")


def test_A03_vetoviive(sim, check, logic):
    sim.call("loadExample", "ex5"); sim.call("run", 0.05)
    T = sim.call("param", "KT1")["T"]
    sim.call("click", "S1"); t0 = sim.call("time")
    rec = sim.call("record", ["KT1", "H1"], T + 1)
    check("A03", f"Vetoviive: KT1:n kosketin sulkeutuu ajan T = {T} s kuluttua ohjauksesta", edges(rec, "KT1")[0] - t0, T, 0.002, "s")
    sim.call("click", "S1"); sim.call("run", 0.05)
    logic("A03", "Vetoviive: ohjauksen poisto avaa koskettimen heti", sim.call("active", "KT1"), False)


def test_A04_paastoviive(sim, check, logic):
    sim.call("loadExample", "ex5"); sim.call("run", 0.05)
    T = sim.call("param", "KT2")["T"]
    sim.call("click", "S2"); sim.call("run", 0.01)
    logic("A04", "Päästöviive: kosketin sulkeutuu heti ohjauksesta", sim.call("active", "KT2"), True)
    sim.call("run", 0.5); sim.call("click", "S2"); t0 = sim.call("time")
    rec = sim.call("record", ["KT2"], T + 1)
    check("A04", f"Päästöviive: kosketin aukeaa ajan T = {T} s kuluttua ohjauksen poistosta", edges(rec, "KT2")[0] - t0, T, 0.002, "s")


def test_A05_ristiinlukitus_ja_suunnanvaihto(sim, logic):
    sim.call("loadExample", "ex3"); sim.call("run", 0.05)
    sim.call("press", "S1", 0.2); sim.call("run", 1.0)
    logic("A05", "Suunnanvaihto: S1 → K1, moottori myötäpäivään (L1–L2–L3 → U–V–W)", sim.call("state", "M1")["dir"], 1)
    sim.call("press", "S2", 0.2); sim.call("run", 0.2)
    logic("A05", "Ristiinlukitus: S2 ei vedä K2:ta, kun K1 on vetänyt (K1 21–22 auki)", sim.call("active", "K2"), False)
    sim.call("press", "S0", 0.2); sim.call("press", "S2", 0.2); sim.call("run", 2.5)
    logic("A05", "Suunnanvaihto: S0 ja S2 → K2, L1 ja L3 vaihdettu → moottori vastapäivään", sim.call("state", "M1")["dir"], -1)
    logic("A05", "Ristiinlukitus: K1 ei vedä K2:n aikana", sim.call("active", "K1"), False)


def test_A06_tahti_kolmio(sim, check, logic):
    sim.call("loadExample", "ex4"); sim.call("run", 0.05)
    T = sim.call("param", "KT1")["T"]
    sim.call("hold", "S1", True); t0 = sim.call("time")
    rec = sim.call("record", ["K1", "K2", "K3"], 0.3)
    sim.call("hold", "S1", False)
    logic("A06", "Tähti–kolmio: käynnistyksessä tähti (M1 kytkentä Y)", sim.call("state", "M1")["conn"], "Y")
    rec2 = sim.call("record", ["K2", "K3"], T + 1)
    t_k2_off = edges(rec2, "K2")[0]; t_k3_on = edges(rec2, "K3")[0]
    check("A06", f"Tähtiaika: K2 päästää ajan T = {T} s (+ kontaktorin päästöaika 25 ms) kuluttua", t_k2_off - t0, T + 0.025, 0.003, "s")
    logic("A06", "Tähti- ja kolmiokontaktori eivät ole yhtä aikaa vetäneinä (K3 vetää vasta K2:n päästettyä)", t_k3_on > t_k2_off, True)
    check("A06", "Kytkentätauko K2 auki → K3 kiinni (K2 21–22 + kontaktorin vetoaika)", t_k3_on - t_k2_off, 0.025, 0.08, "s")
    sim.call("run", 1)
    logic("A06", "Tähti–kolmio: käynnistyksen jälkeen kolmio (M1 kytkentä Δ)", sim.call("state", "M1")["conn"], "D")


# ---------- suojalaitteet ----------

def test_A07_lampoorele_ylikuorma(sim, check, logic):
    sim.call("loadExample", "ex2"); sim.call("run", 0.05)
    sim.call("press", "S1", 0.2); sim.call("run", 2)
    In, Ir = sim.call("param", "M1")["In"], sim.call("param", "F1")["Ir"]
    sim.call("setParam", "M1", "kuorma", "ylikuorma")
    h0 = sim.call("state", "F1")["h"]; t0 = sim.call("time")
    t = sim.call("runUntil", "F1", 200)
    r = 2 * In / Ir
    check("A07", f"Lämpöreleen laukeamisaika, I = {r:.1f}·Ir (τ = 100 s, alkulämpö h0 = {h0:.3f})", t - t0, t_trip(r, h0), 0.005, "s")
    sim.call("run", 0.1)
    logic("A07", "Laukeaminen: 95–96 aukeaa → K1 päästää, 97–98 sulkeutuu → vikalamppu H2 palaa", [sim.call("active", "K1"), sim.call("active", "H2")], [False, True])
    sim.call("click", "F1")
    logic("A07", "Palautusta ei hyväksytä heti laukeamisen jälkeen (rele kuuma)", sim.call("active", "F1"), True)


def test_A08_jumittunut_akseli(sim, check):
    sim.call("loadExample", "ex2"); sim.call("run", 0.05)
    sim.call("setParam", "M1", "kuorma", "jumissa")
    In, Ir = sim.call("param", "M1")["In"], sim.call("param", "F1")["Ir"]
    sim.call("hold", "S1", True); sim.call("run", 0.2); sim.call("hold", "S1", False)
    check("A08", "Jumittuneen moottorin virta = käynnistysvirta 6·In", sim.call("state", "M1")["I"], 6 * In, 0.001, "A")
    t = sim.call("runUntil", "F1", 30)
    check("A08", "Lämpöreleen laukeamisaika jumittuneella akselilla (I = 6·Ir)", t, 0.05 + 0.001 + 0.025 + t_trip(6 * In / Ir), 0.01, "s")


def test_A09_puuttuva_vaihe(sim, check, logic):
    sim.call("loadExample", "ex2"); sim.call("run", 0.05)
    i = [w["i"] for w in sim.call("wires") if w["a"] == "G1:L3"][0]
    sim.call("breakWire", i, True)
    sim.call("hold", "S1", True); sim.call("run", 0.2); sim.call("hold", "S1", False)
    logic("A09", "Kaksivaihekäyttö: moottori ei käynnisty", round(sim.call("state", "M1")["n"]), 0)
    logic("A09", "Kaksivaihekäyttö: varoitus", "kaksivaihe" in sim.call("warningCodes"), True)
    In, Ir = sim.call("param", "M1")["In"], sim.call("param", "F1")["Ir"]
    t = sim.call("runUntil", "F1", 30)
    check("A09", "Lämpöreleen laukeamisaika pysähdyksissä kahdella vaiheella (I = 5·In)", t, 0.05 + 0.001 + 0.025 + t_trip(5 * In / Ir), 0.01, "s")


def test_A10_oikosulku_ohjauspiirissa(sim, logic):
    c = circuit([("c1", "dc", {"U": 24}, "G1"), ("c2", "sel", {"kosk": "NO"}, "S1"), ("c3", "k", {}, "K1")],
                [("c1:p", "c2:a"), ("c2:b", "c1:n"), ("c1:p", "c3:a1"), ("c3:a2", "c1:n")])
    sim.call("loadCircuit", c); sim.call("run", 0.1)
    logic("A10", "Ennen oikosulkua kela vetää", sim.call("active", "K1"), True)
    sim.call("click", "S1"); sim.call("run", 0.1)
    logic("A10", "Oikosulku (+ ja 0 V samassa solmussa): teholähde laukeaa ja K1 päästää",
          [sim.call("state", "G1")["trip"], sim.call("active", "K1"), "oikosulku" in sim.call("warningCodes")], [True, False, True])
    sim.call("click", "S1"); sim.call("click", "G1"); sim.call("run", 0.1)
    logic("A10", "Vian poiston ja kuittauksen jälkeen piiri toimii", sim.call("active", "K1"), True)


def test_A11_oikosulku_paapiirissa(sim, logic):
    c = circuit([("c1", "l3", {}, "G1"), ("c2", "qm", {"Ir": 5}, "Q1"), ("c3", "sel", {"kosk": "NO"}, "S1")],
                [("c1:L1", "c2:1"), ("c1:L2", "c2:3"), ("c1:L3", "c2:5"), ("c2:2", "c3:a"), ("c3:b", "c2:4")])
    sim.call("loadCircuit", c); sim.call("run", 0.05)
    sim.call("click", "S1"); sim.call("run", 0.05)
    logic("A11", "Vaiheiden välinen oikosulku moottorinsuojakytkimen jälkeen: Q1 laukeaa, syöttö ei",
          [sim.call("state", "Q1")["on"], sim.call("state", "Q1")["trip"], sim.call("state", "G1")["trip"], "qm_oikosulku" in sim.call("warningCodes")], [False, True, False, True])


# ---------- moottorin kytkennät ----------

def test_A12_tahtipiste_puuttuu(sim, logic):
    c = circuit([("c1", "l3", {}, "G1"), ("c2", "mot6", {}, "M1")],
                [("c1:L1", "c2:U1"), ("c1:L2", "c2:V1"), ("c1:L3", "c2:W1")])
    sim.call("loadCircuit", c); sim.call("run", 1)
    logic("A12", "Käämien toiset päät kytkemättä: moottori ei pyöri ja varoitus tähtipisteestä",
          [round(sim.call("state", "M1")["n"]), "tahtipiste" in sim.call("warningCodes")], [0, True])


def test_A13_kolmiokytkenta_ja_suunta(sim, logic):
    delta = [("c1:L1", "c2:U1"), ("c1:L2", "c2:V1"), ("c1:L3", "c2:W1"), ("c1:L1", "c2:W2"), ("c1:L2", "c2:U2"), ("c1:L3", "c2:V2")]
    c = circuit([("c1", "l3", {}, "G1"), ("c2", "mot6", {}, "M1")], delta)
    sim.call("loadCircuit", c); sim.call("run", 1)
    s = sim.call("state", "M1")
    logic("A13", "Kolmio U1–W2, V1–U2, W1–V2: kytkentä Δ, myötäpäivään", [s["conn"], s["dir"]], ["D", 1])
    c = circuit([("c1", "l3", {}, "G1"), ("c2", "mot", {}, "M1")], [("c1:L2", "c2:U1"), ("c1:L1", "c2:V1"), ("c1:L3", "c2:W1")])
    sim.call("loadCircuit", c); sim.call("run", 1)
    logic("A13", "Kahden vaiheen vaihto (L2–L1–L3): moottori vastapäivään", sim.call("state", "M1")["dir"], -1)


# ---------- sähköpneumatiikka ----------

def test_A14_sylinterin_liikeaika(sim, check, logic):
    sim.call("loadExample", "ex6"); sim.call("run", 0.05)
    tout, tin = sim.call("param", "A1")["tout"], sim.call("param", "A1")["tin"]
    sim.call("hold", "S1", True); t0 = sim.call("time")
    rec = sim.call("record", ["Y1", "B2", "B1"], 0.2); sim.call("hold", "S1", False)
    rec2 = sim.call("record", ["Y1", "B2", "B1", "K1"], tout + tin + 1)
    t_y1 = edges(rec, "Y1")[0]; t_b2 = edges(rec2, "B2")[0]
    check("A14", f"Liike ulos: Y1:n ohjauksesta etuasennon anturiin B2 (liikeaika {tout} s)", t_b2 - t_y1, tout, 0.002, "s")
    t_k1_off = edges(rec2, "K1")[0]; t_b1 = edges(rec2, "B1")[0]
    check("A14", f"Liike sisään: K1:n päästöstä taka-asennon anturiin B1 (liikeaika {tin} s)", t_b1 - t_k1_off, tin, 0.003, "s")
    logic("A14", "Automaattinen paluu: B2 → K2 → K1 päästää (K2 21–22)", t_k1_off > t_b2, True)


def test_A15_sekvenssi(sim, check, logic):
    sim.call("loadExample", "ex7"); sim.call("run", 0.05)
    p = [sim.call("param", x) for x in ("A", "B")]
    sim.call("hold", "S1", True); t0 = sim.call("time")
    rec = sim.call("record", ["B1", "B2", "B3", "B4"], 0.1); sim.call("hold", "S1", False)
    rec2 = sim.call("record", ["B1", "B2", "B3", "B4"], 6)
    ev = []
    for lab, mean in (("B2", "A+"), ("B4", "B+"), ("B1", "A−"), ("B3", "B−")):
        for t, v in rec2[lab][1:]:
            if v: ev.append((t, mean))
    ev.sort()
    logic("A15", "Liikejärjestys anturien mukaan", [m for _, m in ev], ["A+", "B+", "A−", "B−"])
    check("A15", "Jakson kesto = A+ + B+ + A− + B− liikeajat", ev[-1][0] - t0, p[0]["tout"] + p[1]["tout"] + p[0]["tin"] + p[1]["tin"], 0.005, "s")


# ---------- turvallisuus ----------

def _ex8_running(sim):
    sim.call("loadExample", "ex8"); sim.call("run", 0.05)
    sim.call("press", "S1", 0.2); sim.call("run", 1.0)


def test_A16_hataseis(sim, logic):
    _ex8_running(sim)
    logic("A16", "Kuittauksen (S1, laskeva reuna) jälkeen K0:n lähdöt, K1, K2 ja moottori päällä",
          [sim.call("active", "K0"), sim.call("active", "K1"), sim.call("active", "K2"), sim.call("state", "M1")["dir"]], [True, True, True, 1])
    sim.call("click", "S0"); sim.call("run", 0.05)
    logic("A16", "Hätäseis: K0:n lähdöt aukeavat ja K1, K2 päästävät", [sim.call("active", "K0"), sim.call("active", "K1"), sim.call("active", "K2")], [False, False, False])
    sim.call("click", "S0"); sim.call("run", 0.5)
    logic("A16", "Hätäseisin vapautus ei käynnistä uudelleen (valvottu kuittaus)", sim.call("active", "K0"), False)
    sim.call("hold", "S1", True); sim.call("run", 0.2)
    logic("A16", "Kuittaus ei toimi painettaessa, vaan vasta vapautuksessa (laskeva reuna)", sim.call("active", "K0"), False)
    sim.call("hold", "S1", False); sim.call("run", 0.1)
    logic("A16", "Kuittauspainikkeen vapautus käynnistää", sim.call("active", "K0"), True)


def test_A17_kanavavika(sim, logic):
    _ex8_running(sim)
    sim.call("setParam", "S0", "vika", "k2")
    sim.call("click", "S0"); sim.call("run", 0.05)
    logic("A17", "Kanava 2 hitsautunut: hätäseis pysäyttää kanavan 1 kautta", sim.call("active", "K0"), False)
    sim.call("click", "S0"); sim.call("press", "S1", 0.2); sim.call("run", 0.3)
    logic("A17", "Kanavat eriävät: uudelleenkäynnistys estyy ja varoitus", [sim.call("active", "K0"), sim.call("state", "K0")["lock"], "turvarele" in sim.call("warningCodes")], [False, "erivat", True])


def test_A18_takaisinkytkenta(sim, logic):
    _ex8_running(sim)
    sim.call("setParam", "K1.1", "vika", "p1")
    sim.call("click", "S0"); sim.call("run", 0.1)
    logic("A18", "K1:n pääkosketin hitsautunut: K2 katkaisee moottorin (kaksi kontaktoria sarjassa)", sim.call("state", "M1")["mode"], "off")
    sim.call("click", "S0"); sim.call("press", "S1", 0.2); sim.call("run", 0.3)
    logic("A18", "Takaisinkytkentä: K1:n peilikosketin 21–22 jää auki → kuittaus ei käynnistä", sim.call("active", "K0"), False)


def test_A19_kanavien_oikosulku(sim, logic):
    _ex8_running(sim)
    d = json.loads(sim.call("serialize"))
    d["wires"].append({"a": "c10:S12", "b": "c10:S22"})
    sim.call("loadCircuit", d); sim.call("run", 0.05); sim.call("press", "S1", 0.2); sim.call("run", 0.3)
    logic("A19", "Kanavien välinen oikosulku (S12–S22): lähdöt eivät kytkeydy", [sim.call("active", "K0"), sim.call("state", "K0")["lock"]], [False, "ristikko"])


# ---------- kuormat ja anturit ----------

def test_A20_kuorman_jannite(sim, logic):
    c = circuit([("c1", "dc", {"U": 24}, "G1"), ("c2", "k", {"Un": "24"}, "K1"), ("c3", "k", {"Un": "24"}, "K2"), ("c4", "k", {"Un": "230"}, "K3")],
                [("c1:p", "c2:a1"), ("c2:a2", "c3:a1"), ("c3:a2", "c1:n"), ("c1:p", "c4:a1"), ("c4:a2", "c1:n")])
    sim.call("loadCircuit", c); sim.call("run", 0.1)
    logic("A20", "Kaksi 24 V kelaa sarjassa 24 V:ssa: kumpikaan ei vedä (12 V < 0,7·24 V)", [sim.call("active", "K1"), sim.call("active", "K2")], [False, False])
    logic("A20", "230 V kela 24 V:ssa ei vedä", sim.call("active", "K3"), False)
    c = circuit([("c1", "ac", {"U": 230}, "G1"), ("c2", "k", {"Un": "24"}, "K1")], [("c1:L", "c2:a1"), ("c2:a2", "c1:N")])
    sim.call("loadCircuit", c); sim.call("run", 0.1)
    logic("A20", "24 V kela 230 V:ssa: varoitus ylijännitteestä", "ylijannite" in sim.call("warningCodes"), True)


def test_A21_pnp_npn(sim, logic):
    for out, wires in (("pnp", [("c1:p", "c2:bn"), ("c2:bu", "c1:n"), ("c2:bk", "c3:a1"), ("c3:a2", "c1:n")]),
                       ("npn", [("c1:p", "c2:bn"), ("c2:bu", "c1:n"), ("c1:p", "c3:a1"), ("c3:a2", "c2:bk")])):
        c = circuit([("c1", "dc", {"U": 24}, "G1"), ("c2", "prox", {"out": out}, "B1"), ("c3", "k", {}, "K1")], wires)
        sim.call("loadCircuit", c); sim.call("run", 0.1)
        a = sim.call("active", "K1")
        sim.call("click", "B1"); sim.call("run", 0.1)
        logic("A21", f"{out.upper()}-anturi: kuorma ohjautuu vain, kun kohde tunnistetaan", [a, sim.call("active", "K1")], [False, True])


def test_A22_varahtely_ja_pakko_ohjaus(sim, logic):
    c = circuit([("c1", "dc", {"U": 24}, "G1"), ("c2", "kc", {"ref": "K1", "kosk": "NC", "nro": 1}, "x"), ("c3", "k", {}, "K1")],
                [("c1:p", "c2:a"), ("c2:b", "c3:a1"), ("c3:a2", "c1:n")])
    sim.call("loadCircuit", c)
    rec = sim.call("record", ["K1"], 1.0)
    n = len(rec["K1"]) - 1
    logic("A22", "Rele omalla avautuvalla koskettimellaan värähtelee (> 20 tilanmuutosta sekunnissa) ja varoitus",
          [n > 20, "varahtely" in sim.call("warningCodes")], [True, True])
    c = circuit([("c1", "dc", {"U": 24}, "G1"), ("c2", "sel", {}, "S1"), ("c3", "k", {}, "K1"), ("c4", "kc", {"ref": "K1", "kosk": "NO", "nro": 1, "vika": "kiinni"}, "x"),
                 ("c5", "kc", {"ref": "K1", "kosk": "NC", "nro": 2}, "y")],
                [("c1:p", "c2:a"), ("c2:b", "c3:a1"), ("c3:a2", "c1:n")])
    sim.call("loadCircuit", c); sim.call("run", 0.1)
    logic("A22", "Pakko-ohjatut koskettimet: sulkeutuvan koskettimen hitsautuessa avautuva ei sulkeudu", sim.call("active", "K1.21"), False)
