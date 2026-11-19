"""Chromium : 5 départements, 17 liens indirects et absence de rétroprojection."""
from test_lieux_corse_pactols_navigateur import serveur

CASES=[
 ("44003","26678/pcrtm2rmswpj3vsnfzjx9hpr","Q57208924","26678/pcrtdOwjOLvibi"),
 ("49060","26678/pcrtbbrmxmp38d27cr251d2t","Q58839998","26678/pcrtyZ8xgFPWc7"),
 ("53062","26678/pcrtpjxq9ts7tk9kb0k1md00","Q59344205","26678/pcrtM5zGF9k5oE"),
 ("72080","26678/pcrtk5xjv8vgwk9w8fmrz9z3","Q59487990","26678/pcrtW93HHq1P8L"),
 ("85001","26678/pcrtdxtkn2hw8953wg2j3nz7","Q110014813","26678/pcrt8VTmPEbLKQ")
]
def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        b=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=b.new_page(viewport={"width":1280,"height":900})
        errors=[]
        page.on("pageerror",lambda e:errors.append(str(e)))
        for code,ark,qid,ancien in CASES:
            page.goto(url+"/lieux/?region=pdl&code="+code+"&annee=2026&niveau=commune",
                      wait_until="domcontentloaded",timeout=45000)
            page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                                   arg=ark,timeout=60000)
            detail=page.locator('#detail').text_content()
            assert "Wikidata" in detail and "P374" in detail and qid in detail,detail
            assert "Pactols ne fournit pas directement" in detail,detail
            assert ancien not in detail,detail
            page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
            page.locator('#search').fill(ark)
            page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
            assert "Pactols validé en 2026" in page.locator('#results').text_content()
            page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
            page.locator('#search').fill(ancien)
            page.wait_for_timeout(350)
            hits=page.locator('#results').text_content()
            assert "Pactols validé en 2026" not in hits or code not in hits,(code,hits)
        page.goto(url+"/lieux/?region=pdl&code=44003&annee=2017&niveau=commune",
                  wait_until="domcontentloaded",timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtm2rmswpj3vsnfzjx9hpr')",
            timeout=60000)
        historical=page.locator('#detail').text_content()
        assert "2017" in historical and "Aucun contour communal historique qualifié" in historical
        assert not errors,errors
        b.close()
        print('PDL_WIKIDATA_17_NAVIGATEUR_OK — 5 départements et 2017 distinct')
if __name__=='__main__':
    main()
