/* Tests du contrat de données et de la fiche nationale, sans DOM ni réseau. */
'use strict';
const assert=require('node:assert/strict');
const m=require('../docs/assets/lieux-national.js');
function fixture() {
  return {
    pactols:{schema:'adlfi.lieux.pactols.xml.index.recette.v1',
      etat:'recette_non_publiee',autorites:[
        {ark_pactols:'26678/pcrtMarchaux',libelle_documentaire:'Marchaux',
         formes_attestees_xml:['Marchaux'],annees_operation_xml:[2017],
         occurrences_xml:1,notice_distinctes:1,statut:'aucune_validation_cog',
         correspondance_cog_validee_2026:null},
        {ark_pactols:'26678/pcrtDraix',libelle_documentaire:'Draix',
         formes_attestees_xml:['Draix'],annees_operation_xml:[2021],
         occurrences_xml:1,notice_distinctes:1,statut:'validation_existante_paca',
         correspondance_cog_validee_2026:{
           type:'correspondance_communale_editoriale_existante',
           code_insee:'04072',libelle_cog:'Draix',millesime:2026}},
        {ark_pactols:'26678/pcrtHauterocheJura',libelle_documentaire:'Hauteroche (Jura)',
         formes_attestees_xml:['Hauteroche (Jura)'],annees_operation_xml:[],
         occurrences_xml:3,notice_distinctes:2,statut:'aucune_validation_cog',
         correspondance_cog_validee_2026:null}
      ]},
    cog:{schema:'adlfi.lieux.cog.national.temporel.recette.v1',
      etat:'recette_non_publiee',entrees:[
        {code_insee:'25368',libelles_attestes:['Marchaux','Marchaux-Chaudefontaine']},
        {code_insee:'04072',libelles_attestes:['Draix']},
        {code_insee:'39177',libelles_attestes:['Crançot','Hauteroche']},
        {code_insee:'21314',libelles_attestes:['Hauteroche']},
        {code_insee:'71566',libelles_attestes:['Verdun-sur-le-Doubs','Verdun-Ciel']},
        {code_insee:'39012',libelles_attestes:['Antorpe']}
      ]}};
}
function segment(code,periods,complement=[],movements=[]) {
  return {schema:'adlfi.lieux.cog.national.temporel.recette.v1',
    etat:'recette_non_publiee',prefixe_code:code.slice(0,2),
    periodes_COM:periods,periodes_ARM:[],
    observations_COMA_COMD_2026:complement,
    mouvements:movements,validations_editoriales:[],geometries_historiques:[]};
}
const d=fixture();
const index=m.creerIndex(d.pactols,d.cog);
assert.equal(index.length,9);
assert.equal(m.chercher(index,'Marchaux').length,2);
assert.deepEqual(new Set(m.chercher(index,'Marchaux').map(x=>x.type)),
                 new Set(['cog','pactols']));
assert.equal(m.chercher(index,'Hauteroche').filter(x=>x.type==='cog').length,2);
assert.equal(m.chercher(index,'Hauteroche').filter(x=>x.type==='pactols').length,1);
assert.equal(m.chercher(index,'Verdun-Ciel').length,1);
assert.equal(m.chercher(index,'Verdun-Ciel')[0].type,'cog');
assert.equal(m.chercher(index,'26678/pcrtMarchaux')[0].type,'pactols');
assert.equal(m.chercher(index,'25368')[0].type,'cog');
assert.equal(m.chercher(index,'Œuvre').length,0);
assert.equal(m.normaliser('l’Œuvre'),'l oeuvre');
const march=m.chercher(index,'26678/pcrtMarchaux')[0];
assert.equal(m.fiche(march,null,2017).statut_relation,'aucune_correspondance_validee');
assert.equal(m.fiche(march,null,2017).correspondance_administrative,null);
const s25=segment('25368',[
  {code_insee:'25368',libelle:'Marchaux',debut_inclus:'1943-01-01',fin_exclue:'2018-01-01'},
  {code_insee:'25368',libelle:'Marchaux-Chaudefontaine',
   debut_inclus:'2018-01-01',fin_exclue:null}],
  [],[{id:'m1',date_effet:'2018-01-01',code_avant:'25368',code_apres:'25368',MOD:'32'}]);
