"""Chromium : Chemillé 2026 et absence de promotion des deux ARK historiques."""
from test_lieux_corse_pactols_navigateur import serveur
ARK="26678/pcrtzDf0WnnRyr"
OLD=["26678/pcrtL5GRFXn3Zs","26678/pcrtWU8rdgPSSH"]
def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":900})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.goto(url+"/lieux/?region=pdl&code=49092&annee=2026&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                               arg=ARK,timeout=60000)
        d=page.locator("#detail").text_content()
        assert "Chemillé-en-Anjou" in d and "créée le 15 décembre 2015" in d,d
        assert "Chemillé-Melay" in d and "sans équivalence ni identification rétroactive" in d,d
        assert all(old not in d for old in OLD),d
        assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ARK+'"]').count()==1
        page.locator("#search").fill(ARK)
        page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=12000)
        assert "Pactols validé en 2026" in page.locator("#results").text_content()
        for old in OLD:
            page.locator("#search").fill(old)
            page.wait_for_timeout(300)
            result=page.locator("#results").text_content()
            assert "Pactols validé en 2026" not in result or "49092" not in result,(old,result)
        page.goto(url+"/lieux/?region=pdl&code=49092&annee=2014&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                               arg=ARK,timeout=60000)
        d=page.locator("#detail").text_content()
        assert "2014" in d and "2026" in d
        assert "Aucun contour communal historique qualifié" in d
        assert not errors,errors
        browser.close()
        print("PDL_CHEMILLE_NAVIGATEUR_OK — 2026 et 2014, ARK historiques non promus")
if __name__=="__main__":
    main()
