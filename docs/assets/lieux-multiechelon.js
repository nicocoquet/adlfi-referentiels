(()=>{
'use strict';
const geo={layers:{},edition_IGN:{'2015':'2015-03-04','2016':'2016-06-28'},
  source_COG:{'2015':'https://www.insee.fr/fr/information/2560698','2016':'https://www.insee.fr/fr/information/2114819'}};
const commun={regions:{},pactols:null};
const core=window.AdlfiLieuxChronologieCore;
const $=id=>document.getElementById(id);
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const label={region:'Région',departement:'Département',commune:'Commune',arrondissement:'Arrondissement municipal',territoire:'Collectivité ou territoire'};
const ids=['paca','corse','pdl','bfc'];
const nomZones={paca:'Provence-Alpes-Côte d’Azur',corse:'Corse',pdl:'Pays de la Loire',bfc:'Bourgogne-Franche-Comté'};
const views={metropole:[[41.2,-5.7],[51.4,10.1]],bfc:[[46.0,2.7],[49.0,8.0]],pdl:[[46.9,-2.7],[48.7,0.9]],corse:[[41.2,8.5],[43.2,9.7]],paca:[[42.8,4.2],[45.3,7.9]],antilles:[[1,-64],[16,-51]],indien:[[-22,43],[-10,57]],pacifique:[[-27,-160],[23,-130]],atlantique:[[46.5,-57.0],[47.3,-55.5]],taaf:[[-52,41],[-36,79]]};
const state={map:null, layer:null, reference:null, selected:null, bounds:new Map(), indexes:[], noMap:false};
let activeRequest=0;
const ROOT='../data/';
const layerData=new Map();
let communeDataPromise=null;
let timelineTimer=null;
function year(){return Number($('year').value)}
function level(){return $('level').value}
function refreshTimeline(){
 const y=year();
 $('year-label').textContent=String(y);
 $('year-label').value=String(y);
 $('year').setAttribute('aria-valuetext','Situation administrative au 1er janvier '+y);
 $('year-prev').disabled=y<=1943;
 $('year-next').disabled=y>=2026;
 $('year-now').disabled=y===2026;
}
function commitTimeline(){
 if(timelineTimer!==null){clearTimeout(timelineTimer);timelineTimer=null;}
 // Une fiche communale reste suivie d'une année à l'autre ; une fiche de géométrie
 // régionale/départementale doit être désélectionnée si son instantané change.
 if(state.selected?.kind==='admin'&&state.selected.year!==year())state.selected=null;
 render();
}
function setTimelineYear(value){
 $('year').value=String(Math.max(1943,Math.min(2026,value)));
 refreshTimeline();
 commitTimeline();
}
function selectedFeature(){if(state.selected?.kind!=='admin')return null;const x=state.selected;return geo.layers[String(x.year)]?.[x.level]?.find(f=>f.properties.code===x.code)||null}
async function loadJSON(url){
 const r=await fetch(url,{cache:'force-cache'});
 if(!r.ok)throw new Error('Source indisponible ('+r.status+') : '+url);
 return r.json();
}
function validateAdmin(index){
 if(index.schema!=='adlfi.lieux.admin.index.v1'||index.entries?.length!==227)throw new Error('Index administratif incohérent');
 const counts={'2015/region':0,'2015/departement':0,'2016/region':0,'2016/departement':0};
 for(const e of index.entries){
   const k=e.year+'/'+e.level;
   if(!Object.hasOwn(counts,k)||!e.code||!e.label||!e.champs?.length)throw new Error('Identifiant administratif inattendu');
   counts[k]++;
 }
 if(counts['2015/region']!==22||counts['2015/departement']!==96||
    counts['2016/region']!==13||counts['2016/departement']!==96)throw new Error('Cardinalités administratives incorrectes');
}
async function layerFor(y,l){
 const key=l+'s-'+y;
 if(!layerData.has(key)){
   const path=ROOT+'lieux-historique/'+key+'.geojson';
   layerData.set(key,loadJSON(path).then(fc=>{
     if(fc.type!=='FeatureCollection'||fc.provenance?.schema!=='adlfi.lieux.contours.historiques.v1'||
        fc.provenance?.cog_au_premier_janvier!==String(y)||fc.provenance?.pactols_valide!==false||
        fc.provenance?.edition_IGN!==geo.edition_IGN[String(y)]||
        fc.features?.length!==(l==='region'?(y===2015?22:13):96))
       throw new Error('Couche IGN/COG incompatible : '+key);
     for(const f of fc.features){
       if(f.properties?.annee!==y||f.properties?.niveau!==l||
          f.properties?.pactols_valide!==false)throw new Error('État géographique non validé : '+key);
     }
     geo.layers[String(y)]??={};
     geo.layers[String(y)][l]=fc.features;
     return fc.features;
   }).catch(e=>{layerData.delete(key);throw e}));
 }
 return layerData.get(key);
}
async function chargerCommunes2026(){
 if(!communeDataPromise){
  communeDataPromise=Promise.all(ids.map(id=>loadJSON(ROOT+'lieux-chronologie/contours-2026-'+id+'.geojson')))
    .then(arr=>{
      for(let i=0;i<ids.length;i++){
        const id=ids[i],fc=arr[i];
        if(fc.type!=='FeatureCollection'||fc.provenance?.millesime!==2026)
          throw new Error('Couche communale 2026 non datée : '+id);
        commun.regions[id].contours_2026=fc;
      }
      return communes2026();
    }).catch(e=>{communeDataPromise=null;throw e});
 }
 return communeDataPromise;
}
async function start(){
 if(!core || !window.AdlfiLieuxSearch)throw Error('Moteur du référentiel communal absent');
 const [pactols,adminIndex,...cogs]=await Promise.all([
   loadJSON(ROOT+'lieux.json'),
   loadJSON(ROOT+'lieux-historique/index.json'),
   ...ids.map(id=>loadJSON(ROOT+'lieux-chronologie/cog-'+id+'.json'))
 ]);
 if(pactols.autorites?.length!==103||pactols.totaux?.autorites_pactols!==103)
   throw Error('Les 103 autorités Pactols PACA doivent être conservées');
 commun.pactols=pactols;validateAdmin(adminIndex);
 for(let i=0;i<ids.length;i++){
   const id=ids[i],data=cogs[i];
   core.verifier(data);
   if(data.region!==id)throw Error('Corps communal mal identifié : '+id);
   commun.regions[id]={cog:data};
 }
 $('year').value='2016';
 const former=window.AdlfiLieuxSearch.creerIndex(pactols.autorites);
 const variants=new Map(former.map(x=>[x.ark,x.champs]));
 state.indexes=ids.flatMap(id=>core.indexer(commun.regions[id].cog)
   .map(e=>({...e,zone:id,champs:[...new Set([...(e.champs||[]),...(e.kind==='pactols'?(variants.get(e.ark)||[]):[])])]})))
   .concat(adminIndex.entries);
 const params=new URLSearchParams(location.search);
 const zoom=params.get('zoom')||params.get('region');
 if(views[zoom])$('zoom').value=zoom;
 const levelParam=params.get('niveau');
 if(Object.hasOwn(label,levelParam))$('level').value=levelParam;
 else if(params.get('region'))$('level').value='commune';
 const y=Number(params.get('annee'));
 if(Number.isInteger(y)&&y>=1943&&y<=2026)$('year').value=String(y);
 const code=params.get('code'),zone=params.get('zone')||params.get('region');
 if(code && ids.includes(zone))state.selected={kind:'commune',code,zone,year:year()};
 const hash=new URLSearchParams(location.hash.replace(/^#/,'')),ark=hash.get('ark');
 if(ark){const found=state.indexes.find(x=>x.kind==='pactols'&&x.ark===ark);
   if(found){state.selected={kind:'commune',code:found.code,zone:found.zone,year:year(),ark};
     $('level').value='commune';$('year').value='2026';}}
 if(window.L){
  state.map=L.map('map',{scrollWheelZoom:false,preferCanvas:true}).setView([46.5,2.2],6);
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png',{maxZoom:18,
    attribution:'© <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">contributeurs OpenStreetMap</a>'}).addTo(state.map);
  state.map.attributionControl.addAttribution('Surcouches : IGN GEOFLA / Insee COG / référentiel AdlFI');
  frame();
 }else{state.noMap=true;$('map-status').textContent='Leaflet indisponible : la recherche et les fiches restent accessibles.'}
 $('zoom').addEventListener('change',()=>{frame();updateUrl()});
 $('level').addEventListener('change',()=>{state.selected=null;render()});
 $('year').addEventListener('input',()=>{
   refreshTimeline();
   if(timelineTimer!==null)clearTimeout(timelineTimer);
   timelineTimer=setTimeout(commitTimeline,160);
 });
 $('year').addEventListener('change',commitTimeline);
 $('year-prev').addEventListener('click',()=>setTimelineYear(year()-1));
 $('year-next').addEventListener('click',()=>setTimelineYear(year()+1));
 $('year-now').addEventListener('click',()=>setTimelineYear(2026));
 $('reference').addEventListener('change',render);
 $('reset').addEventListener('click',frame);
 $('search').addEventListener('input',search);
 $('search').addEventListener('keydown',e=>{
   if(e.key==='Escape')hideResults();
   else if(e.key==='Enter'&&!$('results').hidden){
      const a=$('results').querySelector('button');if(a)a.click();
   }
 });
 await render();
 if(state.selected)focusSelection();
}
function updateUrl(){
 const u=new URL(location.href);
 u.searchParams.set('zoom',$('zoom').value);
 u.searchParams.set('niveau',level());
 u.searchParams.set('annee',String(year()));
 u.searchParams.delete('region');
 if(state.selected?.kind==='commune'){
   u.searchParams.set('code',state.selected.code);
   u.searchParams.set('zone',state.selected.zone);
 }else{u.searchParams.delete('code');u.searchParams.delete('zone')}
 history.replaceState(null,'',u);
}
function frame(){
 if(!state.map)return;
 const v=views[$('zoom').value];
 if(v)state.map.fitBounds(v,{padding:[16,16],animate:false});
}
function destroy(){if(state.map){if(state.layer)state.map.removeLayer(state.layer);if(state.reference)state.map.removeLayer(state.reference)}state.layer=null;state.reference=null;state.bounds.clear()}
function color(l){return l==='region'?'#286e83':l==='departement'?'#597f8c':'#8d9ca6'}
function geoLayer(features,{reference=false}={}){
 if(!state.map)return null;
 return L.geoJSON({type:'FeatureCollection',features},{renderer:L.canvas(),interactive:!reference,
   style:f=>({color:reference?'#747e89':color(f.properties.niveau||'commune'),weight:reference?.7:1.15,
      opacity:reference?.7:.9,fillColor:reference?'#c7ccd0':'#5d9cab',fillOpacity:reference?.025:.10,
      dashArray:reference?'4,5':null}),
   onEachFeature(f,layer){if(!reference){
      const p=f.properties;
      const key=p.niveau==='commune'?'com:'+p.code:p.annee+'/'+p.niveau+'/'+p.code;
      state.bounds.set(key,layer);
      layer.bindTooltip(escape(p.nom)+' · '+escape(p.code));
      layer.on('click',()=>choose(p.niveau==='commune'?{kind:'commune',code:p.code,zone:p.zone,year:year()}:{kind:'admin',code:p.code,level:p.niveau,year:p.annee}));
   }}
 }).addTo(state.map);
}
function communes2026(){return ids.flatMap(id=>commun.regions[id].contours_2026.features.map(f=>({type:'Feature',geometry:f.geometry,properties:{...f.properties,code:f.properties.code||f.properties.code_insee,nom:f.properties.nom||f.properties.libelle,zone:id,niveau:'commune',annee:2026}})))}
function showEmpty(title,message){$('map-status').textContent=title+'. '+message;}
async function render(){
 refreshTimeline();
 const sequence=++activeRequest;
 const y=year(),l=level(),current=state.selected;
 $('map-title').textContent=(label[l]||l)+' · état au 1er janvier '+y;
 $('map-subtitle').textContent='Fond OSM contemporain · état administratif '+y;
 $('map-status').textContent='Chargement de la couche et des fiches du référentiel…';
 let features=[],desc='';
 try{
  if((l==='region'||l==='departement')&&(y===2015||y===2016)){
    features=await layerFor(y,l);
    desc=features.length+' contours '+(l==='region'?'régionaux':'départementaux')+
      ' · IGN GEOFLA '+geo.edition_IGN[String(y)]+', généralisation à 100 m (affichage seulement).';
  }else if(l==='commune'&&y===2026){
    features=await chargerCommunes2026();
    desc=features.length+' contours communaux 2026 sur les quatre régions pilotes, sans alignement Pactols inféré.';
  }else if(l==='commune'){
    desc='Les états COG communaux restent consultables par recherche pour '+y+
      ', mais aucun contour communal historique '+y+' n’est qualifié. Le fond OpenStreetMap est contemporain.';
  }else desc='Aucun contour '+(label[l]||l).toLowerCase()+' disponible et qualifié pour '+y+'.';
  let references=[];
  if($('reference').checked&&!(l==='commune'&&y===2026)){
    references=await chargerCommunes2026();
    desc+=' Les contours 2026 sont affichés uniquement comme repères actuels.';
  }
  if(sequence!==activeRequest)return;
  destroy();
  if(features.length)state.layer=geoLayer(features);
  if(references.length)state.reference=geoLayer(references,{reference:true});
  showEmpty('Échelon '+(label[l]||l)+' · '+y,desc);
  if(current?.kind==='admin'&&(current.year!==y||current.level!==l))state.selected=null;
  if(current?.kind==='commune'&&l!=='commune')state.selected=null;
  detail();updateUrl();
 }catch(err){
  if(sequence!==activeRequest)return;
  destroy();
  $('map-status').textContent='Données cartographiques indisponibles : '+err.message+
    '. La recherche documentaire et le fond OSM restent utilisables.';
  detail();updateUrl();console.error(err);
 }
}
function hideResults(){$('results').hidden=true;$('search').setAttribute('aria-expanded','false')}
function search(){
 const q=core.normaliser($('search').value);const ul=$('results');ul.replaceChildren();
 if(q.length<2){hideResults();return}
 const hits=state.indexes.filter(x=>{const parts=q.split(' ');return parts.every(t=>x.champs.some(ch=>ch.includes(t)))}).slice(0,22);
 for(const h of hits){const li=document.createElement('li'),btn=document.createElement('button');btn.type='button';
 const heading=document.createElement('strong');heading.textContent=h.label;
 const sub=document.createElement('small');sub.textContent=h.kind==='admin'?`${label[h.level]} · COG ${h.year} · ${h.code}`:
   `${h.kind==='pactols'?'Pactols validé en 2026':'Commune COG'} · ${nomZones[h.zone]} · ${h.code}`;
 btn.append(heading,sub);btn.addEventListener('click',()=>{
   if(h.kind==='admin'){ $('level').value=h.level;$('year').value=String(h.year);state.selected={kind:'admin',level:h.level,year:h.year,code:h.code}; }
   else{$('level').value='commune';state.selected={kind:'commune',code:h.code,zone:h.zone,year:year(),ark:h.kind==='pactols'?h.ark:null};}
   hideResults();render().then(focusSelection);
 });li.append(btn);ul.append(li)}
 if(!hits.length){const li=document.createElement('li');li.textContent='Aucun résultat dans les données étudiées.';li.style.padding='12px';ul.append(li)}
 ul.hidden=false;$('search').setAttribute('aria-expanded','true');
}
function focusSelection(){const x=state.selected;if(!x||!state.map)return;const key=x.kind==='admin'?x.year+'/'+x.level+'/'+x.code:'com:'+x.code;
 const layer=state.bounds.get(key);
 if(layer&&layer.getBounds().isValid()){state.map.fitBounds(layer.getBounds(),{padding:[25,25],maxZoom:x.kind==='commune'?12:10,animate:false})}
}
function choose(entry){state.selected=entry;hideResults();detail();focusSelection();updateUrl()}
function ligne(dl,k,v,href){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=k;if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=String(v);dd.append(a)}else dd.textContent=String(v??'Non documenté');dl.append(dt,dd)}
function detail(){const target=$('detail');target.replaceChildren();const x=state.selected;
 const kicker=document.createElement('div');kicker.className='kicker';kicker.textContent=x?.kind==='commune'?'Référentiel communal COG / Pactols':x?.kind==='admin'?'Référentiel administratif IGN–COG':'Fiche du référentiel';target.append(kicker);
 if(!x){const h=document.createElement('h2'),p=document.createElement('p');h.textContent='Sélectionnez un territoire ou une commune';p.textContent='Utilisez la recherche ou cliquez sur les contours affichés. La recherche conserve les états COG et les correspondances Pactols existantes.';target.append(h,p);return}
 if(x.kind==='admin'){
   const f=selectedFeature();if(!f){state.selected=null;detail();return};const p=f.properties;
   const h=document.createElement('h2');h.textContent=p.nom;target.append(h);
   const dl=document.createElement('dl');ligne(dl,'Échelon',label[x.level]);ligne(dl,'Code COG',p.code);ligne(dl,'État',`1er janvier ${x.year}`);ligne(dl,'Édition IGN',geo.edition_IGN[String(x.year)]);
   if(x.level==='departement')ligne(dl,'Région de rattachement',`${p.nom_region_parent} (${p.code_region_parent})`);
   if(x.level==='region')ligne(dl,'Composition',`${p.departements.length} départements`);
   target.append(dl);
   const note=document.createElement('p');note.className='source';note.textContent='Géométrie : '+p.source_geometrie+'. Couche simplifiée pour l’affichage ; aucun ARK Pactols n’est attribué automatiquement.';target.append(note);
   const source=document.createElement('p'),a=document.createElement('a');a.href=geo.source_COG[String(x.year)];a.textContent=`Source officielle : Insee COG ${x.year}`;a.target='_blank';a.rel='noopener noreferrer';source.append(a);target.append(source);
   if(p.niveau==='departement'&&(p.code==='44'||p.code==='49')){const warn=document.createElement('p');warn.className='warning';warn.textContent='Le transfert du Fresne-sur-Loire (44 → 49) prend effet juridiquement le 31 décembre 2015 ; cette date est distincte de la création de la commune nouvelle le 1er janvier 2016.';target.append(warn)}
   return;
 }
 const data=commun.regions[x.zone].cog;const stateCom=core.etat(data,x.code,year());
 const align=data.alignements_Pactols_COG_valides_2026.find(a=>a.code_insee===x.code);
 const h=document.createElement('h2');h.textContent=stateCom.etat?.libelle||x.code;target.append(h);
 const dl=document.createElement('dl');ligne(dl,'Code INSEE',x.code);ligne(dl,'État administratif',`1er janvier ${year()}`);ligne(dl,'Zone du corpus',nomZones[x.zone]);
 if(stateCom.etat){ligne(dl,'Libellé COG',stateCom.etat.libelle);ligne(dl,'Type de commune',stateCom.etat.typecom);
   ligne(dl,'Période du libellé',`${stateCom.etat.debut_inclus} – ${stateCom.etat.fin_exclue||'en cours dans la source'}`)}
 if(align){ligne(dl,'Concept Pactols',align.libelle_pactols,'https://ark.frantiq.fr/ark:/'+align.ark_pactols);ligne(dl,'ARK',align.ark_pactols)}
 target.append(dl);
 const note=document.createElement('p');note.className=align?'source':'warning';note.textContent=align?'Correspondance Pactols–COG déjà validée par AdlFI pour le millésime 2026 seulement : elle ne vaut pas validation historique automatique.':'Aucun alignement Pactols individuellement validé pour cette commune dans le corpus disponible.';target.append(note);
 if(!stateCom.etat){const n=document.createElement('p');n.className='warning';n.textContent='Aucun état COM attesté pour cette date et ce code dans le corpus étudié ; ne pas en conclure à la disparition du lieu.';target.append(n)}
 if(year()!==2026){const n=document.createElement('p');n.className='warning';n.textContent='Aucun contour communal historique qualifié dans cette recette. Les éventuelles limites communales affichées sont exclusivement des repères 2026.';target.append(n)}
 if(stateCom.mouvements.length){const t=document.createElement('h3');t.textContent='Mouvements COG déjà survenus';target.append(t);const ul=document.createElement('ul');for(const ev of stateCom.mouvements.slice(-6)){const li=document.createElement('li');li.textContent=`${ev.date_effet} · ${ev.libelle_avant||'—'} → ${ev.libelle_apres||'—'} (MOD ${ev.mod})`;ul.append(li)}target.append(ul)}
}
start().catch(error=>{$('map-status').textContent='Erreur du référentiel : '+error.message;console.error(error)});
})();