"""Chromium : PACA — nouvel ARK, ancien ARK Dévoluy, 1975 et exception COG."""
from __future__ import annotations
from test_lieux_corse_pactols_navigateur import serveur

def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url,sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        code='04001'
        ark='26678/pcrtzU15KxxGTs'
        page.goto(url+'/lieux/?region=paca&code='+code+'&annee=2026&niveau=commune',
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
        hist=page.locator('#detail').text_content()
        assert ark in hist and '2026 seulement' in hist,hist
        # Dévoluy conserve le choix éditorial du pilote malgré un second ARK dans le RDF.
        page.goto(url+'/lieux/?region=paca&code=05139&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtSeD2WMEIYA')",
            timeout=60000)
        assert '26678/pcrt2XYqgMPgx5' not in page.locator('#detail').text_content()
        # Ubaye-Serre-Ponçon : deux ARK concurrents, aucune validation inférée.
        page.goto(url+'/lieux/?region=paca&code=04033&annee=2026&niveau=commune',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('04033')",
            timeout=60000)
        negative=page.locator('#detail').text_content()
        assert 'Aucun alignement Pactols individuellement validé' in negative,negative
        assert '26678/pcrtC1Vi7jqzBS' not in negative
        assert not errors,errors
        print('PACA_935_NAVIGATEUR_OK — nouveau code, ancien Dévoluy, année 1975, exception 04033')
        browser.close()

if __name__=='__main__':
    main()
