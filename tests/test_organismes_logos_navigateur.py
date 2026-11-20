"""Recette Chromium : logos agrandis et reproduits dans la fiche détaillée."""
from test_lieux_corse_pactols_navigateur import serveur


def main():
    from playwright.sync_api import sync_playwright
    with serveur() as url, sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1360,'height':900})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url+'/organismes/',wait_until='domcontentloaded')
        page.locator('#query').fill('Institut national de recherches archéologiques préventives')
        card=page.locator('#cards .authority-card[data-id="ORG-0008"]')
        card.wait_for(timeout=30000)
        logo=card.locator('.lab-primary-logo')
        logo.wait_for()
        assert logo.evaluate("(e)=>e.complete && e.naturalWidth>0")
        padding=logo.evaluate("(e)=>parseFloat(getComputedStyle(e).paddingLeft)")
        assert padding<=4, f"Le logo reste trop petit : marge {padding}px"

        def detail(identifier):
            page.goto(url+'/organismes/?fiche='+identifier+'#'+identifier,
                      wait_until='domcontentloaded',timeout=45000)
            page.wait_for_function(
                "() => document.querySelector('#details')?.open && "
                "document.querySelector('#detail-content')?.textContent.length>70",
                timeout=45000)
        detail('ORG-0008')
        image=page.locator('#detail-content .detail-brand-logo')
        assert image.count()==1
        assert image.get_attribute('src').endswith('ORG-0008.jpg')
        assert image.evaluate("(e)=>e.complete && e.naturalWidth>0")
        rect=image.bounding_box()
        assert rect and rect['width']>=100, rect
        assert 'Institut national' in page.locator('#detail-content .detail-head').inner_text()

        detail('ORG-0068')
        assert page.locator('#detail-content .detail-brand').count()==0, (
            'Une autorité sans JPEG ne doit pas afficher de logo factice dans la fiche')

        page.set_viewport_size({'width':400,'height':800})
        detail('ORG-0008')
        image=page.locator('#detail-content .detail-brand-logo')
        assert image.is_visible()
        rect=image.bounding_box()
        assert rect and rect['width']<=83, rect
        assert not errors, errors
        print('ORGANISMES_LOGOS_NAVIGATEUR_OK — card, fiche, JPEG absent, mobile')
        browser.close()


if __name__=='__main__':
    main()
