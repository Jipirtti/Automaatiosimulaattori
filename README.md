# Automaatiosimulaattori / Automation Simulator

[![Validointi](../../actions/workflows/validointi.yml/badge.svg)](../../actions/workflows/validointi.yml)

Selaimessa toimiva opetussimulaattori relelogiikalle, ohjauspiireille ja PLC-ohjelmoinnille. Piiri piirretään kuten sähköpiirikaavio: syöttö, painikkeet, anturit, releiden kelat ja koskettimet, kontaktorit, suojalaitteet, moottorit, merkkilamput ja magneettiventtiilien kelat kytketään johtimilla. Releen kela ja sen koskettimet ovat erillisiä komponentteja, jotka liitetään toisiinsa releen tunnuksella (esimerkiksi K1). Aikakaavio näyttää releiden, anturien ja toimilaitteiden tilat ajan funktiona. PLC:tä ohjelmoidaan tikapuukaaviolla (LD), ja ohjelman tila näkyy ajon aikana.

**Kokeile:** <https://jipirtti.github.io/Automaatiosimulaattori/> tai avaa `index.html` suoraan selaimessa. Asennusta tai palvelinta ei tarvita.

**Kieli / Language / Sprache:** käyttöliittymä on suomeksi, englanniksi ja saksaksi. Kieltä vaihdetaan yläpalkin FI | EN | DE -valitsimella lennosta, ja valinta muistetaan selaimessa. Suora linkki: `?lang=en` tai `?lang=de`. Käyttöohje: [suomeksi](https://jipirtti.github.io/Automaatiosimulaattori/docs/kayttoohje.html), [englanniksi](https://jipirtti.github.io/Automaatiosimulaattori/docs/user-manual.html), [saksaksi](https://jipirtti.github.io/Automaatiosimulaattori/docs/bedienungsanleitung.html). The user interface is available in Finnish, English and German (FI | EN | DE toggle, or `?lang=en` / `?lang=de`); [user manual in English](https://jipirtti.github.io/Automaatiosimulaattori/docs/user-manual.html). Die Oberfläche ist auf Finnisch, Englisch und Deutsch verfügbar (Umschalter FI | EN | DE oder `?lang=de`); [Bedienungsanleitung auf Deutsch](https://jipirtti.github.io/Automaatiosimulaattori/docs/bedienungsanleitung.html).

Tekijä: Juho Pirttilahti, Seinäjoen ammattikorkeakoulu (SEAMK), 2026. Suunnittelu, sisältö ja validointi: Juho Pirttilahti. Ohjelmakoodi toteutettu tekoälyavusteisesti (Claude, Anthropic). Lisenssi: [CC BY 4.0](LICENSE).

## Ominaisuudet

- 23 komponenttia:
  - syötöt: DC-teholähde, AC-syöttö 230 V, kolmivaihesyöttö 400 V ja kytkentäpiste
  - ohjauslaitteet: painike (palautuva tai lukittuva, NO tai NC), valintakytkin ja kaksikanavainen hätäseis
  - anturit: rajakytkin, reed-anturi ja 3-johdinlähestymiskytkin (PNP/NPN)
  - releet ja logiikka: releen tai kontaktorin kela, aikarele (veto- ja päästöviive), apukosketin, kontaktorin pääkoskettimet, turvarele ja PLC (8 tuloa, 8 lähtöä)
  - suojalaitteet: moottorinsuojakytkin ja lämpörele
  - toimilaitteet: merkkilamppu, magneettiventtiilin kela, pneumatiikkasylinteri 5/2-venttiilillä ja oikosulkumoottori (3 tai 6 napaa, tähti ja kolmio)
- Kosketinnumerot standardin mukaan: rele 13–14 ja 21–22, aikarele 17–18 ja 15–16, lämpörele 95–96 ja 97–98, pääkoskettimet 1–6.
- Releiden veto- ja päästöajat (apurele 10 ms, kontaktori 25 ms). Kontaktoreiden pakko-ohjatut koskettimet ja peilikoskettimet.
- Moottorin pyörimissuunta vaihejärjestyksestä, tähti- ja kolmiokytkennän tunnistus, käynnistysvirta, ylikuorma, jumittunut akseli ja puuttuva vaihe.
- Lämpöreleen ja moottorinsuojakytkimen laukeaminen lämpömallilla. Moottorinsuojakytkimen magneettinen laukaisu oikosulussa.
- Turvarele: kaksikanavainen hätäseispiiri, valvottu kuittaus (laskeva reuna), kanavien eriävyyden ja kanavien välisen oikosulun tunnistus.
- Viat: hitsautunut tai kulunut kosketin, katkennut kela, katkennut johdin, hätäseisin hitsautunut kanava, jumittunut anturin lähtö.
- PLC ja tikapuukaavio (LD, IEC 61131-3):
  - elementit: sulkeutuva ja avautuva kosketin, nouseva ja laskeva reuna, kela, asetus, nollaus, ajastimet TON ja TOF sekä laskuri CTU
  - rinnakkaishaarat ja ohjelmakierto 10 ms
  - ajonaikainen näkymä: jännitteiset polut, ajastimien kuluneet ajat ja laskurien laskennat
- Aikakaavio, jossa on enintään kahdeksan signaalia ja aikaeron mittaus kursoreilla.
- Palaute-painike, joka avaa valmiiksi täytetyn GitHub-issuen piirin kanssa.
- 11 esimerkkipiiriä:
  - itsepito
  - moottorin suora käynnistys
  - suunnanvaihto ristiinlukituksella
  - tähti–kolmiokäynnistys
  - aikareleet
  - sähköpneumaattinen automaattinen paluu
  - sekvenssi A+ B+ A− B−
  - hätäseis turvareleellä
  - PLC: käynnistys ja pysäytys
  - PLC: vilkkuvalo ja laskuri
  - PLC: askelketju A+ B+ A− B−
- Piirin muokkaus samaan tapaan kuin hydrauliikka- ja elektroniikkasimulaattorissa: johtimien reitin veto, laatikkovalinta, kopioi ja liitä, kumoa, tallennus selaimeen ja tekstinä.

> Simulaattori on opetusväline. Sillä ei voi osoittaa ohjausjärjestelmän turvallisuustasoa (PL, SIL) eikä suunnitella todellisia turvatoimintoja.

## Dokumentaatio

| Tiedosto | Sisältö |
| --- | --- |
| [docs/kayttoohje.md](docs/kayttoohje.md) | Käyttöohje, esimerkit ja harjoitustehtävät. Verkkosivuna: <https://jipirtti.github.io/Automaatiosimulaattori/docs/kayttoohje.html> |
| [VALIDOINTI.md](VALIDOINTI.md) | Validoitavat toiminnot, odotetut tulokset ja opettajan validoinnin tila |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Kehitysohjeet, testien ajaminen ja palautteen antaminen |
| [CHANGELOG.md](CHANGELOG.md) | Versiohistoria |

## Validointi

Simulaattorin toiminta validoidaan kahdella tasolla, ks. [VALIDOINTI.md](VALIDOINTI.md):

- **Automaattisesti:**
  - Validointitestit (`tests/test_validointi.py`, A01–A30) tarkistavat piirien toimintalogiikan kytkentäkaavion mukaan, esimerkiksi itsepidon, ristiinlukituksen, tähti–kolmiovaihdon ja turvareleen toiminnan.
  - Samat testit vertaavat aikoja käsinlaskuun, esimerkiksi aikareleiden viiveitä, sylinterien liikeaikoja ja lämpöreleen laukeamisaikaa.
  - Kielitestit (K01–K03) ja käyttöliittymätestit (U01–U08) ja palautetestit (P01–P07) täydentävät niitä.
  - GitHub Actions ajaa testit jokaisesta muutoksesta ja maanantaisin ajastetusti.
- **Opettajan validointi:** jokainen toiminto tarkistetaan ja kirjataan validoiduksi. Validointikierros avautuu issueksi automaattisesti 15.1. ja 15.8.

Testien ajaminen omalla koneella:

```bash
pip install -r requirements-test.txt
python -m playwright install chromium
python -m pytest tests -v
```

## Palaute

Simulaattorin yläpalkin **Palaute**-painike avaa valmiiksi täytetyn issuen, johon on liitetty versio, kieli, selain, varoitukset ja piiri. Issueita voi avata myös suoraan:

- **Toiminta ei vastaa odotusta:** avaa issue mallilla *Toiminta ei vastaa odotusta* ja liitä piiri JSON-muodossa (simulaattorin Tallenna / lataa).
- **Virhe käyttöliittymässä:** mallilla *Virheilmoitus*.
- **Ideat ja kysymykset:** Discussions-osio tai malli *Kehitysehdotus*.

## Rakenne

```
index.html                  Simulaattori (yksi tiedosto, ei riippuvuuksia eikä käännösvaihetta)
docs/                       Käyttöohje (markdown) ja kuvat
tools/rakenna_ohje.py       Rakentaa käyttöohjeen HTML-sivun julkaisun yhteydessä
tests/                      Validointitestit (pytest + Playwright)
VALIDOINTI.md               Validointisuunnitelma ja -tila
.github/workflows/          Validointi, validointikierros ja GitHub Pages -julkaisu
.github/ISSUE_TEMPLATE/     Palautelomakkeet
```

## Lisenssi

Simulaattori ja käyttöohje on lisensoitu [Creative Commons Nimeä 4.0 Kansainvälinen -lisenssillä (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/deed.fi). Saat kopioida, jakaa ja muokata aineistoa mihin tahansa tarkoitukseen, kunhan mainitset tekijän ja oppilaitoksen, merkitset lisenssin ja kerrot tekemistäsi muutoksista.

Suositeltu viittaus: Pirttilahti, J. (2026). *Automaatiosimulaattori ja käyttöohje.* Seinäjoen ammattikorkeakoulu. CC BY 4.0.
