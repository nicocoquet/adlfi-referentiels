"""Chromium : contrôle représentatif des 5 départements, sans ARK anciens promus."""
from test_lieux_corse_pactols_navigateur import serveur
CASES=[
 ("44180","26678/pcrtygSjlBdwSc","26678/pcrtO42UaHupVP"),
 ("49023","26678/crtr7hpu73Yuq","26678/pcrtvjGasJXuqo"),
 ("53017","26678/pcrtlP7Iva0Nmn","26678/pcrtL3LoVJsIUv"),
 ("72025","26678/pcrtRaa5XyZ6XN","26678/pcrtMlSYLHLeBi"),
 ("85090","26678/pcrtJlbnUsIRmk","26678/pcrtacMY1yGSDj")
]
def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={"width":1280,"height":900})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        for code,ark,old in CASES:
            page.goto(url+"/lieux/?region=pdl&code="+code+"&annee=2026&niveau=commune",
                      wait_until="domcontentloaded",timeout=45000)
            page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                                   arg=ark,timeout=60000)
            detail=page.locator("#detail").text_content()
            assert "Correspondance Pactols–COG validée pour 2026" in detail,detail
            assert "ancienne commune" in detail and "déléguée" in detail,detail
            assert old not in detail,detail
            assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
            page.locator("#search").fill(ark)
            page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
            assert "Pactols validé en 2026" in page.locator("#results").text_content()
            page.locator("#search").fill(old)
            page.wait_for_timeout(350)
            hits=page.locator("#results").text_content()
            assert "Pactols validé en 2026" not in hits or code not in hits,(code,hits)
        page.goto(url+"/lieux/?region=pdl&code=44180&annee=2017&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtygSjlBdwSc')",
            timeout=60000)
        historical=page.locator('#detail').text_content()
        assert "2017" in historical and "Aucun contour communal historique qualifié" in historical
        assert not errors,errors
        browser.close()
        print("PDL_LOT02_NAVIGATEUR_OK — 5 départements et 2017 sans rétroprojection")
if __name__=="__main__":
    main()
