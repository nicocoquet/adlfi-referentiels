"""Chromium : la recherche d'Afa distingue le COG 1975 du COG 2026."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':820})
        errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.on('console',lambda msg:errs.append('console: '+msg.text) if msg.type=='error' else None)
        def open_search(query):
            page.locator('#search-tool').evaluate('(x) => {x.open=true}')
            page.locator('#search').fill(query)
            page.wait_for_function(
                "() => !document.querySelector('#results')?.hidden && "
                "document.querySelectorAll('#results button').length > 0",timeout=30000)
        def first():
            return page.locator('#results button').first.text_content()
        page.goto(url+'/lieux/?zoom=corse&niveau=commune&annee=2026',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
            timeout=60000)
        open_search('Afa')
        assert '2A001' in first(),('2026 : '+first())
        assert 'actif en 2026' in first(),('2026 : '+first())
        results=page.locator('#results').text_content()
        assert '20001' in results,results
        assert 'non actif au 1er janvier 2026' in results,results
        open_search('20001')
        assert '20001' in first(),('Code historique explicite : '+first())
        open_search('26678/pcrtgs2LLPYow2')
        assert 'Pactols validé pour 2026' in first(),('ARK explicite : '+first())

        page.goto(url+'/lieux/?zoom=corse&niveau=commune&annee=1975',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('historique 1975')",
            timeout=60000)
        open_search('Afa')
        assert '20001' in first(),('1975 : '+first())
        assert 'actif en 1975' in first(),('1975 : '+first())
        results=page.locator('#results').text_content()
        assert '2A001' in results,results
        assert 'non actif au 1er janvier 1975' in results,results
        open_search('2A001')
        assert '2A001' in first(),('Code futur explicitement demandé : '+first())
        assert not errs,errs
        print('LIEUX_RECHERCHE_AFA_CHRONO_NAVIGATEUR_OK — COG 1975/2026, codes, ARK')
        browser.close()


if __name__=='__main__':
    main()
