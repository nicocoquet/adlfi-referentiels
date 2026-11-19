"""Chromium : les trois nouvelles communes sont visibles, les ARK historiques ne sont pas promus."""
from test_lieux_corse_pactols_navigateur import serveur
CASES=[("49244","26678/pcrtVBIl6UNl1S","26678/pcrtE0bVL7JsdM"),
       ("53255","26678/pcrtwUykeFf31u","26678/pcrts0lDLWcVyJ"),
       ("72137","26678/pcrtoVf9Ovfyy7","26678/pcrtg6rwdnGM9r")]
def main():
 from playwright.sync_api import sync_playwright
 with serveur() as url,sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=["--no-sandbox"])
  page=b.new_page(viewport={"width":1280,"height":900})
  errors=[]
  page.on("pageerror",lambda e:errors.append(str(e)))
  for code,ark,old in CASES:
   page.goto(url+"/lieux/?region=pdl&code="+code+"&annee=2026&niveau=commune",
             wait_until="domcontentloaded",timeout=45000)
   page.wait_for_function("(ark)=>document.querySelector('#detail')?.textContent.includes(ark)",
                          arg=ark,timeout=60000)
   d=page.locator("#detail").text_content()
   assert "Correspondance Pactols–COG validée pour 2026" in d,(code,d)
   assert old not in d,(code,d)
   page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
   page.locator('#search').fill(ark)
   page.wait_for_function("()=>!document.querySelector('#results')?.hidden",timeout=15000)
   assert "Pactols validé en 2026" in page.locator("#results").text_content()
   page.locator('#search-tool').evaluate("(el) => { el.open = true; }")
   page.locator('#search').fill(old)
   page.wait_for_timeout(350)
   hits=page.locator("#results").text_content()
   assert "Pactols validé en 2026" not in hits or code not in hits,(code,hits)
  assert not errors,errors
  b.close()
  print("PDL_TROIS_COLLISIONS_NAVIGATEUR_OK")
if __name__=="__main__":main()
