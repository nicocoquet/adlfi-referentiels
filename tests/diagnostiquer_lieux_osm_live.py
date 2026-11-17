"""Diagnostic réseau réel du fond de carte du référentiel Lieux."""
import json,os
from playwright.sync_api import sync_playwright
URL=os.environ.get("LIEUX_URL","https://nicocoquet.github.io/adlfi-referentiels/lieux/")
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=["--no-sandbox"])
 page=b.new_page(viewport={"width":1440,"height":980})
 errors=[];requests=[]
 page.on("console",lambda m:errors.append("console "+m.type+": "+m.text) if m.type=="error" else None)
 page.on("pageerror",lambda e:errors.append("pageerror "+str(e)))
 page.on("requestfailed",lambda req:requests.append({"url":req.url,"error":req.failure}))
 page.on("response",lambda resp:requests.append({"url":resp.url,"status":resp.status}) if ("openstreetmap.org" in resp.url or "leaflet" in resp.url or "lieux-multiechelon" in resp.url) else None)
 try:
  resp=page.goto(URL,wait_until="domcontentloaded",timeout=45000)
  page.wait_for_timeout(12000)
  stats=page.evaluate("""() => ({
    title:document.title,
    leaflet:typeof window.L,
    status:document.querySelector('#map-status')?.textContent,
    maprect:document.querySelector('#map')?.getBoundingClientRect().toJSON(),
    mapClass:document.querySelector('#map')?.className,
    tileCount:document.querySelectorAll('.leaflet-tile').length,
    tileLoaded:[...document.querySelectorAll('.leaflet-tile')].filter(t=>t.complete&&t.naturalWidth>0).length,
    tileBroken:[...document.querySelectorAll('.leaflet-tile')].filter(t=>t.complete&&t.naturalWidth===0).length,
    pane:!!document.querySelector('.leaflet-tile-pane'),
    layerCanvas:document.querySelectorAll('.leaflet-overlay-pane canvas').length,
    css:document.querySelector('#map')?getComputedStyle(document.querySelector('#map')).height:null
  })""")
  print("OSM_DIAGNOSTIC",json.dumps({"url":URL,"http_status":resp.status if resp else None,"stats":stats,"errors":errors[:20],"network":requests[:50]},ensure_ascii=False))
  page.screenshot(path="/tmp/lieux-osm-live-diagnostic.png",full_page=False)
 except Exception as exc:
  print("OSM_DIAGNOSTIC_ERROR",repr(exc),json.dumps({"errors":errors,"network":requests[:50]},ensure_ascii=False))
 finally:b.close()
