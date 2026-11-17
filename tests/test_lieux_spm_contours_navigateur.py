"""Chromium : deux communes SPM, zoom sur contour, ARK 2026 et frise 1975."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    cases=[
        ("97501","Miquelon-Langlade","26678/pcrtQAMzeGHldU"),
        ("97502","Saint-Pierre","26678/pcrtYQmFfwxLq8"),
    ]
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for code,label,ark in cases:
            page.goto(url+'/lieux/?zoom=atlantique&ref_cog=COMER:COM:'+code+
                '&annee=2026&niveau=commune',wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "() => document.querySelector('#map-status')?.textContent.includes('deux communes de Saint-Pierre-et-Miquelon')",
                timeout=60000)
            page.wait_for_function(
                "(code) => document.querySelector('#detail')?.textContent.includes(code)",
                arg=code,timeout=30000)
            detail=page.locator('#detail').text_content()
            assert label in detail and ark in detail,detail
            assert 'Contour communal de référence 2026 affiché' in detail,detail
            assert 'non homologué comme limite juridique' in detail,detail
            assert 'Correspondance Pactols validée (2026)' in detail,detail
            assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
            assert page.locator('.leaflet-overlay-pane canvas').count()==1

            page.locator('#search').fill(code)
            page.wait_for_function("() => !document.querySelector('#results')?.hidden")
            hits=page.locator('#results').text_content()
            assert label in hits and code in hits,hits

            page.locator('#year').evaluate(
                "(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
            page.locator('#year').dispatch_event('change')
            page.wait_for_function("() => document.querySelector('#year-label')?.textContent.includes('1975')")
            page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('ne restitue pas les limites de 1975')")
            hist=page.locator('#detail').text_content()
            assert 'Contour communal de référence 2026 affiché' not in hist,hist
            assert 'Correspondance Pactols validée (2026)' in hist,hist
        assert not errors,errors
        print('SPM_2_NAVIGATEUR_OK — deux communes, ARK préexistants, contours 2026 et repère 1975')
        browser.close()


if __name__=='__main__':
    main()
