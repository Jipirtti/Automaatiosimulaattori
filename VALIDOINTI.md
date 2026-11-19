# Validointisuunnitelma

Simulaattorin toiminta validoidaan kahdella tasolla:

1. **Automaattinen regressiovalidointi:** testit kansiossa `tests/` vertaavat simulaattorin toimintaa kytkentäkaavion mukaiseen odotukseen. Ajoja verrataan käsinlaskuun, jonka testi laskee itsenäisesti komponenttien parametreista. GitHub Actions ajaa testit jokaisesta muutoksesta ja maanantaisin.
2. **Opettajan validointi:** vastuuopettaja tarkistaa jokaisen toiminnon simulaattorissa ja vertaa sitä kytkentäkaavioon, standardiin, valmistajan ohjeeseen tai laboratoriokokeeseen. Tulos kirjataan tähän tiedostoon (päivämäärä, validoija, menetelmä). Validointikierros avautuu issueksi automaattisesti 15.1. ja 15.8.

Kun simulaattorin toimintalogiikkaa muutetaan, muutoksen koskemat rivit palautetaan tilaan *Ei validoitu*.

## Mallin vakiot

| Suure | Arvo | Peruste |
| --- | --- | --- |
| Aika-askel | 1 ms | Releen vetoaikaa lyhyempi; kosketintilan muutos näkyy piirissä seuraavalla askeleella |
| Kuorman toimintaraja | 0,7·Un | Tyypillinen releen ja kontaktorin vetojännitteen alaraja |
| Ylijännitevaroitus | 1,3·Un | |
| Releen veto- ja päästöaika | apurele 10 ms, kontaktori 25 ms | Tyypilliset luettelo-arvot |
| Lämpömalli | dh/dt = ((I/Ir)² − h)/τ, τ = 100 s, laukeaminen kun h ≥ 1,44 | Laukeaa pysyvällä virralla 1,2·Ir; ei laukea virralla 1,05·Ir |
| Laukeamisaika | t = −τ·ln((r² − 1,44)/(r² − h0)), r = I/Ir | Ratkaisu lämpömallista, h0 = alkulämpenemä |
| Palautus | sallittu, kun h < 1,2 | |
| Moottorin virta | käynnistysvirta 6·In (suora, kolmio) tai 2·In (tähti), nimelliskuormalla In, ylikuormalla 2·In, kahdella vaiheella pysähdyksissä 5·In | Yksinkertaistus; virta laskee lineaarisesti jättämän mukana |
| Moottorin nopeus | 1450 r/min (Δ ja suora), 1420 r/min (Y); kiihdytysaika parametrina, tähdessä kolminkertainen | Yksinkertaistus |

## A. Automaattisesti testatut toiminnot (tests/test_validointi.py)

