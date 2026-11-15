"""Import depuis le PC : python scripts/load_snowflake.py. Authentification navigateur."""
import os,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    from dotenv import load_dotenv
    import snowflake.connector
    load_dotenv(ROOT/'.env')
    for key in ['SNOWFLAKE_ACCOUNT','SNOWFLAKE_USER']:
        if not os.getenv(key):raise SystemExit(f'Renseigner {key} dans .env (voir .env.example).')
    with snowflake.connector.connect(account=os.environ['SNOWFLAKE_ACCOUNT'],user=os.environ['SNOWFLAKE_USER'],
          role=os.getenv('SNOWFLAKE_ROLE','SYSADMIN'),authenticator='externalbrowser') as conn:
        def run(name):
            print('Exécution',name)
            with (ROOT/'sql'/name).open(encoding='utf-8') as f:
                for cur in conn.execute_stream(f):
                    try:
                        if cur.description:print(cur.fetchall()[:8])
                    finally:cur.close()
        run('01_setup.sql')
        with conn.cursor() as cur:
            for path in sorted((ROOT/'data').glob('*.csv')):
                uri=path.resolve().as_uri().replace("'","''")
                cur.execute(f"PUT '{uri}' @RETAIL_CLARK.RAW.CSV_STAGE AUTO_COMPRESS=TRUE OVERWRITE=FALSE")
                print(path.name,cur.fetchall())
        for name in ['02_load.sql','03_model.sql','04_checks.sql']:run(name)
        print('Import terminé. Lancer python -m streamlit run app.py puis choisir Snowflake.')
if __name__=='__main__':main()
