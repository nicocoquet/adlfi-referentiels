"""Chromium : Normandie cartographiée en 2026, 16 ARK, 4 exceptions et COG ancien."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':920})
        errors=[]
        requests=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('request',lambda r:requests.append(r.url))
        page.goto(url+'/lieux/?zoom=normandie&niveau=commune&annee=2026&code=50129&zone=normandie',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026') && "
            "document.querySelector('#map-status')?.textContent.includes('Normandie')",
            timeout=120000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrt4Ft3j507NA')",
            timeout=60000)
        assert page.locator('#zoom').input_value()=='normandie'
        detail=page.locator('#detail').text_content()
        assert 'Cherbourg-en-Cotentin' in detail,detail
        assert '50129' in detail,detail
        assert 'validée uniquement' in detail,detail
        assert '26678/pcrtKpjSHTRIyK' in detail,detail
        assert any('contours-2026-normandie.geojson' in x for x in requests),requests
        assert not errors,errors

        # Recherche directe d'un ARK contemporain, sans promotion de l'ancien.
        page.locator('#search-tool').evaluate('(el) => { el.open=true; }')
        page.locator('#search').fill('26678/pcrt4Ft3j507NA')
        page.wait_for_function(
            "() => !document.querySelector('#results')?.hidden && "
            "document.querySelector('#results')?.textContent.includes('Cherbourg-en-Cotentin')",
            timeout=30000)
        assert 'Pactols validé pour 2026' in page.locator('#results').text_content()

        # Remonter à 2015 : conserver l'état administratif COG de 2015,
        # sans étiqueter comme valide l'ARK de la commune nouvelle de 2016.
        page.locator('#year').evaluate(
            "(el) => {el.value='2015';el.dispatchEvent(new Event('input',{bubbles:true}));}"
        )
        page.locator('#year').dispatch_event('change')
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('aucun contour communal historique 2015')",
            timeout=60000)
        detail_2015=page.locator('#detail').text_content()
        assert 'Cherbourg-Octeville' in detail_2015,detail_2015
        assert '26678/pcrt4Ft3j507NA' not in detail_2015,detail_2015
        assert 'Aucun contour communal historique qualifié' in detail_2015,detail_2015

        # Les quatre exceptions sont consultables, sans fausse validation.
        page.goto(url+'/lieux/?zoom=normandie&niveau=commune&annee=2026&code=50412&zone=normandie',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('Port-Bail-sur-Mer')",
            timeout=120000)
        reserved=page.locator('#detail').text_content()
        assert 'Aucun alignement Pactols individuellement validé' in reserved,reserved
        assert '26678/pcrtouI45wMnJl' not in reserved,reserved
        assert not errors,errors
        print('NORMANDIE_CARTE_NAVIGATEUR_OK — contour 2026, ARK, historique et Portbail réservé')
        browser.close()


if __name__=='__main__':
    main()
