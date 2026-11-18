"""Chromium : Orée d'Anjou et absence d'alignement des Hauts-d'Anjou 2016."""
from test_lieux_corse_pactols_navigateur import serveur
ARK="26678/pcrtS50omR9Tb5"
HISTORICAL="26678/pcrtlzVsRTHJSP"
def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=b.new_page(viewport={"width":1280,"height":900})
        errors=[]
        page.on("pageerror",lambda x:errors.append(str(x)))
        page.goto(url+"/lieux/?region=pdl&code=49126&annee=2026&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                               arg=ARK,timeout=60000)
        detail=page.locator("#detail").text_content()
        assert "Orée d'Anjou" in detail and "MOD50" in detail,detail
        assert "49069" in detail and "49126" in detail,detail
        assert HISTORICAL not in detail,detail
        page.locator("#search").fill(ARK)
        page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
        assert "Pactols validé en 2026" in page.locator("#results").text_content()
        page.locator("#search").fill(HISTORICAL)
        page.wait_for_timeout(350)
        hits=page.locator("#results").text_content()
        assert "Pactols validé en 2026" not in hits or "49126" not in hits
        page.goto(url+"/lieux/?region=pdl&code=49080&annee=2026&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Les Hauts-d')",
            timeout=60000)
        assert "26678/pcrtJmNskrfHiK" not in page.locator("#detail").text_content()
        assert not errors,errors
        b.close()
        print("PDL_OREE_MOD50_NAVIGATEUR_OK — 49126 validé, 49080 ancien concept exclu")
if __name__=="__main__":
    main()
