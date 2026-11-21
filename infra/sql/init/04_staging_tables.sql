-- ==============================================================================
-- 04_staging_tables.sql
-- Couche de staging : ingestion brute sans altération des types d'origine
-- ==============================================================================

-- Staging Caisse (CSV)
CREATE TABLE IF NOT EXISTS staging.caisse_raw (
    staging_id          BIGSERIAL PRIMARY KEY,
    lot_id              BIGINT NOT NULL REFERENCES audit.lot_import(lot_id),
    ticket_id           TEXT,
    ligne_no            TEXT,
    date_vente          TEXT,
    ref_produit_caisse  TEXT,
    designation         TEXT,
    client_code         TEXT,
    quantite            TEXT,
    prix_unitaire       TEXT,
    remise_pct          TEXT,
    statut              TEXT,
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Staging B2B (JSON aplati ou brut)
CREATE TABLE IF NOT EXISTS staging.b2b_raw (
    staging_id          BIGSERIAL PRIMARY KEY,
    lot_id              BIGINT NOT NULL REFERENCES audit.lot_import(lot_id),
    order_id            TEXT,
    created_at          TEXT,
    customer_id         TEXT,
    customer_name       TEXT,
    status              TEXT,
    sku                 TEXT,
    qty                 TEXT,
    unit_price          TEXT,
    discount            TEXT,
    raw_payload         JSONB,
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Staging Mouvements Stock (CSV)
CREATE TABLE IF NOT EXISTS staging.stock_raw (
    staging_id          BIGSERIAL PRIMARY KEY,
    lot_id              BIGINT NOT NULL REFERENCES audit.lot_import(lot_id),
    mvt_id              TEXT,
    date_mvt            TEXT,
    code_article        TEXT,
    type_mvt            TEXT,
    quantite            TEXT,
    entrepot            TEXT,
    motif               TEXT,
    ref_document        TEXT,
    imported_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
