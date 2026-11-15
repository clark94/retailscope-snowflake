from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'scripts'))
import pandas as pd
import streamlit as st
from local_data import load_local

st.set_page_config(page_title='RetailScope · Clark',page_icon='📊',layout='wide')
st.title('RetailScope — Ventes et stocks')
st.caption('Projet personnel · Données fictives · Avril à septembre 2026 · Montants en euros hors taxes')
source=st.sidebar.radio('Source',['Démo locale','Snowflake'])
@st.cache_data(ttl=300)
def fetch(mode):
    if mode=='Démo locale':return load_local()
    import snowflake.connector
    import os
    from dotenv import load_dotenv
    load_dotenv()
    required=['SNOWFLAKE_ACCOUNT','SNOWFLAKE_USER']
    missing=[x for x in required if not os.getenv(x)]
    if missing:raise ValueError('Configurer le fichier .env : '+', '.join(missing))
    with snowflake.connector.connect(account=os.environ['SNOWFLAKE_ACCOUNT'],user=os.environ['SNOWFLAKE_USER'],
        authenticator='externalbrowser',role=os.getenv('SNOWFLAKE_ROLE','SYSADMIN'),
        warehouse='RETAIL_WH',database='RETAIL_CLARK',schema='MART') as conn:
        def read(q):
            cur=conn.cursor()
            try:
                cur.execute(q); rows=cur.fetchall()
                return pd.DataFrame(rows,columns=[x[0].lower() for x in cur.description])
            finally:cur.close()
        sales=read('SELECT * FROM MART.V_VENTES_DETAIL')
        stocks=read('SELECT * FROM MART.V_STOCKS_DETAIL')
        objectives=read('SELECT * FROM MART.V_OBJECTIFS_DETAIL')
        rejects=read('SELECT * FROM DQ.V_REJETS')
        dup=read('SELECT COUNT(*) AS N FROM DQ.V_DOUBLONS').iloc[0,0]
        for df in [sales,stocks,objectives]:
            for col in ['quantite','prix_unitaire','remise','cout_achat','ca_net','marge_estimee','stock_disponible','objectif_ca']:
                if col in df:df[col]=pd.to_numeric(df[col])
            for col in ['date_vente','date_stock','mois']:
                if col in df:df[col]=df[col].astype(str)
        return sales,stocks,objectives,rejects,int(dup)
try:sales,stocks,objectives,rejects,dup=fetch(source)
except Exception as e:
    st.error('Connexion ou lecture impossible. Vérifier .env, les droits et les scripts SQL.');st.exception(e);st.stop()
if st.sidebar.button('Actualiser les données'):st.cache_data.clear();st.rerun()
cities=st.sidebar.multiselect('Magasins',sorted(sales.ville.unique()),default=sorted(sales.ville.unique()))
months=st.sidebar.multiselect('Mois complets',sorted(sales.mois.unique()),default=sorted(sales.mois.unique()))
s=sales[sales.ville.isin(cities)&sales.mois.isin(months)]
o=objectives[objectives.ville.isin(cities)&objectives.mois.isin(months)]
ca=s.ca_net.sum();margin=s.marge_estimee.sum();orders=s.commande_id.nunique();target=o.objectif_ca.sum()
cols=st.columns(4)
cols[0].metric('Chiffre d’affaires net',f'{ca:,.2f} €')
cols[1].metric('Marge estimée',f'{margin:,.2f} €')
cols[2].metric('Panier moyen',f'{ca/orders:,.2f} €' if orders else '—')
cols[3].metric('Atteinte des objectifs',f'{100*ca/target:.1f} %' if target else '—')
a,b,c=st.tabs(['Ventes','Stocks au 30/09/2026','Qualité des données'])
with a:
    if s.empty:st.info('Aucune vente pour cette sélection.')
    else:
        st.subheader('Chiffre d’affaires mensuel')
        st.bar_chart(s.groupby('mois').ca_net.sum())
        st.subheader('Chiffre d’affaires par catégorie')
        st.bar_chart(s.groupby('categorie').ca_net.sum())
        st.dataframe(s,width='stretch',hide_index=True)
        st.download_button('Exporter les ventes filtrées',s.to_csv(index=False).encode('utf-8-sig'),'ventes_filtrees.csv','text/csv')
with b:
    st.caption('Stock fixe au 30 septembre ; indépendant du filtre mensuel. Couverture basée sur les ventes du 1er au 30 septembre, jours sans vente inclus. Alerte si couverture < 7 jours ; ce seuil est une règle métier, pas un modèle IA.')
    demand=sales[(sales.date_vente>='2026-09-01')&(sales.date_vente<='2026-09-30')].groupby(['magasin_id','produit_id']).quantite.sum().rename('ventes_30j').reset_index()
    stock=stocks[stocks.ville.isin(cities)].merge(demand,on=['magasin_id','produit_id'],how='left')
    stock['ventes_30j']=stock.ventes_30j.fillna(0)
    stock['couverture_jours']=stock.stock_disponible/(stock.ventes_30j/30).replace(0,float('nan'))
    stock['alerte']=stock.couverture_jours.lt(7)
    st.metric('Articles / magasins sous 7 jours',int(stock.alerte.sum()))
    st.dataframe(stock.sort_values('couverture_jours'),width='stretch',hide_index=True)
with c:
    st.write(f'{len(sales)} lignes valides · {dup} doublons écartés · {len(rejects)} lignes rejetées')
    st.dataframe(rejects,width='stretch',hide_index=True)
