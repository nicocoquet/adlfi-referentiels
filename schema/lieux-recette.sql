-- AdlFI Lieux : schéma des données de RECETTE (non publiables).
-- Adapté du schéma relationnel de travail du 15 novembre 2026.
-- Les contraintes s'appliquent aux identités et aux liens, jamais aux équivalences SKOS.
PRAGMA foreign_keys = ON;

CREATE TABLE dossiers (
  identifiant_dossier TEXT PRIMARY KEY NOT NULL,
  region TEXT, lot TEXT, priorite TEXT, objet_instruction TEXT,
  ark_source TEXT, libelle_source TEXT, code_insee_source TEXT,
  ark_cible_candidat TEXT, libelle_cible TEXT, code_insee_cible TEXT,
  evenement_cog_date TEXT, qualification_candidate TEXT, niveau_preuve TEXT,
  source_documentaire TEXT, statut_instruction TEXT, action_suivante TEXT,
  famille_instruction TEXT
);
CREATE TABLE validations (
  identifiant_dossier TEXT PRIMARY KEY NOT NULL REFERENCES dossiers(identifiant_dossier),
  decision_editoriale TEXT, justification TEXT, responsable_validation TEXT,
  date_validation TEXT, assertion_editoriale TEXT, relation_typee TEXT,
  typecom_portee TEXT, validite_debut TEXT, validite_fin TEXT,
  preuve_editoriale TEXT, controle_orientation TEXT, controle_validation TEXT,
  statut_export TEXT
);
CREATE TABLE concepts_pactols (
  ark TEXT PRIMARY KEY NOT NULL,
  libelles_documentaires_observes TEXT, codes_insee_mentionnes TEXT,
  source_provenance TEXT, statut_identification TEXT, nb_libelles INTEGER
);
CREATE TABLE couples_neutres (
  id_dossier TEXT PRIMARY KEY NOT NULL REFERENCES dossiers(identifiant_dossier),
  ark_a TEXT NOT NULL REFERENCES concepts_pactols(ark),
  ark_b TEXT REFERENCES concepts_pactols(ark),
  nom_a TEXT, nom_b TEXT, code_a_mention TEXT, code_b_mention TEXT,
  qualification_source TEXT, orientation TEXT, date_evenement_indice TEXT,
  source_documentaire TEXT, statut TEXT
);
CREATE TABLE evenements_cog (
  id_evenement TEXT PRIMARY KEY NOT NULL,
  region TEXT, date_effet TEXT, modalite_mod TEXT, phase TEXT,
  nom_receptrice TEXT, code_receptrice TEXT, qualification TEXT,
  source_preuve TEXT, statut_preuve TEXT, dossiers_lies TEXT
);
CREATE TABLE groupes_pdl (
  id_groupe TEXT PRIMARY KEY NOT NULL,
  code_suivi TEXT, date_effet TEXT, mod TEXT, nb_lignes_rattachees INTEGER,
  etats_avant TEXT, etats_apres TEXT, preuve TEXT, statut TEXT
);
CREATE TABLE liens_dossiers (
  id_dossier TEXT NOT NULL REFERENCES dossiers(identifiant_dossier),
  id_objet TEXT NOT NULL, type_objet TEXT NOT NULL, role TEXT, statut TEXT,
  PRIMARY KEY (id_dossier,id_objet,type_objet),
  CHECK (type_objet IN ('evenement','groupe_PDL'))
);
CREATE TABLE mouvements_cog (
  id_ligne TEXT PRIMARY KEY NOT NULL,
  id_evenement TEXT REFERENCES evenements_cog(id_evenement),
  region TEXT, date_effet TEXT, mod TEXT, typecom_av TEXT, code_av TEXT,
  libelle_av TEXT, typecom_ap TEXT, code_ap TEXT, libelle_ap TEXT,
  source TEXT, source_feuille TEXT, codes_suivis TEXT
);
CREATE TABLE periodes_cog (
  id_periode TEXT PRIMARY KEY NOT NULL,
  region TEXT, typecom TEXT, code_insee TEXT, libelle_cog TEXT,
  date_debut TEXT, date_fin_exclusive TEXT, source TEXT, portee TEXT,
  couverture TEXT
);
CREATE TABLE uri_pdl (
  id_dossier TEXT PRIMARY KEY NOT NULL REFERENCES dossiers(identifiant_dossier),
  ark TEXT REFERENCES concepts_pactols(ark),
  libelle TEXT, uri_insee_litterale TEXT, type_uri TEXT,
  code_candidat TEXT, typecom_candidat TEXT, episode TEXT,
  qualification TEXT, verification TEXT, statut TEXT,
  source_pactols TEXT, source_insee TEXT
);
CREATE TABLE conventions (
  id_convention TEXT PRIMARY KEY NOT NULL,
  MOD TEXT, statut TEXT, portee TEXT, regle TEXT, restrictions TEXT,
  date_accord TEXT, origine TEXT, source_documentaire TEXT
);
CREATE TABLE journal_arbitrages (
  date TEXT, id_objet TEXT, acte TEXT, objet TEXT, source TEXT,
  origine_accord TEXT, portee_restrictions TEXT
);
CREATE TABLE sources (
  source TEXT PRIMARY KEY NOT NULL,
  provenance TEXT, sha256 TEXT, utilisation TEXT
);
