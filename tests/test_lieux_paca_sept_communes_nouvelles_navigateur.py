"""Chromium : sept communes nouvelles 2026, ancien Abriès exclu mais nouvelle validée indirectement."""
from test_lieux_corse_pactols_navigateur import serveur
CASES=[
 ("04033","26678/pcrtDcVUj2Mdw9","Ubaye-Serre-Ponçon"),
 ("04120","26678/pcrtjDzQ2Y9N5o","Val d'Oronaye"),
 ("05024","26678/pcrtAUevxwngAh","Valdoule"),
 ("05039","26678/pcrtFGmyycRjcC","Aubessagne"),
 ("05053","26678/pcrtKc33Ttmi9L","Garde-Colombe"),
 ("05101","26678/pcrt2BsRDBxggr","Vallouise-Pelvoux"),
 ("05118","26678/pcrtjKbaVOnEjn","Val Buëch-Méouge"),
]
def main():
 from playwright.sync_api import sync_playwright
 with serveur() as url,sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1320,'height':900})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  for code,ark,name in CASES:
   page.goto(url+'/lieux/?region=paca&code='+code+'&annee=2026&niveau=commune',
      wait_until='domcontentloaded',timeout=45000)
   page.wait_for_function("() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",timeout=60000)
   page.wait_for_function("(a) => document.querySelector('#detail')?.textContent.includes(a)",arg=ark,timeout=30000)
   detail=page.locator('#detail').text_content()
   assert name in detail and 'Correspondance Pactols–COG' in detail and '2026 seulement' in detail,detail
   assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
  page.goto(url+'/lieux/?region=paca&code=05001&annee=2026&niveau=commune',
     wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('05001')",timeout=30000)
  detail=page.locator('#detail').text_content()
  assert '26678/pcrtm96gvvfnwmggc9z0wrxn' in detail,detail
  assert 'convergence entre Pactols, Wikidata et le COG officiel' in detail,detail
  assert '26678/pcrtGQ7nGPZN7K' not in detail
  page.goto(url+'/lieux/?region=paca&code=04045&annee=2026&niveau=commune',
     wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('26678/pcrtHxveTzUMik')",timeout=30000)
  page.goto(url+'/lieux/?region=paca&code=04033&annee=1975&niveau=commune',
     wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function("() => document.querySelector('#detail')?.textContent.includes('26678/pcrtDcVUj2Mdw9')",timeout=30000)
  detail=page.locator('#detail').text_content()
  assert '2026 seulement' in detail
  assert not errors,errors
  print('PACA_946_NAVIGATEUR_RETRO_OK — sept communes nouvelles, Abriès-Ristolas distincte, Céreste conservée')
  browser.close()
if __name__=='__main__':main()
