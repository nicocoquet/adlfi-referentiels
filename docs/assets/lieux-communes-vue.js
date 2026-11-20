/* Déterminer les couches communales métropolitaines nécessaires à la vue Leaflet.
 * Les emprises sont des cadres de CHARGEMENT, pas des géométries administratives.
 * À petite échelle, conserver le comportement de la carte publiée : quatre
 * régions couvertes sont chargées pour offrir le repère communal national.
 */
(function(root,factory){
 'use strict';
 const api=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=api;
 if(root)root.AdlfiLieuxCommunesVue=api;
}(typeof window!=='undefined'?window:null,function(){
 'use strict';
 const ZOOM_REDUCTION=7;
 function valideCadre(b){
   return Array.isArray(b)&&b.length===2&&
     b.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite))&&
     b[0][0]<=b[1][0]&&b[0][1]<=b[1][1];
 }
 function intersecte(a,b){
   if(!valideCadre(a)||!valideCadre(b))throw Error('Cadre géographique invalide');
   return !(a[1][0]<b[0][0]||a[0][0]>b[1][0]||
            a[1][1]<b[0][1]||a[0][1]>b[1][1]);
 }
 function zonesPourVue(bounds,zoom,emprises){
   if(!valideCadre(bounds)||!Number.isFinite(zoom)||!emprises||
      typeof emprises!=='object'||Array.isArray(emprises))
     throw Error('Paramètres de vue non conformes');
   const keys=Object.keys(emprises);
   if(!keys.length)throw Error('Aucune couche enregistrée');
   for(const k of keys)if(!valideCadre(emprises[k]))
     throw Error('Emprise régionale non conforme : '+k);
   // Conserver le cadrage national et la présence des quatre régions au zoom <= 6.
   if(zoom<ZOOM_REDUCTION)return keys;
   return keys.filter(k=>intersecte(bounds,emprises[k]));
 }
 function cle(zones){
   if(!Array.isArray(zones)||zones.some(z=>typeof z!=='string'))
     throw Error('Identifiants de couche invalides');
   return [...new Set(zones)].sort().join('|');
 }
 return Object.freeze({ZOOM_REDUCTION,intersecte,zonesPourVue,cle});
}));
