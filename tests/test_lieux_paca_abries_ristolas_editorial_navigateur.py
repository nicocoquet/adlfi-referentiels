"""Chromium : Abriès-Ristolas est distincte d'Abriès, sans exactMatch INSEE direct."""
from test_lieux_corse_pactols_navigateur import serveur

def main():
 from playwright.sync_api import sync_playwright
 with serveur() as url,sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':900})
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  code='05001';ark='26678/pcrtm96gvvfnwmggc9z0wrxn'
  page.goto(url+'/lieux/?region=paca&code='+code+'&annee=2026&niveau=commune',
            wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function(
   "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
   timeout=60000)
  page.wait_for_function(
   "(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
   arg=ark,timeout=30000)
  d=page.locator('#detail').text_content()
  assert 'Abriès-Ristolas' in d and 'Correspondance Pactols–COG' in d,d
  assert 'convergence entre Pactols, Wikidata et le COG officiel' in d,d
  assert 'sans' not in d or 'Pactols ne fournit pas d’exactMatch INSEE direct' in d,d
  assert '26678/pcrtGQ7nGPZN7K' not in d,d
  assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
  page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
  page.locator('#search').fill(ark)
  page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
  found=page.locator('#results').text_content()
  assert 'Pactols validé en 2026' in found and code in found,found
  page.goto(url+'/lieux/?region=paca&code='+code+'&annee=1975&niveau=commune',
            wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function("(ark) => document.querySelector('#detail')?.textContent.includes(ark)",
                         arg=ark,timeout=30000)
  d=page.locator('#detail').text_content()
  assert 'Abriès' in d and '2026' in d,d
  assert not errors,errors
  print('PACA_946_NAVIGATEUR_OK — Abriès-Ristolas, chaîne indirecte, ancienne identité préservée')
  browser.close()
if __name__=='__main__':main()
