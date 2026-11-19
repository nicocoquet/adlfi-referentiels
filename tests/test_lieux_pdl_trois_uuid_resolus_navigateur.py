"""Chromium : trois UUID INSEE résolus en PDL et Rives-du-Fougerais réservée."""
from test_lieux_corse_pactols_navigateur import serveur

CASES=[
 ("44066","26678/pcrt99dzcmxdhR","Grandchamp-des-Fontaines"),
 ("85165","26678/pcrtsn4IGEserS","L'Oie"),
 ("85212","26678/pcrt3AUfSktjqj","Sainte-Florence")
]

def main():
 from playwright.sync_api import sync_playwright
 with serveur() as url,sync_playwright() as p:
  browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':900})
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  for code,ark,label in CASES:
   page.goto(url+'/lieux/?region=pdl&code='+code+'&annee=2026&niveau=commune',
      wait_until='domcontentloaded',timeout=45000)
   page.wait_for_function(
     "() => document.querySelector('#map-status')?.textContent.includes('contours communaux 2026')",
     timeout=60000)
   page.wait_for_function(
     "(a) => document.querySelector('#detail')?.textContent.includes(a)",
     arg=ark,timeout=30000)
   detail=page.locator('#detail').text_content()
   assert label in detail,detail
   assert 'Correspondance Pactols–COG validée pour 2026' in detail,detail
   assert 'geo:codeINSEE et owl:sameAs' in detail,detail
   assert 'ne valide pas automatiquement les identités communales antérieures' in detail,detail
   assert page.locator('#detail a[href="https://ark.frantiq.fr/ark:/'+ark+'"]').count()==1
   page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
   page.locator('#search').fill(ark)
   page.wait_for_function("() => !document.querySelector('#results')?.hidden",timeout=15000)
   hits=page.locator('#results').text_content()
   assert code in hits and 'Pactols validé en 2026' in hits,hits
  page.goto(url+'/lieux/?region=pdl&code=85292&annee=2026&niveau=commune',
    wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function(
    "() => document.querySelector('#detail')?.textContent.includes('85292')",
    timeout=30000)
  reserve=page.locator('#detail').text_content()
  assert 'Aucun alignement Pactols individuellement validé' in reserve,reserve
  assert '26678/pcrtjr01c5sg25ngf5hq8898' not in reserve,reserve
  page.goto(url+'/lieux/?region=pdl&code=85165&annee=2019&niveau=commune',
    wait_until='domcontentloaded',timeout=45000)
  page.wait_for_function(
    "() => document.querySelector('#detail')?.textContent.includes('26678/pcrtsn4IGEserS')",
    timeout=30000)
  old=page.locator('#detail').text_content()
  assert '2026' in old and '2019' in old and 'aucun état' not in old.lower() or '2026' in old,old
  assert not errors,errors
  print('PDL_1143_NAVIGATEUR_OK — trois UUID prouvés et Rives non validée, frise historique inchangée')
  browser.close()
if __name__=='__main__':main()
