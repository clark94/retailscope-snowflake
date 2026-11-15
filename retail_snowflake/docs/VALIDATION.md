# Validation du livrable

Vérifications effectuées le 31/10/2026 :

- Génération reproductible des cinq CSV.
- Quatre tests Python : réconciliation des lignes, calcul indépendant avec Decimal,
  granularité des stocks/objectifs, reproductibilité et cohérence des commandes.
- Démarrage de Streamlit avec AppTest, indicateurs initiaux, filtre Lyon et sélection vide.
- Analyse syntaxique des quatre fichiers SQL avec le dialecte Snowflake de sqlglot.

Référence locale : 6000 ventes valides, 3000 commandes, 6 rejets, 10 doublons,
CA net 1 521 543,00 EUR, marge estimée 484 590,25 EUR.

Une analyse syntaxique n'est pas une exécution Snowflake.
La connexion réelle, PUT, COPY, MERGE et les droits doivent être vérifiés dans votre compte
avec les contrôles `04_checks.sql`. Aucun accès à votre compte n'a été utilisé.
