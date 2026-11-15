# Importer le projet dans Snowflake

## 0. Vérifier le compte

Utiliser votre compte personnel d'apprentissage ou un environnement de développement autorisé.
Un essai Snowflake et des crédits AWS sont deux choses distinctes. Aucune clé AWS n'est nécessaire.
Dans Snowsight, vérifier le solde, la date d'expiration et les droits de création.
Le rôle SYSADMIN peut convenir à un compte personnel ; en entreprise demander un rôle dédié à l'administrateur.
Ne jamais publier `.env` ni transmettre vos identifiants.

## Méthode A — Depuis le navigateur, sans Python pour l'import

### 1. Créer les objets

Dans Snowflake/Snowsight, ouvrir un éditeur SQL (SQL Worksheet, ou éditeur SQL dans un Workspace selon l'interface).
Choisir le rôle autorisé. Copier tout le contenu de `sql/01_setup.sql` et l'exécuter dans l'ordre.
Le script crée le warehouse `RETAIL_WH`, la base `RETAIL_CLARK`, les schémas `RAW`, `MART`, `DQ`
et les cinq tables RAW. Les intitulés des menus peuvent varier selon votre interface.

### 2. Importer les CSV dans les tables EXISTANTES

Dans l'explorateur des bases et schémas, ouvrir `RETAIL_CLARK` → `RAW`.
Pour chaque table ci-dessous, choisir **Load data / Charger des données**, puis charger le fichier correspondant :

| Fichier sur votre PC | Table cible existante | Lignes attendues |
|---|---|---:|
| produits.csv | RETAIL_CLARK.RAW.PRODUITS | 30 |
| magasins.csv | RETAIL_CLARK.RAW.MAGASINS | 6 |
| ventes.csv | RETAIL_CLARK.RAW.VENTES | 6016 |
| stocks.csv | RETAIL_CLARK.RAW.STOCKS | 180 |
| objectifs.csv | RETAIL_CLARK.RAW.OBJECTIFS | 36 |

Sélectionner `RETAIL_WH` comme warehouse de chargement.
Choisir CSV, virgule, UTF-8, première ligne d'en-tête à ignorer (SKIP_HEADER=1),
guillemets doubles facultatifs. Utiliser `RETAIL_CLARK.RAW.FF_CSV` si l'assistant propose un format existant.
Vérifier que l'en-tête n'est pas traité comme une ligne de données et que les colonnes correspondent.
Les colonnes RAW doivent rester VARCHAR : les erreurs de date/prix seront traitées ensuite en SQL.
Prévisualiser et confirmer le chargement. Ne pas importer deux fois le même fichier via cet assistant.

Avec cette méthode, **ne pas exécuter `02_load.sql`** : les données sont déjà dans les tables.
Le stage existe mais vous n'avez pas besoin de l'alimenter.

### 3. Construire le modèle

Ouvrir une feuille SQL et exécuter tout `sql/03_model.sql` dans l'ordre.
Puis exécuter `sql/04_checks.sql`.
Attendu : 6016 brutes, 6000 valides, 6 rejets, 10 doublons.
Les six motifs de rejet doivent compter une ligne chacun.
Comparer les montants au fichier `RESULTATS_ATTENDUS.json`.

### 4. Explorer les résultats

```sql
USE WAREHOUSE RETAIL_WH;
SELECT * FROM RETAIL_CLARK.MART.KPI_MENSUELS ORDER BY MOIS, MAGASIN_ID;
SELECT * FROM RETAIL_CLARK.DQ.V_REJETS;
SELECT * FROM RETAIL_CLARK.MART.V_VENTES_DETAIL LIMIT 20;
```

Pour afficher le tableau de bord local connecté, configurer `.env` comme dans la méthode B
puis lancer Streamlit et choisir **Snowflake** dans la barre latérale.

## Méthode B — Automatique depuis votre ordinateur

Cette méthode crée les objets, dépose les fichiers dans le stage, lance COPY, puis construit le modèle.
Ne pas la cumuler avec un premier import manuel des mêmes fichiers.

1. Installer les dépendances comme dans README.md.
2. Copier `.env.example` vers `.env` et remplir le compte et l'utilisateur.
3. Dans les détails de connexion du compte Snowsight, copier l'identifiant du compte au format
   `organisation-compte` fourni par Snowflake. Ne pas coller l'URL complète `https://...`.
4. Utiliser le nom de connexion Snowflake, pas forcément votre adresse email.
5. Conserver `SNOWFLAKE_ROLE=SYSADMIN` uniquement si votre compte personnel possède ce rôle.

Windows PowerShell :
```powershell
Copy-Item .env.example .env
.\.venv\Scripts\python.exe scripts/load_snowflake.py
```

macOS / Linux :
```bash
cp .env.example .env
.venv/bin/python scripts/load_snowflake.py
```

Le navigateur s'ouvre pour l'authentification et la MFA éventuelle. Effectuer cette connexion vous-même.
`externalbrowser` nécessite une session de bureau sur votre PC et une configuration d'authentification compatible ;
sur un serveur sans navigateur, demander une méthode d'authentification adaptée (par exemple clé privée).
Le script ne stocke aucun mot de passe.

Le script utilise PUT depuis le connecteur Python ; ne pas coller une commande PUT de fichier local dans une feuille SQL Snowsight.
Après succès : lancer Streamlit, choisir **Snowflake**, puis vérifier les mêmes résultats que dans la démo locale.

## Dépannage

| Symptôme | Action |
|---|---|
| Insufficient privileges | Choisir un rôle autorisé ou demander les privilèges de développement ; ne pas modifier les droits d'un compte d'entreprise sans accord. |
| Object does not exist | Exécuter 01, importer les CSV, puis 03 ; vérifier la base RETAIL_CLARK et le rôle. |
| 0 fichiers chargés avec COPY | Si déjà importés, c'est normal ; sinon LIST @RETAIL_CLARK.RAW.CSV_STAGE et vérifier les noms CSV. |
| Mauvais nombre de colonnes | Virgule comme séparateur ; ne pas réenregistrer les CSV avec un point-virgule depuis Excel. |
| Une ligne de trop par table | L'en-tête a été chargé comme donnée ; repartir d'un environnement de démo propre. |
| 0 ventes dans l'application | Vérifier les filtres, les tables RAW, puis relancer 03_model.sql. |
| Login navigateur impossible | Vérifier compte, utilisateur, méthode d'authentification et politique MFA ; demander l'aide de l'administrateur si nécessaire. |

## Fin de séance

Fermer l'application Streamlit et les sessions actives. Le warehouse se suspend après 60 secondes d'inactivité.
Pour le suspendre explicitement après avoir fini :
```sql
ALTER WAREHOUSE RETAIL_WH SUSPEND;
```
Une nouvelle requête peut le redémarrer automatiquement. Le stockage reste présent même warehouse suspendu.