const cogMarch=m.chercher(index,'25368')[0];
assert.equal(m.fiche(cogMarch,s25,2017).etat_admin.etat.libelle,'Marchaux');
assert.equal(m.fiche(cogMarch,s25,2018).etat_admin.etat.libelle,'Marchaux-Chaudefontaine');
assert.equal(m.fiche(cogMarch,s25,2017).etat_admin.mouvements_deja_survenus.length,0);
assert.equal(m.fiche(cogMarch,s25,2018).etat_admin.mouvements_deja_survenus.length,1);
assert.equal(m.fiche(cogMarch,s25,2018).ark_pactols,null);
const ant=segment('39012',[
  {code_insee:'39012',libelle:'Antorpe',debut_inclus:'1943-01-01',fin_exclue:'1974-06-01'}],
  [{code_insee:'39012',typecom:'COMA',libelle:'Antorpe',comparent_COG_2026:'25527'}]);
assert.equal(m.projectionCOG(ant,'39012',1974).qualification,'COM_ARM_historique_atteste');
assert.equal(m.projectionCOG(ant,'39012',1975).qualification,'etat_non_documente_a_cette_date');
assert.equal(m.projectionCOG(ant,'39012',2026).qualification,'COMA_COMD_observe_en_2026');
assert.equal(m.projectionCOG(ant,'39012',1975).etat,null);
assert.throws(()=>m.projectionCOG(ant,'25368',2026));
assert.throws(()=>m.projectionCOG(ant,'39012',2027));
const draix=m.chercher(index,'26678/pcrtDraix')[0];
const s04=segment('04072',[{code_insee:'04072',libelle:'Draix',
  debut_inclus:'1943-01-01',fin_exclue:null}]);
assert.equal(m.fiche(draix,s04,2026).correspondance_administrative.code_insee,'04072');
assert.equal(m.fiche(draix,s04,2026).statut_relation,'correspondance_COG_editeur_PACA_validee');
assert.equal(m.fiche(draix,s04,2026).portee_validation,'millesime_COG_2026_uniquement');
assert.equal(m.fiche(draix,s04,2026).consultation_COG_historique_meme_code,null);
assert.equal(m.fiche(draix,s04,2017).correspondance_administrative,null);
assert.equal(m.fiche(draix,s04,2017).consultation_COG_historique_meme_code.etat.libelle,'Draix');
// Aucun mécanisme de rapprochement lexical ne doit inventer ce lien.
assert.equal(m.fiche(m.chercher(index,'04072')[0],s04,2026).ark_pactols,null);
assert.throws(()=>m.creerIndex({...d.pactols,autorites:[
  {...d.pactols.autorites[0],statut:'validation_existante_paca'}]},d.cog));
// Contrôle des dix meilleurs résultats même avec beaucoup de noms communs.
const many=Array.from({length:1200},(_,i)=>({
  id:'cog:'+String(i).padStart(5,'0'),type:'cog',
  label:'Saint-Exemple-'+String(i).padStart(4,'0'),
  code:String(i).padStart(5,'0'),ark:null,
  noms:['Saint-Exemple-'+String(i).padStart(4,'0')],
  champs:[m.normaliser('Saint-Exemple-'+String(i).padStart(4,'0'))]
}));
const first10=m.chercher(many,'saint',10);
assert.equal(first10.length,10);
assert.deepEqual(first10,m.chercher(many,'saint',1200).slice(0,10));
console.log('Contrat Lieux national : recherche, fiches et curseur annuel OK.');
