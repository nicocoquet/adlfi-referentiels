import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('audit_pactols',ROOT/'scripts/auditer_export_pactols_lieux.py')
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class AuditSKOS(unittest.TestCase):
    def test_normalisation(self):
        self.assertEqual(m.norm('L’Île-aux-Œufs'),m.norm("L ile aux oeufs"))

    def test_audit_integral(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); rdf=d/'x.rdf'; master=d/'autorites.json'; out=d/'sorties'
            rdf.write_text('''<?xml version="1.0" encoding="utf-8"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:skos="http://www.w3.org/2004/02/skos/core#">
<skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtABCD"><skos:prefLabel xml:lang="fr">Église</skos:prefLabel><skos:altLabel xml:lang="fr">L'Eglise</skos:altLabel><skos:exactMatch rdf:resource="https://www.wikidata.org/wiki/Q1"/></skos:Concept>
<skos:Concept rdf:about="https://ark.frantiq.fr/ark:/26678/pcrtEFGH"><skos:prefLabel xml:lang="fr">Tarascon</skos:prefLabel></skos:Concept>
</rdf:RDF>''',encoding='utf8')
            items=[('26678/pcrtABCD','Église'),('26678/pcrtEFGH','Tarascon'),('26678/pcrtIJKL','Inconnu')]
            master.write_text(json.dumps({'unite':'concept_pactols_atteste_dans_XML','autorites':[{'ark_pactols':ark,'libelle_documentaire':label} for ark,label in items]}),encoding='utf8')
            report=m.audit(master,rdf,out,hashlib.sha256(rdf.read_bytes()).hexdigest())
            self.assertEqual(report['ark_analyses'],3)
            self.assertEqual(report['ark_trouves_dans_export'],2)
            self.assertEqual(report['repartition'],{'absent_export_date':1,'libelle_pref_fr_concordant':2})
            self.assertIn('wikidata', (out/'controle_concepts_pactols.csv').read_text(encoding='utf-8-sig'))

    def test_empreinte_invalide(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); rdf=d/'x.rdf';master=d/'a.json'
            rdf.write_text('<rdf:RDF/>');master.write_text(json.dumps({'unite':'concept_pactols_atteste_dans_XML','autorites':[]}))
            with self.assertRaisesRegex(ValueError,'Empreinte inattendue'):
                m.audit(master,rdf,d/'out','0'*64)

    def test_duplicate_ark(self):
        with tempfile.TemporaryDirectory() as d:
            d=Path(d); master=d/'a.json'
            master.write_text(json.dumps({'unite':'concept_pactols_atteste_dans_XML','autorites':[{'ark_pactols':'26678/pcrtABCD'},{'ark_pactols':'26678/pcrtABCD'}]}))
            with self.assertRaisesRegex(ValueError,'dupliqué'):
                m.charger_autorites(master)

if __name__=='__main__':unittest.main()
