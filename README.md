# RetailScope — Snowflake, SQL et Streamlit

Projet personnel de pilotage commercial pour le portfolio de Clark. Toutes les données sont fictives.
Périmètre : ventes d'avril à septembre 2026, 6 magasins, 30 produits ; stock au 30/09/2026.
Ce projet est une application Data/BI : les alertes de stock sont des règles métier, sans modèle IA.

## Commencer

1. Extraire le ZIP et ouvrir le dossier `retail_snowflake` dans VS Code.
2. Installer Python 3.11 ou 3.12.
3. Ouvrir le terminal dans ce dossier.

Windows PowerShell :
```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS / Linux :
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Ouvrir l'adresse indiquée par Streamlit, généralement http://localhost:8501.
Le mode **Démo locale** fonctionne immédiatement avec les CSV inclus, sans Snowflake.
Les dépendances utilisent des plages de versions ; ce n'est pas un environnement verrouillé.

## Importer dans Snowflake

Lire **docs/GUIDE_IMPORT_SNOWFLAKE.md** : méthode visuelle Snowsight et méthode Python automatisée.
Les deux méthodes sont alternatives : choisir une seule méthode pour le premier chargement.
Un compte Snowflake est nécessaire pour le mode cloud ; aucun service AWS n'est utilisé.
Le statut « pro gratuit » ne suffit pas à connaître le crédit ou l'échéance : vérifier votre compte.
Le warehouse est XSMALL et se suspend après 60 secondes d'inactivité. Les calculs et le stockage peuvent consommer des crédits.

## Ce qui est livré

- `data/` : cinq CSV UTF-8, séparateur virgule, point décimal, dates ISO.
- `sql/01_setup.sql` : base RETAIL_CLARK, schémas, warehouse, tables et stage.
- `sql/02_load.sql` : chargement CSV avec COPY INTO.
- `sql/03_model.sql` : validation, rejets, dédoublonnage, MERGE et vues métier.
- `sql/04_checks.sql` : contrôles SQL et indicateurs.
- `scripts/load_snowflake.py` : connexion navigateur, création, upload et import.
- `app.py` : tableau de bord local ou connecté à Snowflake.
- `tests/` : contrôles locaux de réconciliation, montants, granularité et reproductibilité.
- `docs/RESULTATS_ATTENDUS.json` : référence calculée sur les fichiers fournis.
- `docs/DICTIONNAIRE.md` : champs et règles métier.

## Architecture

CSV → RAW (texte brut) → validation DQ → MART (ventes, dimensions, stocks, objectifs) → Streamlit.

Une vente représente une ligne de commande ; une commande comporte ici deux lignes.
Les objectifs sont mensuels par magasin ; les stocks sont un instantané produit/magasin.
Ces trois granularités restent séparées pour éviter les doubles comptes.

## Relancer et étendre

Les mêmes fichiers sont normalement ignorés par COPY lorsqu'ils figurent encore dans son historique.
Le MERGE protège FACT_VENTE contre la réinsertion d'une même clé `ligne_id`.
L'historique COPY est limité dans le temps : ne pas en faire une garantie permanente d'unicité.
Le journal DQ conserve une nouvelle entrée par reconstruction ; ce n'est pas un journal transactionnel de chaque fichier.
Les doublons inclus sont identiques. Des corrections contradictoires d'une même clé dans plusieurs lots
nécessiteraient une date de mise à jour et une règle de priorité, non implémentées ici.
Les suppressions dans les fichiers ne suppriment pas les faits déjà chargés.
Pour repartir à zéro, utiliser une nouvelle base de développement ou supprimer explicitement cette base de démonstration
après avoir vérifié qu'elle ne contient aucune donnée à conserver. Aucun reset destructif automatique n'est fourni.

Le chargement est manuel, relançable, sans ordonnanceur. Pour une V2 : lots quotidiens datés,
validation des référentiels, alertes email, Snowflake Tasks, tests CI et rôles lecture seule.
Les référentiels, stocks et objectifs fournis sont valides ; la quarantaine détaillée porte sur les ventes.
Le coût d'achat est supposé constant : la marge est une estimation hors transport, retours et autres charges.

## Vérifier

```bash
python -m unittest discover -s tests -v
```

Utiliser le Python de `.venv` si l'environnement n'est pas activé.
Comparer ensuite `sql/04_checks.sql` à `docs/RESULTATS_ATTENDUS.json` dans votre compte Snowflake.
Les scripts cloud nécessitent vos identifiants et autorisations ; ils n'ont pas été exécutés sur un compte Snowflake lors de la préparation du ZIP.

## Présentation en entretien

1. Expliquer le besoin commercial et la granularité des tables.
2. Montrer les six rejets et les dix doublons.
3. Expliquer le MERGE et les limites des corrections multi-lots.
4. Montrer chiffre d'affaires, objectifs et couverture de stock.
5. Présenter le code SQL et une amélioration envisagée.

Après réalisation et compréhension : « Projet personnel : intégration et contrôle de données de ventes dans Snowflake,
modélisation décisionnelle, indicateurs SQL et tableau de bord Streamlit. »

## Sources techniques

Documentation consultée le 31/10/2026 :
- Chargement visuel : https://docs.snowflake.com/en/user-guide/data-load-web-ui
- Stage et COPY : https://docs.snowflake.com/en/user-guide/data-load-local-file-system-copy
- Connexion Python : https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect

Les CSV ont été générés pour cet exercice et ne proviennent d'aucune entreprise.
