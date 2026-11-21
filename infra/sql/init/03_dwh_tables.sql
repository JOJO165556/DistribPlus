-- ==============================================================================
-- 03_dwh_tables.sql
-- Entrepôt de données : Modèle dimensionnel en étoile (Kimball)
-- ==============================================================================

-- 1. Dimension Temps
CREATE TABLE IF NOT EXISTS dwh.dim_temps (
    date_sk      INT PRIMARY KEY, -- YYYYMMDD
    date_jour    DATE UNIQUE NOT NULL,
    annee        INT NOT NULL,
    trimestre    INT NOT NULL,
    mois         INT NOT NULL,
    mois_nom     VARCHAR(20) NOT NULL,
    semaine      INT NOT NULL,
    jour_semaine INT NOT NULL,
    jour_nom     VARCHAR(20) NOT NULL,
    est_weekend  BOOLEAN NOT NULL,
    est_ferie    BOOLEAN NOT NULL DEFAULT false
);

-- 2. Dimension Canal
CREATE TABLE IF NOT EXISTS dwh.dim_canal (
    canal_sk    SMALLINT PRIMARY KEY,
    code        VARCHAR(50) UNIQUE NOT NULL, -- 'caisse', 'b2b'
    libelle     VARCHAR(100) NOT NULL
);

-- 3. Dimension Entrepôt
CREATE TABLE IF NOT EXISTS dwh.dim_entrepot (
    entrepot_sk SMALLINT PRIMARY KEY,
    entrepot_id VARCHAR(50) UNIQUE NOT NULL, -- 'ENT-01'
    libelle     VARCHAR(100) NOT NULL,
    localisation VARCHAR(100)
);

