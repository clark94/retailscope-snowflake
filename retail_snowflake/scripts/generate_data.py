"""Données entièrement fictives, reproductibles, sans service externe."""
from pathlib import Path
import csv, random
from datetime import date, timedelta

ROOT = Path(__file__).resolve().parents[1]
def generate():
    rng = random.Random(94)
    dest = ROOT / 'data'
    dest.mkdir(exist_ok=True)
    def write(name, fields, rows):
        with (dest / name).open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
    products = [dict(produit_id=f'P{i:03}', libelle=f'Article {i:02}',
                     categorie=['Bureau','Informatique','Maison'][i % 3],
                     cout_achat=round(5+i*2.15, 2)) for i in range(1,31)]
    stores = [dict(magasin_id=f'M{i:02}',ville=city,region=region) for i,(city,region) in enumerate([
        ('Lyon','Auvergne-Rhône-Alpes'),('Écully','Auvergne-Rhône-Alpes'),
        ('Montpellier','Occitanie'),('Nantes','Pays de la Loire'),
        ('Rennes','Bretagne'),('Lille','Hauts-de-France')],1)]
    sales=[]
    for i in range(1,6001):
        p=rng.choice(products)
        sales.append(dict(ligne_id=f'L{i:06}',commande_id=f'C{(i+1)//2:05}',
            date_vente=(date(2026,4,1)+timedelta(days=rng.randrange(183))).isoformat(),
            magasin_id=stores[((i+1)//2)%6]['magasin_id'],produit_id=p['produit_id'],
            quantite=rng.randint(1,8),prix_unitaire=round(p['cout_achat']*rng.uniform(1.3,1.8),2),
            remise=rng.choice([0,0,0,0.05,0.1,0.15])))
    # Deux lignes d'une même commande partagent magasin ET date.
    for i in range(0,6000,2): sales[i+1]['date_vente']=sales[i]['date_vente']
    raw=sales+[dict(sales[i]) for i in range(10)]
    changes=[('date_vente','2026-02-30'),('produit_id','INCONNU'),
             ('magasin_id','INCONNU'),('quantite','-2'),('prix_unitaire',''),('remise','1.4')]
    for i,(field,value) in enumerate(changes):
        row=dict(sales[100+i]);row['ligne_id']=f'ERR{i+1}';row[field]=value;raw.append(row)
    write('ventes.csv',list(sales[0]),raw)
    write('produits.csv',list(products[0]),products)
    write('magasins.csv',list(stores[0]),stores)
    stocks=[dict(date_stock='2026-09-30',magasin_id=s['magasin_id'],produit_id=p['produit_id'],
                 stock_disponible=rng.randint(0,120)) for s in stores for p in products]
    write('stocks.csv',list(stocks[0]),stocks)
    objectives=[dict(mois=f'2026-{m:02}-01',magasin_id=s['magasin_id'],objectif_ca=15000+(m-4)*500)
                for m in range(4,10) for s in stores]
    write('objectifs.csv',list(objectives[0]),objectives)
    print('Génération : 6016 lignes brutes, dont 6000 ventes valides, 10 doublons et 6 rejets.')
if __name__=='__main__':generate()
