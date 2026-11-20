"""Chromium : les géométries communales sont chargées selon la vue, sans perdre les fiches."""
from __future__ import annotations

from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':920})
        seen=[]
        errors=[]
        page.on('request',lambda req: seen.append(req.url))
        page.on('pageerror',lambda err: errors.append(str(err)))

        def count(id):
            return sum('contours-2026-'+id+'.geojson' in u for u in seen)

        def select(name):
            page.locator('#zoom').evaluate(
                "(el, value) => { el.value=value; el.dispatchEvent(new Event('change',{bubbles:true})); }",
                name
            )

        page.goto(url+'/lieux/?zoom=pdl&niveau=commune&annee=2026',
                  wait_until='domcontentloaded',timeout=45000)
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
            timeout=60000)
        status=page.locator('#map-status').text_content()
        assert 'Pays de la Loire' in status,status
        assert count('pdl')==1,seen
        # Avec une grande fenêtre, le cadre du PDL peut aussi recouper BFC :
        # une seconde couche limitrophe est alors attendue, pas une erreur.
        assert count('paca')==0 and count('corse')==0,seen
        assert count('bfc') in (0,1),seen
        bfc_initial=count('bfc')

        # Passer d'une région métropolitaine à une autre ne télécharge que la
        # couche demandée ; les mêmes fichiers ne sont pas rechargés au retour.
        select('corse')
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('Corse')",
            timeout=60000)
        assert count('corse')==1,seen
        assert count('bfc')==bfc_initial,seen
        # La Corse peut recouper le cadre PACA avec un écran très large :
        # les régions limitrophes dans la fenêtre ne doivent pas être masquées.
        select('pdl')
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('Pays de la Loire')",
            timeout=60000)
        assert count('pdl')==1,seen

        # Recherche d'une commune qui n'est pas actuellement affichée :
        # elle doit provoquer le chargement de la région puis ouvrir sa fiche.
        page.locator('#search-tool').evaluate("(el) => { el.open=true; }")
        # Rechercher l'ARK de l'Afa actuelle : le libellé seul retrouve aussi
        # l'ancien code corse 20001 (avant la recodification de 1976).
        page.locator('#search').fill('26678/pcrtgs2LLPYow2')
        page.wait_for_function(
            "() => !document.querySelector('#results')?.hidden && document.querySelector('#results')?.textContent.includes('2A001')",
            timeout=20000)
        # Le résultat exact en tête est une commune corse.
        page.locator('#results button').first.click()
        page.wait_for_function(
            "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtgs2LLPYow2')",
            timeout=60000)
        assert 'Corse' in page.locator('#map-status').text_content()
        assert count('corse')==1,seen

        # Zoom national : conserver les cinq régions 2026, sans tronquer la
        # couverture déjà publiée dans le modèle initial.
        select('metropole')
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('9054 contours communaux 2026')",
            timeout=60000)
        assert all(count(id)==1 for id in ('paca','corse','pdl','bfc','normandie')),seen

        # En année historique, la source 2026 n'est jamais qualifiée d'état
        # ancien. Le repère reste désactivable.
        page.locator('#year').evaluate(
            "(el) => {el.value='1975'; el.dispatchEvent(new Event('input',{bubbles:true}));}")
        page.locator('#year').dispatch_event('change')
        page.wait_for_function(
            "() => document.querySelector('#map-status')?.textContent.includes('aucun contour communal historique 1975')",
            timeout=60000)
        assert not errors,errors
        print('LIEUX_CHARGEMENT_PROGRESSIF_NAVIGATEUR_OK — régions ciblées, cache, recherche distante, national, 1975')
        browser.close()


if __name__=='__main__':
    main()
