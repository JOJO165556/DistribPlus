-- ==============================================================================
-- 05_seeds.sql
-- Données initiales indispensables (canaux, entrepôts, client inconnu, calendrier)
-- ==============================================================================

-- Canaux de vente
INSERT INTO dwh.dim_canal (canal_sk, code, libelle) VALUES
    (1, 'caisse', 'Vente physique comptoir / caisse'),
    (2, 'b2b', 'Portail B2B en ligne')
ON CONFLICT (canal_sk) DO NOTHING;

-- Entrepots
INSERT INTO dwh.dim_entrepot (entrepot_sk, entrepot_id, libelle, localisation) VALUES
    (1, 'ENT-01', 'Entrepôt Principal', 'Dépôt Central')
ON CONFLICT (entrepot_sk) DO NOTHING;

-- Client Inconnu (client_sk = -1 pour les ventes comptoir sans compte client - RG-02/RG-04)
-- On autorise l'insertion manuelle de l'ID -1
INSERT INTO dwh.dim_client (client_sk, client_id, raison_sociale, categorie_client, date_debut, date_fin, est_courant)
VALUES
    (-1, 'INCONNU', 'Client comptoir / non renseigné', 'COMPTOIR', '2000-01-01', NULL, true)
ON CONFLICT (client_sk) DO NOTHING;

-- Generation de dim_temps sur 2024 - 2026
INSERT INTO dwh.dim_temps (
    date_sk,
    date_jour,
    annee,
    trimestre,
    mois,
    mois_nom,
    semaine,
    jour_semaine,
    jour_nom,
    est_weekend,
    est_ferie
)
SELECT
    TO_CHAR(d, 'YYYYMMDD')::INT AS date_sk,
    d::DATE AS date_jour,
    EXTRACT(YEAR FROM d)::INT AS annee,
    EXTRACT(QUARTER FROM d)::INT AS trimestre,
    EXTRACT(MONTH FROM d)::INT AS mois,
    TO_CHAR(d, 'TMMonth') AS mois_nom,
    EXTRACT(WEEK FROM d)::INT AS semaine,
    EXTRACT(ISODOW FROM d)::INT AS jour_semaine,
    TO_CHAR(d, 'TMDay') AS jour_nom,
    CASE WHEN EXTRACT(ISODOW FROM d) IN (6, 7) THEN true ELSE false END AS est_weekend,
    false AS est_ferie
FROM generate_series('2024-01-01'::DATE, '2026-12-31'::DATE, '1 day'::interval) AS d
ON CONFLICT (date_sk) DO NOTHING;