| ID | Toiminto | Piiri ja toimenpide | Odotettu tulos | Tol. | Opettajan validointi |
| --- | --- | --- | --- | --- | --- |
| A01 | Itsepito | Esim. 1: S2, sitten S1 | K1 jää vetäneeksi S2:n vapautuksen jälkeen; S1 päästää | täsmälleen | Ei validoitu |
| A02 | Releen ja kontaktorin vetoaika | Esim. 1 ja 2 | 10 ms ja 25 ms | 11 % / 5 % | Ei validoitu |
| A03 | Vetoviive | Esim. 5, S1 | KT1:n kosketin sulkeutuu ajan T = 3,00 s kuluttua; ohjauksen poisto avaa heti | 0,2 % | Ei validoitu |
| A04 | Päästöviive | Esim. 5, S2 | Kosketin sulkeutuu heti; aukeaa T = 3,00 s ohjauksen poistosta | 0,2 % | Ei validoitu |
| A05 | Suunnanvaihto ja ristiinlukitus | Esim. 3 | K1: myötäpäivään; S2 ei vedä K2:ta K1:n aikana; S0 + S2: vastapäivään | täsmälleen | Ei validoitu |
| A06 | Tähti–kolmiokäynnistys | Esim. 4 | Tähti T + 25 ms; K2 ja K3 eivät ole yhtä aikaa vetäneinä; vaihtotauko 25 ms; lopuksi kolmio | 0,3 % / 8 % | Ei validoitu |
| A07 | Lämpörele, ylikuorma 200 % | Esim. 2 | Laukeamisaika −τ·ln((4 − 1,44)/(4 − h0)) ≈ 42–45 s; 95–96 aukeaa, 97–98 sulkeutuu; palautus estyy kuumana | 0,5 % | Ei validoitu |
| A08 | Jumittunut akseli | Esim. 2 | I = 6·In; laukeamisaika −τ·ln((36 − 1,44)/36) = 4,08 s | 0,1 % / 1 % | Ei validoitu |
| A09 | Puuttuva vaihe | Esim. 2, L3 katki | Moottori ei käynnisty, varoitus; laukeaminen −τ·ln((25 − 1,44)/25) = 5,93 s | 1 % | Ei validoitu |
| A10 | Oikosulku ohjauspiirissä | 24 V, + ja 0 V oikosuljettu | Teholähde laukeaa, kuormat päästävät; kuittauksen jälkeen toimii | täsmälleen | Ei validoitu |
| A11 | Oikosulku pääpiirissä | Vaiheiden välinen oikosulku Q1:n jälkeen | Q1 laukeaa (magneettinen), syöttö ei | täsmälleen | Ei validoitu |
| A12 | Tähtipiste puuttuu | 6-napainen moottori, vain U1, V1, W1 kytketty | Ei pyöri, varoitus | täsmälleen | Ei validoitu |
| A13 | Kolmiokytkentä ja pyörimissuunta | Kolmio U1–W2, V1–U2, W1–V2; vaiheet L2–L1–L3 | Δ, myötäpäivään; vaihdetuilla vaiheilla vastapäivään | täsmälleen | Ei validoitu |
| A14 | Sylinterin liikeaika | Esim. 6 | Ulos 1,5 s, sisään 1,0 s; automaattinen paluu | 0,2–0,3 % | Ei validoitu |
| A15 | Sekvenssi A+ B+ A− B− | Esim. 7 | Liikejärjestys anturien mukaan; jakso 4,0 s | 0,5 % | Ei validoitu |
| A16 | Hätäseis ja valvottu kuittaus | Esim. 8 | Hätäseis avaa lähdöt; vapautus ei käynnistä; kuittaus laskevalla reunalla | täsmälleen | Ei validoitu |
| A17 | Hätäseisin kanavavika | Esim. 8, kanava 2 hitsautunut | Pysäytys kanavan 1 kautta; uudelleenkäynnistys estyy (kanavat eriävät) | täsmälleen | Ei validoitu |
| A18 | Takaisinkytkentä | Esim. 8, K1:n pääkosketin hitsautunut | K2 katkaisee moottorin; K1:n peilikosketin estää kuittauksen | täsmälleen | Ei validoitu |
| A19 | Kanavien välinen oikosulku | Esim. 8, S12–S22 yhdistetty | Lähdöt eivät kytkeydy, lukitus | täsmälleen | Ei validoitu |
| A20 | Kuorman jännite | Kaksi 24 V kelaa sarjassa; 230 V kela 24 V:ssa; 24 V kela 230 V:ssa | Eivät vedä; ylijännitevaroitus | täsmälleen | Ei validoitu |
| A21 | PNP- ja NPN-anturi | 3-johdinanturi ja rele | Kuorma ohjautuu vain kohteen ollessa anturilla | täsmälleen | Ei validoitu |
| A22 | Värähtely ja pakko-ohjatut koskettimet | Rele omalla NC-koskettimellaan; hitsautunut NO-kosketin | Värähtely ja varoitus; NC ei sulkeudu | täsmälleen | Ei validoitu |

## B. Laadulliset toiminnot (opettajan validointi)

| ID | Toiminto | Piiri ja toimenpide | Odotettu havainto | Opettajan validointi |
| --- | --- | --- | --- | --- |
| L01 | Johtimien värit | Esim. 2 käynnissä | +24 V punainen, 0 V sininen, vaiheet ruskea / musta / harmaa, jännitteetön vaalea | Ei validoitu |
| L02 | Aikakaavio ja kursorit | Esim. 4, kaksi kursoria K2:n päästöön ja K3:n vetoon | Δt ≈ 25 ms näkyy kursoreilla | Ei validoitu |
| L03 | Lämpöreleen palautus | Esim. 2, ylikuorma, laukeamisen jälkeen | Palautus estyy kuumana ja onnistuu jäähtymisen jälkeen. Automaattisella palautuksella 95–96 sulkeutuu itsestään, mutta itsepitopiiri ei käynnisty ilman S1:tä | Ei validoitu |
| L04 | Moottorinsuojakytkimen laukeaminen ylikuormasta | Esim. 8, M1 ylikuormitettu (200 %) | Q1 laukeaa noin 43 s kuluttua ja avaa pääpiirin | Ei validoitu |
| L05 | Jatkuva sekvenssi | Esim. 7, S1 pohjassa | Jakso A+ B+ A− B− toistuu, kunnes S1 vapautetaan | Ei validoitu |
| L06 | Automaattinen käynnistys turvareleessä | Esim. 8, Käynnistys: automaattinen, S33–S34 kytketty yhteen | Hätäseisin vapautus käynnistää uudelleen ilman kuittausta (ei sallittu hätäseisille) | Ei validoitu |

## C. Rajaukset

Seuraavia ilmiöitä malli ei kuvaa, joten niitä ei validoida:

- kosketinpomppu ja valokaari
- kelojen induktiiviset ilmiöt (katkaisun jännitepiikki, suojadiodit)
- jännitteenalenema johtimissa
- releiden mekaaninen ja sähköinen kestoikä
- turvareleen testipulssit ja diagnostiikan kattavuus
- paineilman virtaus, paine ja kuormitus
- moottorin tarkka momentti- ja virtakäyrä

Simulaattorilla ei voi osoittaa turvatoiminnon suorituskykytasoa (PL standardin EN ISO 13849-1 mukaan) eikä turvallisuuden eheystasoa (SIL).
