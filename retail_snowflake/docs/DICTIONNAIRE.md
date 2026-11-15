# Données et règles métier

Tous les montants sont fictifs, en euros hors taxes. Dates au format YYYY-MM-DD.
CSV : UTF-8, virgule, guillemets doubles si nécessaire ; taux de remise décimal (0.10 = 10 %).

| Fichier | Grain / clé | Champs |
|---|---|---|
| ventes.csv | Ligne de commande / ligne_id | commande_id, date_vente, magasin_id, produit_id, quantite, prix_unitaire, remise |
| produits.csv | Produit / produit_id | libelle, categorie, cout_achat |
| magasins.csv | Magasin / magasin_id | ville, region |
| stocks.csv | date_stock + magasin_id + produit_id | stock_disponible |
| objectifs.csv | mois + magasin_id | objectif_ca |

Ventes : 6000 lignes valides, 3000 commandes ; dix copies identiques de lignes valides et six erreurs.
Rejets prioritaires : date invalide, produit inconnu, magasin inconnu, quantité invalide,
prix absent/invalide, remise hors intervalle [0,1]. Un motif par ligne.
Les référentiels produits/magasins et les stocks/objectifs sont fournis sans anomalies.
Ils doivent faire l'objet de contrôles supplémentaires pour de nouvelles sources réelles.

- CA net de ligne = quantité × prix unitaire × (1 − remise), arrondi au centime, moitié vers le haut.
- Marge estimée = CA net − quantité × coût d'achat constant, arrondi au centime.
- Panier moyen = CA net / nombre de commandes distinctes de la sélection.
- Atteinte = somme du CA / somme des objectifs mensuels des magasins sélectionnés.
- Couverture = stock au 30/09 / (quantité vendue du 01/09 au 30/09 / 30).
- Alerte si couverture < 7 jours ; si aucune vente en septembre, couverture non définie.

Le filtre des ventes porte sur des mois complets : aucune proratisation des objectifs n'est nécessaire.
Le panneau stocks reste daté au 30/09, indépendant du filtre mensuel des ventes.
Pas de TVA, devises multiples, retours, réceptions de stock, délais fournisseur ou prévision ML dans cette V1.
La dimension date ne contient que les dates de vente ; une V2 peut utiliser un calendrier complet.

Le coût d'achat n'est pas historisé : ne pas utiliser cette V1 comme comptabilité d'entreprise.