-- 4. Dimension Produit (SCD Type 2 - RG-08)
CREATE TABLE IF NOT EXISTS dwh.dim_produit (
    produit_sk    BIGSERIAL PRIMARY KEY,
    produit_id    VARCHAR(50) NOT NULL,
    libelle       VARCHAR(255) NOT NULL,
    categorie     VARCHAR(100) NOT NULL,
    cout_standard NUMERIC(14,2) NOT NULL DEFAULT 0,
    prix_base     NUMERIC(14,2) NOT NULL DEFAULT 0,
    date_debut    DATE NOT NULL,
    date_fin      DATE,
    est_courant   BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_dim_produit_id ON dwh.dim_produit(produit_id);
CREATE INDEX IF NOT EXISTS idx_dim_produit_courant ON dwh.dim_produit(produit_id, est_courant);

-- 5. Dimension Client (SCD Type 2 - client_sk = -1 : client comptoir / inconnu)
CREATE TABLE IF NOT EXISTS dwh.dim_client (
    client_sk        BIGSERIAL PRIMARY KEY,
    client_id        VARCHAR(50) NOT NULL,
    raison_sociale   VARCHAR(255) NOT NULL,
    categorie_client VARCHAR(50) NOT NULL,
    date_debut       DATE NOT NULL,
    date_fin         DATE,
    est_courant      BOOLEAN NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_dim_client_id ON dwh.dim_client(client_id);
CREATE INDEX IF NOT EXISTS idx_dim_client_courant ON dwh.dim_client(client_id, est_courant);

-- 6. Table de faits : Ventes (Grain : une ligne de ticket ou de commande)
CREATE TABLE IF NOT EXISTS dwh.fait_ventes (
    vente_sk      BIGSERIAL PRIMARY KEY,
    source        VARCHAR(50) NOT NULL, -- 'caisse' | 'b2b'
    commande_id   VARCHAR(100) NOT NULL,
    ligne_no      INT NOT NULL,
    date_sk       INT NOT NULL REFERENCES dwh.dim_temps(date_sk),
    produit_sk    BIGINT NOT NULL REFERENCES dwh.dim_produit(produit_sk),
    client_sk     BIGINT NOT NULL REFERENCES dwh.dim_client(client_sk),
    canal_sk      SMALLINT NOT NULL REFERENCES dwh.dim_canal(canal_sk),
    entrepot_sk   SMALLINT NOT NULL REFERENCES dwh.dim_entrepot(entrepot_sk),
    quantite      NUMERIC(14,3) NOT NULL CHECK (quantite > 0),
    prix_unitaire NUMERIC(14,2) NOT NULL CHECK (prix_unitaire >= 0),
    remise_pct    NUMERIC(5,2) NOT NULL CHECK (remise_pct BETWEEN 0 AND 100),
    cout_unitaire NUMERIC(14,2) NOT NULL,
    montant_ht    NUMERIC(16,2) NOT NULL,
    marge         NUMERIC(16,2) NOT NULL,
    statut        VARCHAR(20) NOT NULL CHECK (statut IN ('VALIDE', 'ANNULE')),
    lot_id        BIGINT NOT NULL REFERENCES audit.lot_import(lot_id),
    CONSTRAINT uq_fait_ventes_idempotence UNIQUE (source, commande_id, ligne_no)
);

-- Index sur clés étrangères de fait_ventes
CREATE INDEX IF NOT EXISTS idx_fait_ventes_date ON dwh.fait_ventes(date_sk);
CREATE INDEX IF NOT EXISTS idx_fait_ventes_produit ON dwh.fait_ventes(produit_sk);
CREATE INDEX IF NOT EXISTS idx_fait_ventes_client ON dwh.fait_ventes(client_sk);
CREATE INDEX IF NOT EXISTS idx_fait_ventes_canal ON dwh.fait_ventes(canal_sk);
CREATE INDEX IF NOT EXISTS idx_fait_ventes_entrepot ON dwh.fait_ventes(entrepot_sk);
CREATE INDEX IF NOT EXISTS idx_fait_ventes_lot ON dwh.fait_ventes(lot_id);

-- 7. Table de faits : Mouvements de stock
CREATE TABLE IF NOT EXISTS dwh.fait_mouvement_stock (
    mvt_sk       BIGSERIAL PRIMARY KEY,
    mvt_id       VARCHAR(100) NOT NULL UNIQUE,
    date_sk      INT NOT NULL REFERENCES dwh.dim_temps(date_sk),
    produit_sk   BIGINT NOT NULL REFERENCES dwh.dim_produit(produit_sk),
    entrepot_sk  SMALLINT NOT NULL REFERENCES dwh.dim_entrepot(entrepot_sk),
    type_mvt     VARCHAR(20) NOT NULL CHECK (type_mvt IN ('ENTREE', 'SORTIE', 'AJUSTEMENT', 'INVENTAIRE')),
    quantite     INT NOT NULL,
    motif        TEXT,
    ref_document VARCHAR(100),
    lot_id       BIGINT NOT NULL REFERENCES audit.lot_import(lot_id)
);

CREATE INDEX IF NOT EXISTS idx_fait_mvt_date ON dwh.fait_mouvement_stock(date_sk);
CREATE INDEX IF NOT EXISTS idx_fait_mvt_produit ON dwh.fait_mouvement_stock(produit_sk);
CREATE INDEX IF NOT EXISTS idx_fait_mvt_entrepot ON dwh.fait_mouvement_stock(entrepot_sk);

-- 8. Table de faits : Instantané périodique de stock (par jour, produit et entrepôt)
CREATE TABLE IF NOT EXISTS dwh.fait_stock_jour (
    date_sk          INT NOT NULL REFERENCES dwh.dim_temps(date_sk),
    produit_sk       BIGINT NOT NULL REFERENCES dwh.dim_produit(produit_sk),
    entrepot_sk      SMALLINT NOT NULL REFERENCES dwh.dim_entrepot(entrepot_sk),
    stock_physique   INT NOT NULL,
    stock_reserve    INT NOT NULL,
    stock_disponible INT NOT NULL,
    PRIMARY KEY (date_sk, produit_sk, entrepot_sk)
);
