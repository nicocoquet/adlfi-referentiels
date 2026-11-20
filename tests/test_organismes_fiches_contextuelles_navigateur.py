"""Chromium : une fiche hors catalogue est accessible depuis un SER visible.

Contrat : ne pas créer de cartouche autonome ni dégrader le statut de validation.
"""
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda err:errors.append(str(err)))
        page.goto(url+'/organismes/#SER-0180',wait_until='domcontentloaded')
        page.wait_for_function(
            "() => document.querySelector('#details')?.open && "
            "document.querySelector('#detail-content')?.textContent.includes('Musée de Préhistoire régionale')",
            timeout=45000)
        modal=page.locator('#details')
        parent=modal.locator('button.attachment-link[data-detail="ORG-0697"]')
        assert parent.count()==1,'Le lien du musée vers la ville hors catalogue doit être actif'
        parent.click()
        page.wait_for_function(
            "() => document.querySelector('#detail-content .detail-head')?.textContent.includes('Ville de Menton')",
            timeout=15000)
        assert 'Autorité hors catalogue' in modal.locator('.detail-context-note').inner_text()
        assert page.locator('#cards .authority-card[data-id="ORG-0697"]').count()==0
        child=modal.locator('button.attachment-link[data-detail="SER-0180"]')
        assert child.count()==1,'Lien retour vers le musée depuis la collectivité contextuelle'
        child.click()
        page.wait_for_function(
            "() => document.querySelector('#detail-content .detail-head')?.textContent.includes('Musée de Préhistoire régionale')",
            timeout=15000)
        assert modal.locator('.detail-context-note').count()==0
        page.locator('#close-details').click()
        page.locator('#query').fill('Ville de Menton')
        page.wait_for_timeout(250)
        assert page.locator('#cards .authority-card[data-id="ORG-0697"]').count()==0
        assert not errors,errors
        print('ORGANISMES_FICHES_CONTEXTUELLES_OK — SER→ORG→SER, pas de cartouche hors catalogue')
        browser.close()


if __name__=='__main__':
    main()
