-- ==============================================================================
-- 01_schemas_and_audit.sql
-- Initialisation des schémas et de la couche d'audit
-- ==============================================================================

CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS ref;
CREATE SCHEMA IF NOT EXISTS dwh;

-- Table : audit.lot_import (traçabilité de chaque exécution de pipeline)
CREATE TABLE IF NOT EXISTS audit.lot_import (
    lot_id      BIGSERIAL PRIMARY KEY,
    source      VARCHAR(50)  NOT NULL, -- 'caisse' | 'b2b' | 'stock'
    fichier     TEXT         NOT NULL,
    debut       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    fin         TIMESTAMPTZ,
    statut      VARCHAR(20)  NOT NULL CHECK (statut IN ('EN_COURS', 'CHARGE', 'A_REVOIR', 'ECHEC')),
    lues        INT          DEFAULT 0,
    chargees    INT          DEFAULT 0,
    rejetees    INT          DEFAULT 0
);

-- Table : audit.rejet (détail ligne par ligne des rejets qualité)
CREATE TABLE IF NOT EXISTS audit.rejet (
    rejet_id     BIGSERIAL PRIMARY KEY,
    lot_id       BIGINT REFERENCES audit.lot_import(lot_id) ON DELETE CASCADE,
    ligne_source TEXT,
    motif        TEXT NOT NULL,
    code_regle   VARCHAR(50), -- Ex: RG-02, RG-10, DEF-01, etc.
    contenu      JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Table : audit.correction (traçabilité des nettoyages automatiques appliqués)
CREATE TABLE IF NOT EXISTS audit.correction (
    id           BIGSERIAL PRIMARY KEY,
    lot_id       BIGINT REFERENCES audit.lot_import(lot_id) ON DELETE CASCADE,
    champ        VARCHAR(100),
    valeur_avant TEXT,
    valeur_apres TEXT,
    code_regle   VARCHAR(50), -- RG-20, RG-21, RG-22
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index d'audit
CREATE INDEX IF NOT EXISTS idx_audit_rejet_lot ON audit.rejet(lot_id);
CREATE INDEX IF NOT EXISTS idx_audit_rejet_code ON audit.rejet(code_regle);
CREATE INDEX IF NOT EXISTS idx_audit_correction_lot ON audit.correction(lot_id);
