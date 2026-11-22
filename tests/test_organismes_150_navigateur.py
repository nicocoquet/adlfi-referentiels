"""Recette Chromium 1.52 : conservation des liens et du parcours institutionnel."""
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))

        def consulter(ident):
            # Une navigation ne changeant que le fragment n'initialise pas
            # à nouveau l'application : changer aussi l'URL de requête.
            page.goto(url+'/organismes/?fiche='+ident+'#'+ident,
                      wait_until='domcontentloaded',timeout=45000)
            expected='ORG-0747' if ident=='SER-0063' else ident
            page.wait_for_function(
                "(expected) => document.querySelector('#details')?.open && "
                "document.querySelector('#detail-content .detail-head .ident')?.textContent.trim()===expected",
                arg=expected, timeout=45000)
            return page.locator('#details')

        # Ancien identifiant conservé pour la navigation ; l'autorité est ORG.
        modal=consulter('SER-0063')
        assert page.locator('#dataset-version').inner_text()=='1.62'
        assert page.url.endswith('#ORG-0747'),page.url
        head=modal.locator('.detail-head').inner_text()
        assert 'ORG-0747' in head and 'Groupe de recherche archéologique sous-marine' in head,head
        logo=modal.locator('.detail-brand-logo')
        assert logo.count()==1
        assert logo.get_attribute('src').endswith('ORG-0747.jpg')
        assert logo.evaluate('(e)=>e.complete && e.naturalWidth>0')
        federation=modal.locator('button.attachment-link[data-detail="ORG-0120"]')
        assert federation.count()==1,'Affiliation GRASM → FFESSM absente'
        federation.click()
        modal.locator('.detail-head').get_by_text('Fédération française').wait_for(timeout=15000)
        assert modal.locator('button.attachment-link[data-detail="ORG-0747"]').count()==1, (
            'Le lien réciproque FFESSM → GRASM manque')

        # Les nouveaux liens fédéraux doivent être navigables dans les deux sens.
        for membre,federation in [
            ('ORG-0069','ORG-0120'), ('ORG-0419','ORG-0120'),
            ('ORG-0521','ORG-0120'), ('ORG-0355','ORG-0701')
        ]:
            fiche=consulter(membre)
            assert fiche.locator(f'button.attachment-link[data-detail="{federation}"]').count()>=1, membre
            texte=fiche.locator('#detail-content').inner_text()
            assert 'Dates non documentées' in texte, membre
            inverse=consulter(federation)
            assert inverse.locator(f'button.attachment-link[data-detail="{membre}"]').count()>=1, membre

        # Filiations institutionnelles anciennes sans fausse succession totale.
        iramat=consulter('ORG-0299')
        assert iramat.locator('button[data-detail="ORG-0393"]').count()>=1, (
            'Continuité documentée entre IRAMAT 5060 et 7065 absente')
        ceb=consulter('SER-0197')
        assert ceb.locator('button[data-detail="ORG-0299"]').count()>=1
        lmc=consulter('SER-0198')
        assert lmc.locator('button[data-detail="ORG-0299"]').count()>=1
        cea=consulter('SER-0199')
        assert cea.locator('button[data-detail="ORG-0280"]').count()>=1

        # La SFECAG est validée, avec une dénomination historique autonome.
        sfecag=consulter('ORG-0751')
        text=sfecag.locator('#detail-content').inner_text()
        assert 'Groupe d’étude de la céramique antique en Gaule' in text
        assert '1962' in text and '1973' in text
        assert 'Validation documentaire' in text and 'Validée' in text
        assert 'Qualification documentaire à vérifier' not in text

        # Le musée de Riez reste qualifié comme incertain et son rattachement
        # municipal non validé ne doit pas être présenté comme établi.
        riez=consulter('SER-0202')
        text=riez.locator('#detail-content').inner_text()
        assert 'Qualification documentaire à vérifier' in text
        assert 'À confirmer' in text
        assert riez.locator('button.attachment-link[data-detail="ORG-0755"]').count()==0
        assert not errors,errors
        print('ORGANISMES_151_NAVIGATEUR_OK — quatre liens fédéraux, alias GRASM, IRAMAT, CEB, LMC, CEA, SFECAG, Riez')
        browser.close()


if __name__=='__main__':
    main()
