USE WAREHOUSE RETAIL_WH;
USE DATABASE RETAIL_CLARK;
USE SCHEMA RAW;
-- Charger préalablement les 5 CSV à la racine du stage CSV_STAGE.
-- COPY ignore les mêmes fichiers déjà chargés (historique Snowflake limité dans le temps).
COPY INTO PRODUITS FROM @CSV_STAGE PATTERN='.*produits[.]csv([.]gz)?' ON_ERROR=ABORT_STATEMENT;
COPY INTO MAGASINS FROM @CSV_STAGE PATTERN='.*magasins[.]csv([.]gz)?' ON_ERROR=ABORT_STATEMENT;
COPY INTO VENTES FROM @CSV_STAGE PATTERN='.*ventes[.]csv([.]gz)?' ON_ERROR=ABORT_STATEMENT;
COPY INTO STOCKS FROM @CSV_STAGE PATTERN='.*stocks[.]csv([.]gz)?' ON_ERROR=ABORT_STATEMENT;
COPY INTO OBJECTIFS FROM @CSV_STAGE PATTERN='.*objectifs[.]csv([.]gz)?' ON_ERROR=ABORT_STATEMENT;
