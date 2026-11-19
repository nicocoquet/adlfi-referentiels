"""Test Chromium BFC : recherche ARK, fiche 2026, 1975, exception 25060."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    import json
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    pub=json.loads((root/'docs/data/lieux-chronologie/pactols-bfc-2026.json').read_text(encoding='utf-8'))
    first=pub['alignements_Pactols_COG_valides_2026'][0]
    code=first['code_insee']
    ark=first['ark_pactols']
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        errs=[]
        page.on('pageerror',lambda e:errs.append(str(e)))
        page.goto(url+'/lieux/?region=bfc&code='+code+'&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
            timeout=60000)
        page.wait_for_function(
            "(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
            arg=ark,timeout=30000)
        detail=page.locator('#detail').text_content()
        assert 'Correspondance Pactols–COG' in detail and '2026 seulement' in detail,detail
        assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
        page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
        page.locator('#search').fill(ark)
        page.wait_for_function("() => !document.querySelector('#results')?.hidden")
        hits=page.locator('#results').text_content()
        assert 'Pactols validé en 2026' in hits and code in hits,hits
        page.locator('#year').evaluate("(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.locator('#year').dispatch_event('change')
        page.wait_for_function("() => document.querySelector('#year-label')?.textContent.includes('1975')")
        d=page.locator('#detail').text_content()
        assert ark in d and '2026 seulement' in d,d
        page.goto(url+'/lieux/?region=bfc&code=25060&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('25060')",
            timeout=60000)
        neg=page.locator('#detail').text_content()
        assert 'Aucun alignement Pactols individuellement validé' in neg,neg
        assert '26678/pcrtksq5m3cwb846scr9wzkv' not in neg
        assert not errs,errs
        print('BFC_3614_NAVIGATEUR_OK — ARK recherché et affiché en 2026, pas de rétroprojection, exception 25060')
        browser.close()


if __name__=='__main__':
    main()
