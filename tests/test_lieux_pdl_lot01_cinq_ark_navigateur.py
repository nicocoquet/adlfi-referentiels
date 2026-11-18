"""Chromium : cinq fiches communes nouvelles PDL et ARK anciens non promus."""
from test_lieux_corse_pactols_navigateur import serveur
CASES=[
 ("44005","26678/pcrtN3127ZAunw","26678/pcrtju3LL59HiZ"),
 ("44021","26678/pcrt5umeCC5nWQ","26678/pcrt7IaoJP82qR"),
 ("44029","26678/pcrtir0x0oi7Z7","26678/pcrt5I1iVlmViA"),
 ("44087","26678/pcrt9dHhZhLkZ1","26678/pcrtRIS4y4XXSl"),
 ("44163","26678/pcrthouCaXtWcI","26678/pcrtl9Hc5lXKyi")
]
def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=["--no-sandbox"])
        page=browser.new_page(viewport={"width":1280,"height":900})
        errors=[]
        page.on("pageerror",lambda x:errors.append(str(x)))
        for code,ark,old in CASES:
            page.goto(url+"/lieux/?region=pdl&code="+code+"&annee=2026&niveau=commune",
                      wait_until="domcontentloaded",timeout=45000)
            page.wait_for_function(
                "(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                arg=ark,timeout=60000)
            detail=page.locator("#detail").text_content()
            assert "Correspondance Pactols–COG validée pour 2026" in detail,detail
            assert "commune nouvelle créée en 2016" in detail,detail
            assert "commune déléguée" in detail,detail
            assert old not in detail,detail
            assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
            page.locator("#search").fill(ark)
            page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=12000)
            assert code in page.locator("#results").text_content()
            page.locator("#search").fill(old)
            page.wait_for_timeout(300)
            hits=page.locator("#results").text_content()
            assert "Pactols validé en 2026" not in hits or code not in hits,(code,hits)
        page.goto(url+"/lieux/?region=pdl&code=44005&annee=2015&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtN3127ZAunw')",
            timeout=60000)
        old=page.locator("#detail").text_content()
        assert "2026" in old and "2015" in old
        assert "Aucun contour communal historique qualifié" in old
        assert not errors,errors
        browser.close()
        print("PDL_LOT01_NAVIGATEUR_OK — 5 fiches, recherche, ancien ARK exclu et frise 2015")
if __name__=="__main__":
    main()
