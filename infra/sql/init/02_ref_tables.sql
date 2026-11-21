-- ==============================================================================
-- 02_ref_tables.sql
-- Référentiels maîtres et table de correspondances externes
-- ==============================================================================

-- Table de correspondance externe (ADR-0001, RG-03)
CREATE TABLE IF NOT EXISTS ref.ref_externe (
    type_entite       VARCHAR(20) NOT NULL CHECK (type_entite IN ('PRODUIT', 'CLIENT')),
    source            VARCHAR(50) NOT NULL, -- 'caisse' | 'b2b' | 'stock'
    reference_externe VARCHAR(100) NOT NULL,
    entite_id         VARCHAR(50)  NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    PRIMARY KEY (type_entite, source, reference_externe)
);

CREATE INDEX IF NOT EXISTS idx_ref_externe_entite ON ref.ref_externe(entite_id);

-- Grille tarifaire (ADR-0003)
CREATE TABLE IF NOT EXISTS ref.grille_tarifaire (
    id               SERIAL PRIMARY KEY,
    categorie_client VARCHAR(50) NOT NULL,
    palier_min       INT NOT NULL,
    palier_max       INT, -- NULL si pas de limite supérieure (ex: 50+)
    remise_pct       NUMERIC(5,2) NOT NULL CHECK (remise_pct BETWEEN 0 AND 100),
    date_effet       DATE NOT NULL DEFAULT CURRENT_DATE
);
