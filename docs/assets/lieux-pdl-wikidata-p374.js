/* PDL 2026 — 17 concepts Pactols : exactMatch Wikidata → P374 INSEE → COG. */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxPDLWikidataP374=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const SCHEMA='adlfi.lieux.pactols.pdl.wikidata-p374.2026.public.v1';
 const SOURCE='recette/lieux/PDL-17-WIKIDATA-P374-PUBLICATION-2026.md';
 const QUALIF='recette/lieux/PDL-17-WIKIDATA-P374-2026.json';
 const SHA='3a0effe42a27da20c30497a6847fc1becbb736745945f01e4321b4791f0067c7';
 const normalise=s=>String(s??'').replace(/œ/gi,'oe').normalize('NFKD')
  .replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('fr')
  .replace(/[^a-z0-9]+/g,' ').trim().replace(/\s+/g,' ');

 function creer(pub,cog,base,uuid,lot01,chemille,lot02,oree){
  if(pub?.schema!==SCHEMA||pub.region!=='pdl'||pub.millesime_cog!=='2026-01-01'||
     pub.source_RDF_Pactols_sha256!==SHA||pub.source_registre!==SOURCE||
     pub.source_qualification!==QUALIF||
     pub.source_COG!=='docs/data/lieux-chronologie/cog-pdl.json'||
     pub.alignements_publies_precedemment!==1195||pub.nouveaux_alignements!==17||
     pub.total_alignements_PDL_2026!==1212||pub.communes_PDL_COG_2026!==1228||
     pub.communes_a_instruire!==16||pub.geometries_nouvelles!==0||
     pub.liens_historiques_inferes!==0||pub.alignements_Pactols_COG_valides_2026?.length!==17||
     cog?.region!=='pdl'||cog.geometries_historiques?.length!==0||
     base?.byCode?.size!==1140||uuid?.byCode?.size!==3||
     lot01?.byCode?.size!==5||chemille?.byCode?.size!==1||
     lot02?.byCode?.size!==45||oree?.byCode?.size!==1)
   throw Error('PDL Wikidata P374 : registre et publications non conformes');

  const previous=[...base.byCode.values(),...uuid.byCode.values(),
       ...lot01.byCode.values(),...chemille.byCode.values(),
       ...lot02.byCode.values(),...oree.byCode.values()];
  const usedCodes=new Set(previous.map(a=>a.code_insee));
  const usedArks=new Set(previous.map(a=>a.ark_pactols));
  if(previous.length!==1195||usedCodes.size!==1195||usedArks.size!==1195)
   throw Error('PDL Wikidata P374 : les 1195 identités antérieures ne sont pas uniques');
  const current=new Map();
  for(const p of cog.periodes_com){
    if(p.typecom==='COM'&&p.debut_inclus<='2026-01-01'&&
       (!p.fin_exclue||p.fin_exclue>'2026-01-01')){
      if(current.has(p.code_insee))throw Error('PDL Wikidata P374 : COM COG dupliquée');
      current.set(p.code_insee,p);
    }
  }
  if(current.size!==1228)throw Error('PDL Wikidata P374 : 1228 communes attendues');

  const codes=new Set(),arks=new Set(),historiques=new Set(),qids=new Set(),byCode=new Map();
  for(const a of pub.alignements_Pactols_COG_valides_2026){
    const code=a.code_insee,ark=a.ark_pactols;
    const qid=a.qid_Wikidata,old=a.ark_ancienne_commune_distinct,c=current.get(code);
    if(!c||codes.has(code)||arks.has(ark)||historiques.has(old)||qids.has(qid)||
       usedCodes.has(code)||usedArks.has(ark)||usedArks.has(old)||
       !/^26678\/[A-Za-z0-9]+$/.test(ark||'')||
       !/^26678\/[A-Za-z0-9]+$/.test(old||'')||
       !/^Q[1-9][0-9]+$/.test(qid||'')||ark===old||
       a.libelle_COG_2026!==c.libelle||normalise(a.libelle_pactols)!==normalise(c.libelle)||
       a.URI_Wikidata_exactMatch!=='https://www.wikidata.org/wiki/'+qid||
       !Number.isInteger(a.revision_Wikidata)||a.revision_Wikidata<1||
       a.revision_Wikidata_url!==
           'https://www.wikidata.org/w/index.php?title='+qid+'&oldid='+a.revision_Wikidata||
       a.code_INSEE_Wikidata_P374!==code||
       a.predicat_Pactols!=='skos:exactMatch'||a.predicat_Wikidata_INSEE!=='P374'||
       a.source_RDF_Pactols_sha256!==SHA||a.source_qualification!==QUALIF||
       a.source_registre!==SOURCE||a.date_creation_COG!==c.debut_inclus||
       a.nature_evenement_COG!=='MOD32_CREATION_COMMUNE_NOUVELLE'||
       a.date_validation!=='2026-11-18'||a.millesime_validation!==2026||
       a.statut!=='correspondance_PDL_Wikidata_P374_validee_2026'||
       a.portee_chronologique!=='2026_SEULEMENT'||
       a.relations_historiques_inferees!==0)
     throw Error('PDL Wikidata P374 : identité et sources non vérifiées '+code);
    const moves=cog.lignes_mouvements_cog.filter(m=>m.mod==='32'&&
       m.date_effet===c.debut_inclus&&m.code_apres===code&&
       m.typecom_apres==='COM'&&m.libelle_apres===c.libelle);
    if(!moves.length)
      throw Error('PDL Wikidata P374 : création MOD32 absente '+code);
    const ancien=cog.periodes_com.filter(p=>p.typecom==='COM'&&
       p.code_insee===code&&p.fin_exclue===c.debut_inclus&&
       normalise(p.libelle)===normalise((a.libelle_ancienne_commune||'').split(' (')[0]));
    if(ancien.length!==1)
      throw Error('PDL Wikidata P374 : ancienne commune différente '+code);
    codes.add(code);arks.add(ark);historiques.add(old);qids.add(qid);byCode.set(code,a);
  }
  if(codes.size!==17||arks.size!==17||historiques.size!==17||qids.size!==17||
      [...arks].some(a=>historiques.has(a)))
   throw Error('PDL Wikidata P374 : collision interne ARK');
  const index=[...byCode.values()].map(a=>({
    kind:'pactols',id:'pactols:'+a.ark_pactols,zone:'pdl',
    code:a.code_insee,ark:a.ark_pactols,label:a.libelle_COG_2026,
    noms:[a.libelle_COG_2026,a.libelle_pactols],
    champs:[a.libelle_COG_2026,a.libelle_pactols,a.code_insee,a.ark_pactols,
            a.qid_Wikidata].map(normalise)
  }));
  return {byCode,index};
 }
 return {creer};
}));