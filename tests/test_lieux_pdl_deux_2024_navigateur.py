"""Chromium : Ingrandes 2024/Essarts 2024, aucune promotion des anciens ARK."""
from test_lieux_corse_pactols_navigateur import serveur
CASES=[
 ("49160","26678/pcrtj64zr6gnns4mnfd2828b","26678/pcrtQBSwT6fBDW","Wikidata Q123475717"),
 ("85084","26678/pcrt0PrU3oVWxo","26678/pcrtFmygG5m3QZ","MOD21")
]
def main():
 from playwright.sync_api import sync_playwright
 with serveur() as url,sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=["--no-sandbox"])
  page=b.new_page(viewport={"width":1280,"height":900})
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  for code,ark,old,proof in CASES:
   page.goto(url+"/lieux/?region=pdl&code="+code+"&annee=2026&niveau=commune",
             wait_until="domcontentloaded",timeout=45000)
   page.wait_for_function("(ark)=>document.querySelector('#detail')?.textContent.includes(ark)",
                          arg=ark,timeout=60000)
   d=page.locator("#detail").text_content()
   assert proof in d,(code,d)
   assert old not in d,(code,d)
   page.locator("#search").fill(ark)
   page.wait_for_function("()=>!document.querySelector('#results')?.hidden",timeout=15000)
   assert "Pactols validé en 2026" in page.locator("#results").text_content()
   page.locator("#search").fill(old)
   page.wait_for_timeout(350)
   hits=page.locator("#results").text_content()
   assert "Pactols validé en 2026" not in hits or code not in hits,(code,hits)
  assert not errors,errors
  b.close()
  print("PDL_DEUX_2024_NAVIGATEUR_OK — MOD32 distinct MOD21")
if __name__=="__main__":main()
