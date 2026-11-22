"""Recette Chromium ciblée de la publication Organismes 1.52 (A02–A03)."""
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))

        def consulter(ident):
            page.goto(url+'/organismes/?recette152='+ident+'#'+ident,
                      wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "(id) => document.querySelector('#details')?.open && "
                "document.querySelector('#detail-content .detail-head .ident')?.textContent.trim()===id",
                arg=ident,timeout=45000)
            return page.locator('#details')

        def echelon():
            return page.locator('#detail-content dt').filter(
                has_text='Échelon institutionnel').locator(
                'xpath=following-sibling::dd[1]').inner_text().strip()

        consulter('SER-0027')
        assert page.locator('#dataset-version').inner_text()=='1.58'
        assert echelon()=='Régional',echelon()

        for ident,expected in [
            ('SER-0047','Départemental'),
            ('SER-0151','National'),
            ('SER-0152','National'),
            ('SER-0191','National'),
            ('SER-0197','Non applicable'),
            ('SER-0107','Non applicable'),
        ]:
            modal=consulter(ident)
            assert echelon()==expected,(ident,echelon())
            if ident in ('SER-0151','SER-0152'):
                assert modal.locator('button.attachment-link[data-detail="ORG-0023"]').count()>=1,ident
            if ident=='SER-0191':
                assert modal.locator('button.attachment-link[data-detail="ORG-0137"]').count()>=1

        for ident,unverified in [('SER-0178','ORG-0700'),('SER-0202','ORG-0755')]:
            modal=consulter(ident)
            assert echelon()=='Non renseigné',(ident,echelon())
            assert modal.locator(f'button.attachment-link[data-detail="{unverified}"]').count()==0

        assert not errors,errors
        print('ORGANISMES_152_NAVIGATEUR_OK : historiques, non applicables, rattachements provisoires')
        browser.close()


if __name__=='__main__':
    main()
