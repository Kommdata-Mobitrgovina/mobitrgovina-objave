# Samodejne objave MobiTrgovina → Facebook + Instagram

Trikrat na dan (8:15, 13:15, 18:15) GitHub Actions:
1. iz trgovine (WooCommerce, ključ samo za branje) izbere en objavljen izdelek na zalogi – najprej akcije, isti izdelek največ na 21 dni,
2. naredi 10-sekundni navpični video (slike, ime, cena, popust),
3. ga objavi kot Reel na Facebook stran in Instagram,
4. si v `state/posted.json` zapomni, kaj je že objavil.

## Skrivnosti (Settings → Secrets and variables → Actions)
`WC_URL`, `WC_KEY`, `WC_SECRET`, `FB_PAGE_ID`, `FB_PAGE_TOKEN`, `IG_USER_ID`

## Ročni zagon / preizkus
Actions → »Objave na FB in IG« → Run workflow. Z označenim »Samo preizkus« naredi le video (prenos pod Artifacts) in nič ne objavi.

## Ustavitev
Actions → »Objave na FB in IG« → ⋯ → Disable workflow.
