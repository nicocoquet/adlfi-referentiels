(()=>{
'use strict';
const geo={layers:{},edition_IGN:{'2015':'2015-03-04','2016':'2016-06-28'},
  source_COG:{'2015':'https://www.insee.fr/fr/information/2560698','2016':'https://www.insee.fr/fr/information/2114819','2026':'https://www.insee.fr/fr/information/8740222'}};
const commun={regions:{},pactols:null};
const ANNEES_ETALAB=[2018,2019,2021,2022,2023,2024,2025];
const ANNEES_PONTS=[2017,2020];
const ANNEES_QUALIFIEES=[2017,2018,2019,2020,2021,2022,2023,2024,2025];
const ANNEES_DISPONIBLES=new Set([2015,2016,...ANNEES_QUALIFIEES,2026]);
const core=window.AdlfiLieuxChronologieCore;
const outremerSearch=window.AdlfiLieuxOutremerSearch;
const guyaneHistorique=window.AdlfiLieuxGuyaneHistorique;
const martiniqueHistorique=window.AdlfiLieuxMartiniqueHistorique;
const guadeloupeHistorique=window.AdlfiLieuxGuadeloupeHistorique;
const reunionHistorique=window.AdlfiLieuxReunionHistorique;
const mayotteHistorique=window.AdlfiLieuxMayotteHistorique;
const spmHistorique=window.AdlfiLieuxSaintPierreMiquelonHistorique;
const antilles2007=window.AdlfiLieuxAntilles2007;
const wallisHistorique=window.AdlfiLieuxWallisFutunaHistorique;
const polynesieHistorique=window.AdlfiLieuxPolynesieHistorique;
const $=id=>document.getElementById(id);
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const label={region:'Région',departement:'Département',commune:'Commune'};
const ids=['paca','corse','pdl','bfc'];
const nomZones={paca:'Provence-Alpes-Côte d’Azur',corse:'Corse',pdl:'Pays de la Loire',bfc:'Bourgogne-Franche-Comté'};
const views={metropole:[[41.2,-5.7],[51.4,10.1]],bfc:[[46.0,2.7],[49.0,8.0]],pdl:[[46.9,-2.7],[48.7,0.9]],corse:[[41.2,8.5],[43.2,9.7]],paca:[[42.8,4.2],[45.3,7.9]],antilles:[[1,-64],[16,-51]],indien:[[-22,43],[-10,57]],pacifique:[[-27,-160],[23,-130]],atlantique:[[46.5,-57.0],[47.3,-55.5]],taaf:[[-52,41],[-36,79]]};
const state={map:null, layer:null, reference:null, selected:null, bounds:new Map(), indexes:[], noMap:false, renderer:null};
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
}
function commitTimeline(){
 if(timelineTimer!==null){clearTimeout(timelineTimer);timelineTimer=null;}
 // Une fiche communale reste suivie d'une année à l'autre ; une fiche de géométrie
 // régionale/départementale doit être désélectionnée si son instantané change.
 if(state.selected?.kind==='admin'&&state.selected.year!==year())state.selected=null;
 render();
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
function validateAdmin2026(index){
 if(index.schema!=='adlfi.lieux.admin.index_2026.v1'||index.date_reference!=='2026-01-01'||
    index.edition_contours!=='2026-05-04'||index.nouvelles_correspondances_pactols!==0||
    index.entries?.length!==119)throw Error('Index COG 2026 invalide');
 const pairs=new Set();
 for(const e of index.entries){
   if(e.kind!=='admin'||e.year!==2026||!['region','departement'].includes(e.level)||
      !e.code||!e.label||!e.champs?.length)throw Error('Entrée COG 2026 non qualifiée');
   const key=e.level+':'+e.code;
   if(pairs.has(key))throw Error('Index COG 2026 dupliqué');
   pairs.add(key);
 }
 if([...pairs].filter(x=>x.startsWith('region:')).length!==18||
    [...pairs].filter(x=>x.startsWith('departement:')).length!==101||
    !pairs.has('region:06')||!pairs.has('departement:976'))throw Error('Effectifs 2026 incomplets');
}
function validateAdminAnnuels(index){
 if(index.schema!=='adlfi.lieux.admin.index_annuels.v1'||
    JSON.stringify(index.annees)!==JSON.stringify(ANNEES_ETALAB)||
    index.nouvelles_correspondances_pactols!==0||
    index.entries?.length!==ANNEES_ETALAB.length*119)
   throw Error('Index annuel historique incomplet');
 const counts=new Map(),seen=new Set();
 for(const e of index.entries){
   if(e.kind!=='admin'||!ANNEES_ETALAB.includes(e.year)||
      !['region','departement'].includes(e.level)||!e.code||!e.label||!e.champs?.length)
     throw Error('Entrée COG annuelle invalide');
   const key=e.year+'/'+e.level+'/'+e.code;
   if(seen.has(key))throw Error('Entrée COG annuelle dupliquée');
   seen.add(key);
   const yLevel=e.year+'/'+e.level;
   counts.set(yLevel,(counts.get(yLevel)||0)+1);
 }
 for(const year of ANNEES_ETALAB){
   if(counts.get(year+'/region')!==18||counts.get(year+'/departement')!==101)
     throw Error('Effectifs COG annuels invalides : '+year);
 }
}
function validateAdminPonts(index){
 if(index.schema!=='adlfi.lieux.admin.index_ponts.v1'||
    JSON.stringify(index.annees)!==JSON.stringify(ANNEES_PONTS)||
    index.nouvelles_correspondances_pactols!==0||index.entries?.length!==238)
   throw Error('Index IGN 2017/2020 incomplet');
 const codes=new Set(),counts=new Map();
 for(const e of index.entries){
   if(e.kind!=='admin'||!ANNEES_PONTS.includes(e.year)||
      !['region','departement'].includes(e.level)||!e.code||!e.label||!e.champs?.length)
     throw Error('Entrée IGN 2017/2020 invalide');
   const k=e.year+'/'+e.level+'/'+e.code;
   if(codes.has(k))throw Error('Entrée IGN 2017/2020 dupliquée');
   codes.add(k);
   const groupe=e.year+'/'+e.level;
   counts.set(groupe,(counts.get(groupe)||0)+1);
 }
 for(const year of ANNEES_PONTS){
   if(counts.get(year+'/region')!==18||counts.get(year+'/departement')!==101)
     throw Error('Millésime IGN incomplet '+year);
 }
}
async function layerFor(y,l){
 const key=l+'s-'+y;
 if(!layerData.has(key)){
   const path=ROOT+'lieux-historique/'+key+'.geojson';
   layerData.set(key,loadJSON(path).then(fc=>{
     const contemporaine=y===2026;
     const annuelle=ANNEES_QUALIFIEES.includes(y);
     const taille=contemporaine||annuelle?(l==='region'?18:101):(l==='region'?(y===2015?22:13):96);
     if(fc.type!=='FeatureCollection'||fc.provenance?.cog_au_premier_janvier!==String(y)||
        fc.provenance?.pactols_valide!==false||fc.features?.length!==taille||
        (contemporaine?
         (fc.provenance?.schema!=='adlfi.lieux.contours.administratifs_2026.v1'||
          fc.provenance?.edition_contours!=='2026-05-04'||
          fc.provenance?.generalisation_m!==100):
         annuelle?
         (fc.provenance?.schema!=='adlfi.lieux.contours.annuels.v1'||
          fc.provenance?.annee_geometrie!==y||
          fc.provenance?.generalisation_m!==100||
          !fc.provenance?.source_archives_sha256):
         (fc.provenance?.schema!=='adlfi.lieux.contours.historiques.v1'||
          fc.provenance?.edition_IGN!==geo.edition_IGN[String(y)])))
       throw new Error('Couche IGN/COG incompatible : '+key);
     for(const f of fc.features){
       if(f.properties?.annee!==y||f.properties?.niveau!==l||
          f.properties?.pactols_valide!==false)throw new Error('État géographique non validé : '+key);
     }
     if(annuelle){
       geo.source_COG[String(y)]=fc.provenance.source_cog_url;
       if(ANNEES_PONTS.includes(y)){
         if(fc.provenance.source_geometrie!=='IGN ADMIN EXPRESS COG'||
            fc.provenance.edition_IGN!==(y===2017?'2017-06-19':'2020-11-20'))
           throw Error('Édition IGN 2017/2020 incompatible : '+key);
         geo.edition_IGN[String(y)]=fc.provenance.edition_IGN;
       }
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
 if(!core || !window.AdlfiLieuxSearch || !outremerSearch || !guyaneHistorique || !martiniqueHistorique || !guadeloupeHistorique || !reunionHistorique || !mayotteHistorique || !spmHistorique || !antilles2007 || !wallisHistorique || !polynesieHistorique)throw Error('Moteur du référentiel communal absent');
 const [pactols,adminIndex,adminIndex2026,adminIndexAnnuels,indexPonts,indexOutremer,indexGuyaneHistorique,indexMartiniqueHistorique,indexGuadeloupeHistorique,indexReunionHistorique,indexMayotteHistorique,indexSPMHistorique,indexAntilles2007,indexWallisHistorique,indexPolynesieHistorique,...cogs]=await Promise.all([
   loadJSON(ROOT+'lieux.json'),
   loadJSON(ROOT+'lieux-historique/index.json'),
   loadJSON(ROOT+'lieux-historique/index-2026.json'),
   loadJSON(ROOT+'lieux-historique/index-annuels.json'),
   loadJSON(ROOT+'lieux-historique/index-ponts.json'),
   loadJSON(ROOT+'lieux-outremer/recherche-2026.json'),
   loadJSON(ROOT+'lieux-guyane/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-martinique/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-guadeloupe/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-reunion/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-mayotte/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-saint-pierre-miquelon/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-antilles-collectivites-2007/chronologie-cog-juridique-2026.json'),
   loadJSON(ROOT+'lieux-wallis-futuna/chronologie-cog-2026.json'),
   loadJSON(ROOT+'lieux-polynesie/chronologie-cog-2026.json'),
   ...ids.map(id=>loadJSON(ROOT+'lieux-chronologie/cog-'+id+'.json'))
 ]);
 if(pactols.autorites?.length!==103||pactols.totaux?.autorites_pactols!==103)
   throw Error('Les 103 autorités Pactols PACA doivent être conservées');
 commun.pactols=pactols;validateAdmin(adminIndex);validateAdmin2026(adminIndex2026);validateAdminAnnuels(adminIndexAnnuels);validateAdminPonts(indexPonts);
 for(let i=0;i<ids.length;i++){
   const id=ids[i],data=cogs[i];
   core.verifier(data);
   if(data.region!==id)throw Error('Corps communal mal identifié : '+id);
   commun.regions[id]={cog:data};
 }
 $('year').value='2026';
 const former=window.AdlfiLieuxSearch.creerIndex(pactols.autorites);
 const variants=new Map(former.map(x=>[x.ark,x.champs]));
 const autresCOG=outremerSearch.creerIndex(indexOutremer);
 state.outremer=new Map(autresCOG.map(x=>[x.id,x]));
  // 98609 est un ancien code documenté de Wallis-et-Futuna, non une commune
  // ni une seconde autorité Pactols ; permettre sa recherche sans inférence.
  const wf=state.outremer.get('COMER:TERRITOIRE:986');
  if(wf)wf.champs=[...new Set([...wf.champs,'98609'])];
  state.guyane=guyaneHistorique.creer(indexGuyaneHistorique);
  state.martinique=martiniqueHistorique.creer(indexMartiniqueHistorique);
  state.guadeloupe=guadeloupeHistorique.creer(indexGuadeloupeHistorique);
   state.reunion=reunionHistorique.creer(indexReunionHistorique);
   state.mayotte=mayotteHistorique.creer(indexMayotteHistorique);
    state.spm=spmHistorique.creer(indexSPMHistorique);
     state.antilles2007=antilles2007.creer(indexAntilles2007);
     state.wallis=wallisHistorique.creer(indexWallisHistorique);
     state.polynesie=polynesieHistorique.creer(indexPolynesieHistorique);
 state.indexes=ids.flatMap(id=>core.indexer(commun.regions[id].cog)
   .map(e=>({...e,zone:id,champs:[...new Set([...(e.champs||[]),...(e.kind==='pactols'?(variants.get(e.ark)||[]):[])])]})))
   .concat(adminIndex.entries,adminIndex2026.entries,adminIndexAnnuels.entries,indexPonts.entries,autresCOG,state.guyane.historicalIndex,state.guadeloupe.historicalIndex);
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
 const cogId=params.get('ref_cog');
 if(cogId && state.outremer.has(cogId)){
   const entry=state.outremer.get(cogId);
   state.selected={kind:entry.kind,id:entry.id,code:entry.code};
   if(entry.kind==='cog2026')$('level').value='commune';
 }
 const historicalCode=params.get('ref_cog_historique');
 if(historicalCode && state.guyane.old.has(historicalCode)){
   state.selected={kind:'cogHistoriqueGuyane',code:historicalCode};
   $('level').value='commune';
 }
 const guadeloupeCode=params.get('ref_cog_historique_guadeloupe');
 if(guadeloupeCode && state.guadeloupe.old.has(guadeloupeCode)){
   state.selected={kind:'cogHistoriqueGuadeloupe',code:guadeloupeCode};
   $('level').value='commune';
 }
 const hash=new URLSearchParams(location.hash.replace(/^#/,'')),ark=hash.get('ark');
 if(ark){const found=state.indexes.find(x=>x.kind==='pactols'&&x.ark===ark);
   if(found){state.selected={kind:'commune',code:found.code,zone:found.zone,year:year(),ark};
     $('level').value='commune';$('year').value='2026';}}
 if(window.L){
  state.map=L.map('map',{scrollWheelZoom:false,preferCanvas:true}).setView([46.5,2.2],6);
  state.renderer=L.canvas();
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
 if(state.selected?.kind==='cog2026'||state.selected?.kind==='autre_cog2026'){
   u.searchParams.set('ref_cog',state.selected.id);
 }else u.searchParams.delete('ref_cog');
 if(state.selected?.kind==='cogHistoriqueGuyane')u.searchParams.set('ref_cog_historique',state.selected.code);
 else u.searchParams.delete('ref_cog_historique');
 if(state.selected?.kind==='cogHistoriqueGuadeloupe')
   u.searchParams.set('ref_cog_historique_guadeloupe',state.selected.code);
 else u.searchParams.delete('ref_cog_historique_guadeloupe');
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
 return L.geoJSON({type:'FeatureCollection',features},{renderer:state.renderer,interactive:!reference,
   style:f=>{
      const communeRepere=reference&&f.properties?.niveau==='commune';
      return {color:reference?'#354e59':color(f.properties.niveau||'commune'),
        weight:reference?(communeRepere?.55:1.4):1.15,
        opacity:reference?(communeRepere?.60:.95):.9,
        fillColor:reference?'#c7ccd0':'#5d9cab',
        fillOpacity:reference?0:.10,
        dashArray:reference?(communeRepere?'2,5':'5,5'):null};
   },
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
  if((l==='region'||l==='departement')&&ANNEES_DISPONIBLES.has(y)){
    features=await layerFor(y,l);
    desc=features.length+' contours '+(l==='region'?'régionaux':'départementaux')+
      (y===2026?' · COG 1er janvier 2026 et contours data.gouv.fr du 4 mai 2026 (100 m).':
       ANNEES_QUALIFIEES.includes(y)?' · COG au 1er janvier '+y+
         (ANNEES_PONTS.includes(y)?' et contours IGN ADMIN EXPRESS COG, édition '+
           geo.edition_IGN[String(y)]+' (100 m, réparations topologiques documentées).':
          ' et contours Etalab/IGN du millésime '+y+' (100 m, réparations topologiques documentées).'):
       ' · IGN GEOFLA '+geo.edition_IGN[String(y)]+', généralisation à 100 m (affichage seulement).');
  }else if(l==='commune'&&y===2026){
    features=await chargerCommunes2026();
    desc=features.length+' contours communaux 2026 sur les quatre régions pilotes, sans alignement Pactols inféré.';
  }else if(l==='commune'){
    desc='Les états COG communaux restent consultables par recherche pour '+y+
      ', mais aucun contour communal historique '+y+' n’est qualifié. Le fond OpenStreetMap est contemporain.';
  }else desc='Aucun contour '+(label[l]||l).toLowerCase()+' disponible et qualifié pour '+y+'.';
  let references=[];
  // Ne jamais masquer silencieusement tous les contours lorsque la source
  // historique du millésime demandé n'existe pas. Le repère est visuellement
  // distinct, daté et NON assimilé à l'état COG de l'année sélectionnée.
  if(!features.length&&$('reference').checked){
    if(l==='commune'&&y!==2026){
      references=await chargerCommunes2026();
      desc+=' Repère cartographique affiché : contours communaux 2026 (et NON '+y+'). Ce tracé contemporain ne représente pas les limites historiques.';
    }else if(l==='region'||l==='departement'){
      const refYear=y<2015?2015:[...ANNEES_DISPONIBLES].filter(v=>v<=y).at(-1);
      references=await layerFor(refYear,l);
      desc+=' Repère cartographique affiché : limites IGN de '+refYear+' (et NON '+y+'). Ce tracé n\'atteste pas les limites administratives à la date choisie.';
    }
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
 const q=core.normaliser($('search').value),ul=$('results');
 ul.replaceChildren();
 if(q.length<2){hideResults();return}
 const terms=q.split(' ');
 const score=h=>{
   const n=core.normaliser(h.label||''),c=core.normaliser(h.code||'');
   if(h.kind==='admin'&&h.year===year()&&n===q)return 0;
   if(n===q||c===q||core.normaliser(h.ark||h.arkValide||'')===q)return 1;
   if(n.startsWith(q))return 2;
   if(c.startsWith(q))return 3;
   return 4;
 };
 const hits=state.indexes.filter(h=>terms.every(t=>h.champs.some(ch=>ch.includes(t))))
   .sort((a,b)=>score(a)-score(b)||
     a.label.localeCompare(b.label,'fr',{sensitivity:'base'})||
     String(a.id||a.code).localeCompare(String(b.id||b.code))).slice(0,22);
 for(const h of hits){
   const li=document.createElement('li'),btn=document.createElement('button');
   btn.type='button';
   const heading=document.createElement('strong');heading.textContent=h.label;
   const sub=document.createElement('small');
   if(h.kind==='admin')sub.textContent=`${label[h.level]} · COG ${h.year} · ${h.code}`;
   else if(h.kind==='cog2026')
     sub.textContent=`Commune · COG 2026 · ${h.parent} · ${h.code}`+
       (h.arkValide?' · Pactols validé pour 2026':'');
   else if(h.kind==='autre_cog2026')
     sub.textContent=`${h.type} · COG 2026 · ${h.parent||'Territoire'} · ${h.code}`;
   else if(h.kind==='cogHistoriqueGuyane')
     sub.textContent='Commune historique · Guyane · '+h.code+' · COG jusqu’en 1969 (sans contour)';
   else if(h.kind==='cogHistoriqueGuadeloupe')
     sub.textContent='Ancienne commune · Guadeloupe · '+h.code+' · COG jusqu’en 2007 (sans contour ni ARK aligné)';
   else sub.textContent=`${h.kind==='pactols'?'Pactols validé en 2026':'Commune COG'} · ${nomZones[h.zone]} · ${h.code}`;
   btn.append(heading,sub);
   btn.addEventListener('click',()=>{
     if(h.kind==='admin'){
       $('level').value=h.level;
       $('year').value=String(h.year);
       state.selected={kind:'admin',level:h.level,year:h.year,code:h.code};
     }else if(h.kind==='cog2026'||h.kind==='autre_cog2026'){
       if(h.kind==='cog2026')$('level').value='commune';
       state.selected={kind:h.kind,id:h.id,code:h.code};
     }else if(h.kind==='cogHistoriqueGuyane'){
       $('level').value='commune';
       $('year').value=String(h.dernierAnActif);
       state.selected={kind:'cogHistoriqueGuyane',code:h.code};
     }else if(h.kind==='cogHistoriqueGuadeloupe'){
       $('level').value='commune';
       $('year').value=String(h.dernierAnActif);
       state.selected={kind:'cogHistoriqueGuadeloupe',code:h.code};
     }else{
       $('level').value='commune';
       state.selected={kind:'commune',code:h.code,zone:h.zone,year:year(),
         ark:h.kind==='pactols'?h.ark:null};
     }
     hideResults();render().then(focusSelection);
   });
   li.append(btn);ul.append(li);
 }
 if(!hits.length){
   const li=document.createElement('li');
   li.textContent='Aucun résultat dans les données étudiées.';
   li.style.padding='12px';ul.append(li);
 }
 ul.hidden=false;$('search').setAttribute('aria-expanded','true');
}
function focusSelection(){const x=state.selected;
 if(!x||!state.map)return;
 if(x.kind==='cog2026'&&x.code?.startsWith('971')){
   state.map.fitBounds([[15.7,-61.9],[16.57,-60.85]],{padding:[24,24],animate:false});return;
 }
 if(x.kind==='cog2026'&&x.code?.startsWith('972')){
   state.map.fitBounds([[14.32,-61.27],[14.93,-60.79]],{padding:[24,24],animate:false});return;
 }
 if((x.kind==='cogHistoriqueGuyane')||(x.kind==='cog2026'&&x.code?.startsWith('973'))){
   state.map.fitBounds([[2,-54.8],[6,-51.5]],{padding:[24,24],animate:false});return;
 }
 if(x.kind==='cog2026'&&x.code?.startsWith('974')){
    state.map.fitBounds([[-21.42,55.14],[-20.84,55.87]],{padding:[24,24],animate:false});return;
  }
  if(x.kind==='cog2026'&&x.code?.startsWith('976')){
    state.map.fitBounds([[-13.1,44.95],[-12.55,45.35]],{padding:[24,24],animate:false});return;
  }
  if((x.kind==='cog2026'&&x.code?.startsWith('975'))||
      (x.kind==='autre_cog2026'&&x.id==='COMER:TERRITOIRE:975')){
     state.map.fitBounds([[46.5,-57.0],[47.3,-55.5]],{padding:[24,24],animate:false});return;
   }
   if((x.kind==='cog2026'&&x.code?.startsWith('987'))||
      (x.kind==='autre_cog2026'&&x.id==='COMER:TERRITOIRE:987')){
      state.map.fitBounds([[-28,-161],[0,-131]],{padding:[24,24],animate:false});return;
   }
   if(x.kind==='autre_cog2026'&&
        (x.id==='COMER:TERRITOIRE:986'||/^COMER:CIR:9861[123]$/.test(x.id))){
     state.map.fitBounds([[-14.6,-178.6],[-12.9,-175.8]],{padding:[24,24],animate:false});return;
   }
   if(!['admin','commune'].includes(x.kind))return;
 const key=x.kind==='admin'?x.year+'/'+x.level+'/'+x.code:'com:'+x.code;
 const layer=state.bounds.get(key);
 if(layer&&layer.getBounds().isValid()){state.map.fitBounds(layer.getBounds(),{padding:[25,25],maxZoom:x.kind==='commune'?12:10,animate:false})}
}
function choose(entry){state.selected=entry;hideResults();detail();focusSelection();updateUrl()}
function ligne(dl,k,v,href){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=k;if(href){const a=document.createElement('a');a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=String(v);dd.append(a)}else dd.textContent=String(v??'Non documenté');dl.append(dt,dd)}
function afficherChronologieGuyane(target,code){
 if(!state.guyane)return;
 const h=document.createElement('h3');h.textContent='État COG de Guyane au 1er janvier '+year();target.append(h);
 const period=state.guyane.etat(code,year()),all=state.guyane.periodes(code);
 if(period){
   const dl=document.createElement('dl');
   ligne(dl,'Code communal documenté',code);
   ligne(dl,'Libellé à la date sélectionnée',period.label);
   ligne(dl,'Période documentée',period.start+' – '+(period.end||'en cours dans la source'));
   target.append(dl);
 }else{
   const p=document.createElement('p');p.className='warning';
   p.textContent='Aucun épisode actif n’est attesté pour ce code au 1er janvier '+
     year()+' dans l’historique COG étudié. Il ne faut pas en déduire l’absence historique du lieu.';
   target.append(p);
 }
 if(all.length>1){
   const heading=document.createElement('h3');heading.textContent='États documentés du même code';target.append(heading);
   const ul=document.createElement('ul');
   for(const e of all){
     const li=document.createElement('li');
     li.textContent=e.label+' · '+e.start+' – '+(e.end||'en cours dans la source');
     ul.append(li);
   }
   target.append(ul);
 }
 const link=document.createElement('p'),a=document.createElement('a');
 a.href='https://www.insee.fr/fr/information/2560452';
 a.target='_blank';a.rel='noopener noreferrer';
 a.textContent='Source : Insee, historique des communes (COG 2026)';
 link.append(a);target.append(link);
 const warn=document.createElement('p');warn.className='warning';
 warn.textContent='Ces observations concernent des couples code–libellé datés, et non une identité juridique intemporelle. Aucun contour historique de Guyane n’est affiché ; les correspondances Pactols validées pour 2026 ne sont pas rétroactives.';
 target.append(warn);
}
function afficherChronologieMartinique(target,code){
 if(!state.martinique)return;
 const h=document.createElement('h3');h.textContent='État COG de Martinique au 1er janvier '+year();target.append(h);
 const period=state.martinique.etat(code,year()),all=state.martinique.periodes(code);
 if(period){
   const dl=document.createElement('dl');
   ligne(dl,'Code communal documenté',code);
   ligne(dl,'Libellé à la date sélectionnée',period.label);
   ligne(dl,'Période documentée',period.start+' – '+(period.end||'en cours dans la source'));
   target.append(dl);
 }else{
   const p=document.createElement('p');p.className='warning';
   p.textContent='Aucun épisode actif n’est attesté pour ce code au 1er janvier '+
     year()+' dans l’historique COG étudié. Il ne faut pas en déduire l’absence historique du lieu.';
   target.append(p);
 }
 if(all.length>1){
   const heading=document.createElement('h3');heading.textContent='États documentés du même code';target.append(heading);
   const ul=document.createElement('ul');
   for(const e of all){
     const li=document.createElement('li');
     li.textContent=e.label+' · '+e.start+' – '+(e.end||'en cours dans la source');
     ul.append(li);
   }
   target.append(ul);
 }
 const link=document.createElement('p'),a=document.createElement('a');
 a.href='https://www.insee.fr/fr/information/2560452';
 a.target='_blank';a.rel='noopener noreferrer';
 a.textContent='Source : Insee, historique des communes (COG 2026)';
 link.append(a);target.append(link);
 const warn=document.createElement('p');warn.className='warning';
 warn.textContent='Ces observations concernent des couples code–libellé datés, et non une identité juridique intemporelle. Aucun contour historique de Martinique n’est affiché ; les correspondances Pactols validées pour 2026 ne sont pas rétroactives.';
 target.append(warn);
}
function afficherChronologieGuadeloupe(target,code){
 if(!state.guadeloupe)return;
 const h=document.createElement('h3');h.textContent='État COG de Guadeloupe au 1er janvier '+year();target.append(h);
 const period=state.guadeloupe.etat(code,year()),all=state.guadeloupe.periodes(code);
 if(period){
   const dl=document.createElement('dl');
   ligne(dl,'Code communal documenté',code);
   ligne(dl,'Libellé à la date sélectionnée',period.label);
   ligne(dl,'Période documentée',period.start+' – '+(period.end||'en cours dans la source'));
   target.append(dl);
 }else{
   const p=document.createElement('p');p.className='warning';
   p.textContent='Aucun épisode actif n’est attesté pour ce code au 1er janvier '+
     year()+' dans l’historique COG étudié. Il ne faut pas en déduire l’absence historique du lieu.';
   target.append(p);
 }
 if(all.length>1){
   const heading=document.createElement('h3');heading.textContent='États documentés du même code';target.append(heading);
   const ul=document.createElement('ul');
   for(const e of all){
     const li=document.createElement('li');
     li.textContent=e.label+' · '+e.start+' – '+(e.end||'en cours dans la source');
     ul.append(li);
   }
   target.append(ul);
 }
 const link=document.createElement('p'),a=document.createElement('a');
 a.href='https://www.insee.fr/fr/information/2560452';
 a.target='_blank';a.rel='noopener noreferrer';
 a.textContent='Source : Insee, historique des communes (COG 2026)';
 link.append(a);target.append(link);
 const warn=document.createElement('p');warn.className='warning';
 warn.textContent='Ces observations concernent des couples code–libellé datés, et non une identité juridique intemporelle. Aucun contour historique de Guadeloupe n’est affiché ; les correspondances Pactols validées pour 2026 ne sont pas rétroactives.';
 target.append(warn);
}
function afficherChronologieReunion(target,code){
 if(!state.reunion)return;
 const h=document.createElement('h3');
 h.textContent='État COG de La Réunion au 1er janvier '+year();
 target.append(h);
 const period=state.reunion.etat(code,year());
 if(period){
   const dl=document.createElement('dl');
   ligne(dl,'Code communal documenté',code);
   ligne(dl,'Libellé COG à la date sélectionnée',period.label);
   ligne(dl,'Période code–libellé COG',period.start+' – '+(period.end||'en cours dans la source'));
   if(code==='97414'){
     const avant=state.reunion.perimetreSaintLouis(year())==='AVANT_DIVISION_1965';
     ligne(dl,'Situation territoriale documentée',
       avant?'Avant la division du 5 février 1965':'Après la division du 5 février 1965 (code 97414 conservé)');
   }
   target.append(dl);
 }else{
   const p=document.createElement('p');p.className='warning';
   p.textContent='Aucun épisode actif n’est attesté pour ce code au 1er janvier '+
     year()+' dans l’historique COG étudié. Il ne faut pas en déduire l’absence historique du lieu.';
   target.append(p);
 }
 if(code==='97414'||code==='97424'){
   const div=document.createElement('p');div.className='source';
   div.textContent='Mouvement COG attesté le 5 février 1965 (MOD 20) : division de Saint-Louis (97414) en Saint-Louis (97414, code conservé avec emprise réduite) et Cilaos (97424, nouveau code). Le COG comporte deux lignes pour un seul événement de division.';
   target.append(div);
   if(year()===1965){
     const note=document.createElement('p');note.className='warning';
     note.textContent='La frise représente le 1er janvier 1965, antérieur à la division du 5 février : Cilaos n’apparaît dans les états au 1er janvier qu’en 1966.';
     target.append(note);
   }
 }
 const link=document.createElement('p'),a=document.createElement('a');
 a.href='https://www.insee.fr/fr/information/2560452';
 a.target='_blank';a.rel='noopener noreferrer';
 a.textContent='Source : Insee, historique des communes (COG 2026)';
 link.append(a);target.append(link);
 const warn=document.createElement('p');warn.className='warning';
 warn.textContent='Les épisodes COG sont documentaires. Le maintien du code Saint-Louis en 1965 ne signifie pas maintien de son territoire. Aucun contour historique de La Réunion n’est affiché ; les 24 alignements Pactols validés pour 2026 ne sont pas rétroactifs.';
 target.append(warn);
}
function afficherChronologieMayotte(target,code){
 if(!state.mayotte)return;
 const h=document.createElement('h3');
 h.textContent='État COG de Mayotte au 1er janvier '+year();
 target.append(h);
 const period=state.mayotte.etat(code,year());
 if(period){
   const dl=document.createElement('dl');
   ligne(dl,'Code communal documenté',code);
   ligne(dl,'Libellé COG à la date sélectionnée',period.label);
   ligne(dl,'Famille de données du COG',period.famille==='COMER'?
     'COMER · communes des collectivités et territoires d’outre-mer':
     'DROM · communes des départements et régions d’outre-mer');
   ligne(dl,'Période documentaire',period.start+' – '+(period.end||'en cours dans la source'));
   if(period.famille==='DROM'){
     ligne(dl,'Code de la collectivité à statut particulier (autre niveau)',
       year()===2026?'976R · Département-Région de Mayotte':'976D · Département de Mayotte');
   }
   target.append(dl);
 }else{
   const p=document.createElement('p');p.className='warning';
   p.textContent='Aucun épisode de Mayotte n’est documenté dans les deux séries COG utilisées au 1er janvier '+
     year()+'. La première attestation de cette sélection est le 23 février 2007 ; cela ne prouve pas que les communes n’existaient pas auparavant.';
   target.append(p);
 }
 const p=document.createElement('p');p.className='source';
 p.textContent='Au 31 mars 2011, les 17 communes passent de la série COG COMER à la série DROM, avec conservation de leurs codes et libellés dans ces deux séries. Il s’agit d’un changement de statut et de famille documentaire, et non de la date de création des communes.';
 target.append(p);
 if(year()===2011){
   const note=document.createElement('p');note.className='warning';
   note.textContent='Le curseur représente le 1er janvier 2011, avant le changement de statut effectif le 31 mars : l’état COMER reste affiché pour cette année.';
   target.append(note);
 }
 if(code==='97607'){
   const reserve=document.createElement('p');reserve.className='warning';
   reserve.textContent='Dembeni (97607) : ARK 26678/crtZcuFSJVYZU confirmé dans sa forme littérale, mais correspondance Pactols–COG non validée, y compris pour 2026. Aucun alignement historique n’est produit.';
   target.append(reserve);
 }
 const link=document.createElement('p'),a=document.createElement('a');
 a.href='https://www.insee.fr/fr/information/8740222';
 a.target='_blank';a.rel='noopener noreferrer';
 a.textContent='Source : Insee, COG 2026, séries historiques COMER et DROM';
 link.append(a);target.append(link);
 const warn=document.createElement('p');warn.className='warning';
 warn.textContent='Les 34 périodes COG sont documentaires, sans contour historique de Mayotte. Le code institutionnel 976R ne désigne pas une commune. Les 16 correspondances Pactols approuvées pour 2026 ne sont pas rétroactives.';
 target.append(warn);
}
function afficherChronologieSPM(target,entry){
 if(!state.spm)return;
 const y=year(),commune=entry.kind==='cog2026';
 const h=document.createElement('h3');h.textContent='État COG de Saint-Pierre-et-Miquelon au 1er janvier '+y;target.append(h);
 const ep=commune?state.spm.etatCommune(entry.code,y):state.spm.etatCollectivite(y);
 if(ep){
  const dl=document.createElement('dl');
  ligne(dl,'Niveau documenté',commune?'Commune':'Collectivité territoriale');
  ligne(dl,'Code et libellé COG',ep.code+' · '+ep.label);
  ligne(dl,'Début du couple code–libellé COG',ep.start);
  ligne(dl,'Fin documentaire',ep.end||'En cours dans le COG 2026');
  ligne(dl,'Série documentaire COG',commune?
     'Communes des collectivités et territoires d’outre-mer (COMER)':
     'Collectivités et territoires d’outre-mer');
  target.append(dl);
 }else{
  const p=document.createElement('p');p.className='warning';
  p.textContent=commune?
    'Aucun épisode communal n’est documenté pour ce code au 1er janvier '+y+
    '. Sa première attestation dans la série COG consultée est le 21 juillet 1976, non sa date de création.':
    'Aucun épisode du code territorial 975 n’est documenté au 1er janvier '+y+
    '. Sa première attestation dans cette série COG est le 15 juin 1985, sans impliquer l’inexistence antérieure du territoire.';
  target.append(p);
 }
 const statut=state.spm.statutJuridiqueAnnuel(y);
 if(statut){
  const p=document.createElement('p');p.className='source';
  p.textContent='Statut institutionnel au 1er janvier (repère annuel fondé sur les textes) : '+statut+
   '. La série COG COMER ne détermine pas le statut juridique historique.';target.append(p);
 }
 if([1976,1985,2003,2007].includes(y)){
  const p=document.createElement('p');p.className='source';
  p.textContent='Année de réforme : le curseur indique le 1er janvier, antérieurement à la loi promulguée cette année-là. Les changements de statut ne créent pas de nouvelles communes dans cet audit.';target.append(p);
 }
 for(const [label,href] of [
  ['Source historique des codes : Insee, COG 2026','https://www.insee.fr/fr/information/8740222'],
  ['Source des statuts : Insee, codification de Saint-Pierre-et-Miquelon','https://www.insee.fr/fr/information/7929495']
 ]){
   const p=document.createElement('p'),a=document.createElement('a');
   a.href=href;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;p.append(a);target.append(p);
 }
 const p=document.createElement('p');p.className='warning';
 p.textContent='États COG documentaires seulement : aucun contour historique, aucun nouvel alignement Pactols, aucune succession inférée. Les géométries contemporaines ne sont pas rétroprojetées.';
 target.append(p);
}
function afficherTransitionAntilles2007(target,entry){
 if(!state.antilles2007)return;
 const code=entry.code,rel=state.antilles2007.pourCode(code);
 if(!rel)return;
 const y=year(),episode=state.antilles2007.etat(code,y);
 const title=document.createElement('h3');
 title.textContent='Saint-Barthélemy et Saint-Martin · transition 2007 · état au 1er janvier '+y;
 target.append(title);
 if(episode){
  const dl=document.createElement('dl');
  ligne(dl,'Statut du code sélectionné',
    episode.type==='ANCIENNE_COMMUNE'?'Ancienne commune de Guadeloupe':
    episode.type==='COLLECTIVITE'?'Collectivité d’outre-mer':'Code d’application à cinq positions, pas une commune');
  ligne(dl,'Identifiant et libellé actifs au 1er janvier',episode.code+' · '+episode.libelle);
  ligne(dl,'Couple code–libellé documenté',episode.debut+' – '+(episode.fin||'en cours dans le COG 2026'));
  target.append(dl);
 }else{
  const p=document.createElement('p');p.className='warning';
  p.textContent='Aucun épisode de ce code ('+code+') n’est actif au 1er janvier '+y+
    ' dans le COG historique. Ce résultat ne signifie pas que le territoire géographique n’existait pas.';
  target.append(p);
 }
 if(y===2007){
  const p=document.createElement('p');p.className='source';
  p.textContent='Le curseur représente le 1er janvier 2007 : les communes 97123/97127 sont encore actives, et les collectivités 977/978 commencent le 23 février selon le COG.';
  target.append(p);
 }
 const dl=document.createElement('dl');
 ligne(dl,'Ancienne commune',rel.ancienne_commune.code+' · '+rel.ancienne_commune.libelle);
 ligne(dl,'Collectivité successeure (en droit)',rel.collectivite.code+' · '+rel.collectivite.libelle);
 ligne(dl,'Code à cinq positions',rel.code_cinq_positions.code+' · ce n’est pas une nouvelle commune');
 ligne(dl,'Mouvement dans le COG','MOD 30 · 23 février 2007 ; COM_AP vide');
 ligne(dl,'Fondement de la succession',rel.succession_juridique.source);
 target.append(dl);
 const p=document.createElement('p');p.className='source';
 p.textContent='Le COG atteste la fin de l’ancien code communal, sans code de destination. La loi organique établit séparément la succession des droits et obligations par la nouvelle collectivité.';
 target.append(p);
 const refs=[
  ['Insee : codification et codes à cinq positions','https://www.insee.fr/fr/information/7929495'],
  ['Légifrance : article 18 de la loi organique n° 2007-223',rel.succession_juridique.source_legifrance],
  ['Légifrance : '+rel.succession_juridique.fondement_CGCT,rel.succession_juridique.source_CGCT]
 ];
 for(const [label,url]of refs){
  const item=document.createElement('p'),a=document.createElement('a');
  a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;
  item.append(a);target.append(item);
 }
 const link=document.createElement('p'),a=document.createElement('a');
 const estAncienne=code===rel.ancienne_commune.code;
 a.href=estAncienne?
  '?ref_cog='+encodeURIComponent('COMER:TERRITOIRE:'+rel.collectivite.code)+'&annee=2008&niveau=commune':
  '?ref_cog_historique_guadeloupe='+rel.ancienne_commune.code+'&annee=2007&niveau=commune';
 a.textContent=estAncienne?'Consulter la collectivité successeure ('+rel.collectivite.code+')':
  'Consulter l’ancienne commune ('+rel.ancienne_commune.code+')';
 link.append(a);target.append(link);
 const warning=document.createElement('p');warning.className='warning';
 warning.textContent='La succession juridique n’est pas une équivalence Pactols et ne valide ni transfert d’ARK ni contour historique. Le code à cinq positions ne crée pas une commune.';
 target.append(warning);
}
function afficherChronologieWallisFutuna(target,entry){
 if(!state.wallis)return;
 const y=year(),isCirc=entry.nature==='CIR';
 const h=document.createElement('h3');
 h.textContent='État COG de Wallis-et-Futuna au 1er janvier '+y;
 target.append(h);
 const cur=isCirc?state.wallis.etatCirconscription(entry.code,y):
                     state.wallis.etatTerritoire(y);
 if(cur){
  const dl=document.createElement('dl');
  ligne(dl,'Nature de l’autorité COG',isCirc?'Circonscription territoriale (non commune)':'Territoire d’outre-mer (non communal)');
  ligne(dl,'Code et libellé COG',cur.code+' · '+(cur.label||entry.label));
  ligne(dl,'Début de l’épisode code–libellé dans le COG',cur.start);
  ligne(dl,'Fin documentaire',cur.end||'En cours dans le COG 2026');
  target.append(dl);
 }else{
  const p=document.createElement('p');p.className='warning';
  p.textContent='Aucun épisode du code '+entry.code+' n’est documenté au 1er janvier '+y+
   '. Cette absence de code dans la série COG ne démontre pas que l’entité juridique ou le lieu géographique n’existait pas.';
  target.append(p);
 }
 if(entry.id==='COMER:TERRITOIRE:986'){
  const old=state.wallis.codeTerritoireHistorique(y);
  if(old){
    const dl=document.createElement('dl');
    ligne(dl,'Ancienne codification documentée au 1er janvier',old.code+' · '+old.label);
    ligne(dl,'Période du code historique 98609 dans le COG',old.start+' – '+old.end+' (fin exclusive)');
    target.append(dl);
  }
 }
 const legal=state.wallis.statutCirconscriptionsLegal(y);
 if(legal){
  const p=document.createElement('p');p.className='source';
  p.textContent='Référence juridique au 1er janvier : '+legal+
   '. Leur codification COG propre ne débute qu’en 1985 ; cette date ne constitue pas leur création.';
  target.append(p);
 }else if(y===1961){
  const p=document.createElement('p');p.className='source';
  p.textContent='La loi du 29 juillet 1961 est postérieure au 1er janvier sélectionné : les trois circonscriptions seront attestées juridiquement à compter du 30 juillet 1961.';
  target.append(p);
 }
 const dl=document.createElement('dl');
 ligne(dl,'Statut communal','Aucune commune à Wallis-et-Futuna');
 ligne(dl,'Circonscriptions dans le COG 2026','Alo (98611), Sigave (98612), Uvea (98613)');
 target.append(dl);
 for(const [label,url]of [
   ['Insee : COG 2026, circonscriptions et territoires','https://www.insee.fr/fr/information/8740222'],
   ['Insee : codification historique de Wallis-et-Futuna','https://www.insee.fr/fr/information/7929495'],
   ['Légifrance : loi n° 61-814, articles 17 et 18','https://www.legifrance.gouv.fr/loda/id/JORFTEXT000000684031']
 ]){
  const p=document.createElement('p'),a=document.createElement('a');
  a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent=label;p.append(a);target.append(p);
 }
 const p=document.createElement('p');p.className='warning';
 p.textContent='Le code 98607 du COG historique porte le libellé « Nouvelle-Calédonie » : il n’est pas repris comme autorité Wallis-et-Futuna ni relié par succession automatique à 986. Aucun contour historique, aucun alignement Pactols et aucune assimilation des circonscriptions à des communes ou à leurs royaumes coutumiers n’est publié.';
 target.append(p);
}
function detail(){const target=$('detail');target.replaceChildren();const x=state.selected;
 const kicker=document.createElement('div');kicker.className='kicker';kicker.textContent=x?.kind==='commune'?'Référentiel communal COG / Pactols':x?.kind==='admin'?'Référentiel administratif IGN–COG':x?.kind==='cog2026'?'Commune COG · 2026':x?.kind==='cogHistoriqueGuyane'?'Commune historique · Guyane':x?.kind==='cogHistoriqueGuadeloupe'?'Commune historique · Guadeloupe':x?.kind==='autre_cog2026'?'Entité administrative COG · 2026':'Fiche du référentiel';target.append(kicker);
 if(!x){const h=document.createElement('h2'),p=document.createElement('p');h.textContent='Sélectionnez un territoire ou une commune';p.textContent='Utilisez la recherche ou cliquez sur les contours affichés. La recherche conserve les états COG et les correspondances Pactols existantes.';target.append(h,p);return}
 if(x.kind==='cogHistoriqueGuadeloupe'){
   const ancienne=state.guadeloupe?.old.get(x.code);
   if(!ancienne){state.selected=null;detail();return}
   const now=state.guadeloupe.etat(x.code,year());
   const all=state.guadeloupe.periodes(x.code);
   const heading=document.createElement('h2');
   heading.textContent=(now?.label||all.at(-1).label)+' · '+x.code;target.append(heading);
   const dl=document.createElement('dl');
   ligne(dl,'Ancien code INSEE',x.code);
   ligne(dl,'Épisode communal terminé le','23 février 2007 (fin exclusive)');
   ligne(dl,'Mouvement COG attesté','MOD 30 · 23 février 2007');
   ligne(dl,'Code communal après le mouvement (COM_AP)','Non renseigné dans le fichier des mouvements COG');
   ligne(dl,'Citation Pactols de l’ancienne URI INSEE','Aucune dans l’export RDF Lieux examiné du 22 juillet 2026');
   target.append(dl);
   afficherChronologieGuadeloupe(target,x.code);
   const note=document.createElement('p');note.className='warning';
   note.textContent='Cette ancienne commune est une autorité historique documentaire distincte. Le COG consulté ne fournit pas de code de destination dans la ligne MOD 30 ; aucune équivalence automatique avec une collectivité actuelle 977 ou 978, ni avec son concept Pactols, n’est déduite. Aucun contour historique n’est affiché.';
   target.append(note);
   afficherTransitionAntilles2007(target,x);
   return;
 }
 if(x.kind==='cogHistoriqueGuyane'){
   const ancienne=state.guyane?.old.get(x.code);
   if(!ancienne){state.selected=null;detail();return}
   const now=state.guyane.etat(x.code,year());
   const all=state.guyane.periodes(x.code);
   const heading=document.createElement('h2');
   heading.textContent=(now?.label||all.at(-1).label)+' · '+x.code;target.append(heading);
   const dl=document.createElement('dl');
   ligne(dl,'Ancien code INSEE',x.code);
   ligne(dl,'Concept Pactols historique identifié (lien non encore arbitré)',
     ancienne.ark_candidat,'https://ark.frantiq.fr/ark:/'+ancienne.ark_candidat);
   ligne(dl,'Mouvement COG attesté','Fusion simple (MOD 31) · 27 mars 1969');
   const destination=state.outremer.get('DROM:COM:'+ancienne.code_destination_mouvement_COG_1969);
   ligne(dl,'Code de la commune de destination',ancienne.code_destination_mouvement_COG_1969+
     (destination?' · '+destination.label:''));
   target.append(dl);
   afficherChronologieGuyane(target,x.code);
   const note=document.createElement('p');note.className='warning';
   note.textContent='La fusion administrative est documentée par le COG. Elle ne signifie pas que cet ARK Pactols historique équivaut à l’ARK Pactols de la commune de destination.';
   target.append(note);
   return;
 }
 if(x.kind==='cog2026'||x.kind==='autre_cog2026'){
   const entry=state.outremer?.get(x.id);
   if(!entry){state.selected=null;detail();return}
   const h=document.createElement('h2');h.textContent=entry.label;target.append(h);
   const dl=document.createElement('dl');
   ligne(dl,'Identifiant COG',entry.id);
   ligne(dl,'Code géographique',entry.code);
   ligne(dl,'Nature',entry.type);
   if(entry.parent)ligne(dl,'Territoire de rattachement (2026)',entry.parent);
   ligne(dl,'État documenté','COG au 1er janvier 2026');
   if(entry.kind==='cog2026'){
     if(entry.arkValide){
       ligne(dl,'Correspondance Pactols validée (2026)',entry.arkValide,
         'https://ark.frantiq.fr/ark:/'+entry.arkValide);
     }else if(entry.arkConfirme){
       ligne(dl,'ARK identifié (lien COG non validé)',entry.arkConfirme);
     }
   }
   target.append(dl);
   const source=document.createElement('p'),a=document.createElement('a');
   a.href='https://www.insee.fr/fr/information/8740222';
   a.target='_blank';a.rel='noopener noreferrer';
   a.textContent='Source administrative : Insee, COG 2026';
   source.append(a);target.append(source);
   const note=document.createElement('p');note.className='warning';
   if(entry.kind==='cog2026'){
     note.textContent=entry.geomStatut==='PRESENTE_INVALIDE'?
       'Le contour national 2026 présente une anomalie topologique : aucune géométrie de remplacement n’est adoptée ou affichée dans ce module.':
       'Un contour national 2026 est identifié, mais sa géométrie n’a pas encore été qualifiée pour publication dans ce module. Aucune limite de cette commune n’est affichée.';
   }else{
     note.textContent='Cette entité administrative n’est pas une commune dans le sélecteur territorial. Aucun contour de ce zonage n’est publié dans ce module.';
   }
   target.append(note);
   if(entry.arkConfirme){
     const p=document.createElement('p');p.className='warning';
     p.textContent='L’identifiant ARK est confirmé, mais la correspondance Pactols–COG demeure à valider : elle n’est pas présentée comme un alignement.';
     target.append(p);
   }else if(entry.kind==='cog2026'&&!entry.arkValide){
     const p=document.createElement('p');p.className='source';
     p.textContent='Aucune correspondance Pactols individuellement approuvée pour cette fiche COG 2026.';
     target.append(p);
   }
   if(entry.kind==='cog2026'&&entry.code.startsWith('973')){
     afficherChronologieGuyane(target,entry.code);
   }else if(entry.kind==='cog2026'&&entry.code.startsWith('972')){
     afficherChronologieMartinique(target,entry.code);
   }else if(entry.kind==='cog2026'&&entry.code.startsWith('971')){
     afficherChronologieGuadeloupe(target,entry.code);
    }else if(entry.kind==='cog2026'&&entry.code.startsWith('974')){
      afficherChronologieReunion(target,entry.code);
    }else if(entry.kind==='cog2026'&&entry.code.startsWith('976')){
      afficherChronologieMayotte(target,entry.code);
    }else if(entry.kind==='cog2026'&&entry.code.startsWith('975')){
      afficherChronologieSPM(target,entry);
    }else if(entry.kind==='autre_cog2026'&&entry.id==='COMER:TERRITOIRE:975'){
      afficherChronologieSPM(target,entry);
   }
    else if(entry.kind==='autre_cog2026'&&
      ['COMER:TERRITOIRE:977','COMER:TERRITOIRE:978','COMER:COM:97701','COMER:COM:97801'].includes(entry.id)){
      afficherTransitionAntilles2007(target,entry);
    }else if(entry.kind==='autre_cog2026'&&
      (entry.id==='COMER:TERRITOIRE:986'||/^COMER:CIR:9861[123]$/.test(entry.id))){
      afficherChronologieWallisFutuna(target,entry);
    }else if(year()!==2026){
     const p=document.createElement('p');p.className='warning';
     p.textContent='Le curseur indique '+year()+', mais cette fiche décrit exclusivement l’état COG 2026. Aucune équivalence rétroactive, succession ni limite géographique historique n’a été validée pour ce résultat.';
     target.append(p);
   }
   return;
 }
 if(x.kind==='admin'){
   const f=selectedFeature();if(!f){state.selected=null;detail();return};const p=f.properties;
   const h=document.createElement('h2');h.textContent=p.nom;target.append(h);
   const dl=document.createElement('dl');ligne(dl,'Échelon',label[x.level]);ligne(dl,'Code COG',p.code);ligne(dl,'État',`1er janvier ${x.year}`);
   if(x.year===2026)ligne(dl,'Édition des contours','4 mai 2026 · data.gouv.fr / IGN Admin Express');
   else if(ANNEES_PONTS.includes(x.year))
     ligne(dl,'Édition des contours','IGN ADMIN EXPRESS COG '+geo.edition_IGN[String(x.year)]+' · généralisation 100 m');
   else if(ANNEES_QUALIFIEES.includes(x.year))
     ligne(dl,'Édition des contours','Millésime '+x.year+' · Etalab / IGN, généralisation 100 m');
   else ligne(dl,'Édition IGN',geo.edition_IGN[String(x.year)]);
   if(x.level==='departement')ligne(dl,'Région de rattachement',`${p.nom_region_parent} (${p.code_region_parent})`);
   if(x.level==='region')ligne(dl,'Composition',`${p.departements.length} départements`);
   target.append(dl);
   if(x.year===2026&&((x.level==='region'&&p.code==='06')||(x.level==='departement'&&p.code==='976'))){
     const spec=document.createElement('p');spec.className='warning';
     spec.textContent='Mayotte : le COG 2026 conserve les identifiants géographiques de région 06 et de département 976 ; la collectivité à statut particulier Département-Région de Mayotte porte l’identifiant distinct 976R, non représenté ici comme autorité régionale.';
     target.append(spec);
   }
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