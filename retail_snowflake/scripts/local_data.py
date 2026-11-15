"""Référence locale des règles métier ; aucune connexion Snowflake."""
from pathlib import Path
from datetime import datetime
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]

def load_local():
    def read(name):return pd.read_csv(ROOT/'data'/f'{name}.csv',dtype=str,keep_default_na=False)
    products,stores,raw=read('produits'),read('magasins'),read('ventes')
    products['cout_achat']=pd.to_numeric(products['cout_achat'])
    clean=raw.copy()
    # Identique au SQL : un seul motif prioritaire par ligne.
    def reason(r):
        try:datetime.strptime(r.date_vente,'%Y-%m-%d')
        except ValueError:return 'DATE_INVALIDE'
        if r.produit_id not in set(products.produit_id):return 'PRODUIT_INCONNU'
        if r.magasin_id not in set(stores.magasin_id):return 'MAGASIN_INCONNU'
        for key,code,low,high in [('quantite','QUANTITE_INVALIDE',1,None),('prix_unitaire','PRIX_INVALIDE',0,None),('remise','REMISE_INVALIDE',0,1)]:
            try:v=float(r[key])
            except ValueError:return code
            if v<low or (high is not None and v>high) or (key=='quantite' and not v.is_integer()):return code
        return ''
    clean['motif']=clean.apply(reason,axis=1)
    rejects=clean[clean.motif!=''].copy()
    good=clean[clean.motif==''].copy()
    duplicates=good[good.duplicated('ligne_id')].copy()
    good=good.drop_duplicates('ligne_id').drop(columns='motif')
    for key in ['quantite','prix_unitaire','remise']:good[key]=pd.to_numeric(good[key])
    good=good.merge(products,on='produit_id',validate='many_to_one').merge(stores,on='magasin_id',validate='many_to_one')
    from decimal import Decimal, ROUND_HALF_UP
    def money(value):return float(value.quantize(Decimal('.01'),rounding=ROUND_HALF_UP))
    good['ca_net']=[money(Decimal(str(q))*Decimal(str(p))*(1-Decimal(str(r))))
                    for q,p,r in zip(good.quantite,good.prix_unitaire,good.remise)]
    good['marge_estimee']=[money(Decimal(str(ca))-Decimal(str(q))*Decimal(str(cost)))
                          for ca,q,cost in zip(good.ca_net,good.quantite,good.cout_achat)]
    good['mois']=good.date_vente.str[:7]+'-01'
    stocks=read('stocks').merge(products,on='produit_id').merge(stores,on='magasin_id')
    stocks['stock_disponible']=pd.to_numeric(stocks.stock_disponible)
    objectives=read('objectifs').merge(stores,on='magasin_id')
    objectives['objectif_ca']=pd.to_numeric(objectives.objectif_ca)
    return good,stocks,objectives,rejects,len(duplicates)
