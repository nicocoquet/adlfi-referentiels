"""Chromium : les deux renommages PACA et l'exception UUID Céreste 04045."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur

CASES=[
    ("05127","26678/pcrtla4EHGDgDd","Rousset-Serre-Ponçon"),
    ("83052","26678/pcrt7B7bs9P5g2","Esparron-de-Pallières"),
]

def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        for code,ark,label in CASES:
            page.goto(url+'/lieux/?region=paca&code='+code+'&annee=2026&niveau=commune',
                      wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
                timeout=60000)
            page.wait_for_function(
                "(expected) => document.querySelector('#detail')?.textContent.includes(expected)",
                arg=ark,timeout=30000)
            detail=page.locator('#detail').text_content()
            assert label in detail,detail
            assert 'Correspondance Pactols–COG' in detail and '2026 seulement' in detail,detail
            assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
            page.locator('#search').fill(ark)
            page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
            search=page.locator('#results').text_content()
            assert 'Pactols validé en 2026' in search and code in search,search
        page.locator('#year').evaluate(
            "(el) => { el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true})); }")
        page.locator('#year').dispatch_event('change')
        page.wait_for_function(
            "() => document.querySelector('#year-label')?.textContent === '1975'",
            timeout=30000)
        detail=page.locator('#detail').text_content()
        assert '26678/pcrt7B7bs9P5g2' in detail and '2026 seulement' in detail,detail
        page.goto(url+'/lieux/?region=paca&code=04045&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('04045')",
            timeout=60000)
        cereste=page.locator('#detail').text_content()
        assert 'Aucun alignement Pactols individuellement validé' in cereste,cereste
        assert '26678/pcrtHxveTzUMik' not in cereste
        assert not errors,errors
        print('PACA_937_NAVIGATEUR_OK — Rousset, Esparron 2026 et 1975, Céreste UUID réservée')
        browser.close()

if __name__=='__main__':
    main()
