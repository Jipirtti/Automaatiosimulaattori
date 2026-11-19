"""Pytest-asetukset automaatiosimulaattorin validointitesteille.

Testit avaavat index.html-tiedoston headless-Chromiumissa ja ohjaavat simulaattoria
sen testirajapinnan window.AutSim kautta. Jokainen tarkistus kirjataan raporttiin
validointiraportti.md, joka liitetään GitHub Actions -ajon yhteenvetoon.
"""
import os
import pathlib
import datetime
import pytest
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
REPORT = ROOT / "validointiraportti.md"
_rows = []


@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def sim(browser):
    """Tuore simulaattorisivu jokaiselle testille; oletuksena suomi."""
    page = browser.new_page(viewport={"width": 1500, "height": 950})
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(INDEX.as_uri())
    page.wait_for_function("window.AutSim !== undefined")
    page.evaluate("localStorage.clear()")
    page.evaluate("AutSim.setLang('fi')")

    class Sim:
        def js(self, expr):
            return page.evaluate(expr)

        def call(self, fn, *args):
            return page.evaluate(f"(a) => AutSim.{fn}(...a)", list(args))

    s = Sim()
    s.page = page
    s.errors = errors
    yield s
    assert not errors, f"JavaScript-virheitä: {errors}"
    page.close()


@pytest.fixture
def check(request):
    """check(id, kuvaus, mitattu, odotettu, toleranssi_suht, yksikkö) kirjaa ja tarkistaa arvon."""
    def _check(vid, desc, measured, expected, rel_tol, unit=""):
        ok = measured is not None and abs(measured - expected) <= rel_tol * abs(expected)
        _rows.append((vid, desc, f"{measured:.5g} {unit}" if measured is not None else "–", f"{expected:.5g} {unit}", f"±{rel_tol*100:.1f} %", ok))
        assert ok, (f"{vid} {desc}: mitattu {measured} {unit}, odotettu {expected:.5g} {unit} "
                    f"(toleranssi ±{rel_tol*100:.1f} %)")
    return _check


@pytest.fixture
def logic(request):
    """logic(id, kuvaus, havaittu, odotettu) kirjaa ja tarkistaa toimintalogiikan tuloksen (tila tai järjestys)."""
    def _logic(vid, desc, seen, expected):
        ok = seen == expected
        _rows.append((vid, desc, str(seen), str(expected), "täsmälleen", ok))
        assert ok, f"{vid} {desc}: havaittu {seen}, odotettu {expected}"
    return _logic


def pytest_sessionfinish(session, exitstatus):
    if not _rows:
        return
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sha = os.environ.get("GITHUB_SHA", "paikallinen")[:7]
    lines = ["# Validointiraportti", "",
             f"Ajettu {now}, versio `{sha}`. Tarkistuksia {len(_rows)}, "
             f"hyväksytty {sum(r[5] for r in _rows)}.", "",
             "| ID | Ilmiö | Simuloitu | Odotettu (käsinlasku tai kytkentäkaavio) | Toleranssi | Tulos |",
             "| --- | --- | --- | --- | --- | --- |"]
    for vid, desc, m, e, tol, ok in _rows:
        lines.append(f"| {vid} | {desc} | {m} | {e} | {tol} | {'✅' if ok else '❌'} |")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def circuit(comps, wires, traces=()):
    """Rakentaa piirin kuvauksen: comps = [(id, tyyppi, parametrit, nimi)], wires = [('c1:p', 'c2:a'), ...]."""
    return {"comps": [{"id": cid, "type": t, "x": 100 + 120 * i, "y": 200, "rot": 0, "label": lab, "p": p}
                      for i, (cid, t, p, lab) in enumerate(comps)],
            "wires": [{"a": a, "b": b} for a, b in wires],
            "traces": list(traces)}
