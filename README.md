# DistribPlus BI

Plateforme décisionnelle DistribPlus.
Stack : Python, PostgreSQL, dbt Core, Prefect, Metabase.

## Démarrage rapide

```bash
cp .env.example .env
docker compose up -d
```

Metabase accessible sur http://localhost:3000

## Structure du projet

```
.
├── src/
│   ├── generator/        # génération des données sources
│   ├── connectors/       # connecteurs (caisse, b2b, stock)
│   ├── quality/          # validation, normalisation, rejets
│   ├── loading/          # ingestion et chargement
│   └── orchestration/    # ordonnancement des flux
├── dbt/                  # modèles analytiques (staging, ref, marts)
├── infra/
│   └── sql/init/         # scripts DDL PostgreSQL
├── tests/                # tests
├── data/                 # données locales (ignoré par git)
│   ├── inbox/
│   ├── rejects/
│   └── archive/
├── docker-compose.yml
├── pyproject.toml
└── .env.example
```
