(() => {
 'use strict';
 fetch('data/organismes.json').then(r=>r.ok?r.json():Promise.reject(new Error(r.status)))
   .then(data=>{
     const counts=document.querySelectorAll('#home-kpis .metric strong');
     if(counts.length>=2){
       counts[0].textContent=Number(data.totals.authorities).toLocaleString('fr-FR');
       counts[1].textContent=Number(data.totals.catalog_included).toLocaleString('fr-FR');
     }
   }).catch(()=>{ /* Les chiffres statiques restent visibles hors serveur local. */ });
})();