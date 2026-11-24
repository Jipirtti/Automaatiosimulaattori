# Muutosloki

## Julkaisematon

- Saksankielinen käyttöliittymä (FI | EN | DE -valitsin, `?lang=de`, selaimen kieli de). Termit tarkistettu saksalaisista standardeista ja alan termistöstä. Kielitestit tarkistavat, ettei saksankielisessä näkymässä ole kääntämättömiä rivejä.
- Käyttöohje englanniksi (`docs/user-manual.md`) ja saksaksi (`docs/bedienungsanleitung.md`) omilla kuvakaappauksilla (`docs/kuvat/en/`, `docs/kuvat/de/`). `tools/rakenna_ohje.py` rakentaa kaikki kolme HTML-sivua, ja simulaattorin Käyttöohje-linkki avaa valitun kielen ohjeen.
- Kopioi kuva -painike jokaiseen kaavioon: kaavio leikepöydälle PNG-kuvana vaalealla taustalla ja kaksinkertaisella tarkkuudella, otsikon, selitteen ja lähdemerkinnän kanssa. Jos selain estää kopioinnin, kuva avautuu ikkunaan tallennettavaksi. Yhteinen SimKuva-moduuli kaikissa simulaattoreissa. Testit KV01–KV04.

## 1.1.0 – 2026-11-19

- PLC-komponentti: syöttö L+ ja M, 8 digitaalituloa (I0.0–I0.7) ja 8 PNP-lähtöä (Q0.0–Q0.7), RUN/STOP, kierrosaika 10 ms.
- Tikapuukaavioeditori (LD) alapaneelin välilehdellä:
  - elementit: koskettimet, reunat, kela, asetus, nollaus, TON, TOF ja CTU
  - rinnakkaishaarat, kommentit, kumoa
  - ajonaikainen näkymä
- PLC-esimerkit 9–11: käynnistys ja pysäytys, vilkkuvalo ja laskuri, askelketju.
- Palaute-painike: valmiiksi täytetty GitHub-issue (lomakepohja *Toiminta ei vastaa odotusta*, virhe, kehitysehdotus) tai sähköposti.
- Testit A23–A30 (PLC), U07–U08 (editori, tallennus) ja P01–P07 (palaute).

## 1.0.0 – 2026-11-19

- Ensimmäinen julkaisu: relelogiikka ja ohjauspiirit selaimessa.
- Ratkaisu johtavuustarkasteluna 1 ms aika-askeleella. Kuorma toimii, kun sen navat ovat saman lähteen eri napojen kanssa yhteydessä ja jännite on vähintään 70 % nimellisjännitteestä.
- 22 komponenttia:
  - syötöt
  - painikkeet, valintakytkin ja hätäseis
  - raja-, reed- ja lähestymiskytkimet
  - releet, aikareleet, apu- ja pääkoskettimet ja turvarele
  - moottorinsuojakytkin ja lämpörele
  - merkkilamput, magneettiventtiilit, pneumatiikkasylinterit ja oikosulkumoottorit
- Viat ja niiden vaikutukset, esimerkiksi hitsautunut kosketin, pakko-ohjatut koskettimet ja hätäseisin hitsautunut kanava.
- Aikakaavio ja aikaeron mittaus.
- Suomi ja englanti.
- Kahdeksan esimerkkipiiriä, käyttöohje ja harjoitustehtävät.
- Testit:
  - validointitestit A01–A22
  - kielitestit K01–K03
  - käyttöliittymätestit U01–U06
