# Kehitysohjeet

Automaatiosimulaattoria kehitetään avoimesti Seinäjoen ammattikorkeakoulussa (SEAMK). Muutokset ja palaute ovat tervetulleita.

## Periaatteet

- Simulaattori on yksi tiedosto (`index.html`) ilman ulkoisia kirjastoja ja käännösvaihetta.
- Toimintalogiikkaa koskeva muutos vaatii kaksi asiaa:
  - testin tiedostoon `tests/test_validointi.py`
  - rivin tiedostoon `VALIDOINTI.md`

  Muutetun toiminnon opettajan validoinnin tila palautetaan arvoon *Ei validoitu*.
- Testin odotusarvo tulee kytkentäkaaviosta (mitä piirin pitää tehdä) tai käsinlaskusta komponenttien parametreista. Simulaattorin omia välituloksia ei käytetä odotusarvona.

## Koodin rakenne (index.html)

| Osa | Sisältö |
| --- | --- |
| `TY` | Komponenttityypit. Kentät: `ports` (liitännät), `prm` (parametrit), `sw` (johtavat yhteydet), `terms` (lähteen navat), `draw` ja `dyn` (piirrosmerkki), `active` (aikakaavion tila) |
| `ufRoots`, `groupTerms`, `vAcross` | Johtavuustarkastelu (union–find) ja kuorman jännite |
| `stepSim` | Aika-askel: oikosulut, kuormat, releet ja ajastimet, sylinterit, moottorit, suojalaitteet |
| `motorStep`, `srStep`, `attribution` | Moottorin kytkentä ja dynamiikka, turvarele, moottorivirran kohdistus suojalaitteille |
| `drawTD`, `recordTraces` | Aikakaavio |
| `EX` | Esimerkkipiirit |
| `window.AutSim` | Testirajapinta |

### Uusi komponentti

1. Lisää tyyppi `TY`-olioon. Kentät:
   - pakolliset: `ports`, `prm`, `def`, `init`, `draw`
   - tarvittaessa: `sw`, `terms`, `dyn`, `read`, `active`, `click` / `hit`
2. Jos komponentti on kuorma, lisää sen jännitteen laskenta `stepSim`-funktioon.
3. Lisää komponentti palettiin (`PAL`) ja testiin `tests/test_kieli.py` (`TYPES`).

### Käännökset

Kaikki tekstit kirjoitetaan muodossa `tr('suomeksi', 'in English')` tai parametreissa `['suomeksi', 'in English']`. Staattisessa HTML:ssä käytetään `data-en`-, `data-en-title`- ja `data-en-aria`-attribuutteja. Testi K01 varmistaa, ettei englanninkielisessä näkymässä ole suomea.

## Testit

```bash
pip install -r requirements-test.txt
python -m playwright install chromium
python -m pytest tests -v
```

## Palaute

Käytä issue-malleja (Toiminta ei vastaa odotusta, Virheilmoitus, Kehitysehdotus) tai Discussions-osiota. Liitä piiri JSON-muodossa (Tallenna / lataa), jotta tilanne voidaan toistaa.
