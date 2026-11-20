"""Chromium : compétence Inrap explicitement affichée, jamais inférée."""
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1300,'height':900})
        errs=[]
        page.on('pageerror',lambda err:errs.append(str(err)))

        def consulter(ident):
            page.goto(url+'/organismes/#'+ident,
                      wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "() => document.querySelector('#details')?.open && "
                "document.querySelector('#detail-content')?.textContent.length > 80",
                timeout=60000)
            return page.locator('#detail-content').text_content()

        inrap=consulter('SER-0172')
        assert 'Inrap Grand Ouest' in inrap,inrap[:800]
        assert 'Échelon institutionnel' in inrap and 'National' in inrap,inrap
        assert 'Périmètre de compétence' in inrap and 'Interrégional' in inrap,inrap

        org=consulter('ORG-0008')
        assert 'Institut national de recherches archéologiques préventives' in org,org[:800]
        assert 'Périmètre de compétence' in org,org[:1000]

        unrelated=consulter('SER-0149')
        assert 'United Kingdom Hydrographic Office' in unrelated,unrelated[:500]
        assert 'Périmètre de compétence' not in unrelated,unrelated[:1200]
        assert not errs,errs
        print('ORGANISMES_COMPETENCE_NAVIGATEUR_OK — Inrap échelon national et compétence interrégionale')
        browser.close()


if __name__=='__main__':
    main()
