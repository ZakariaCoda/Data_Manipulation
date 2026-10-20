import pandas as pd


def scale_minmax(series):
    """Ramener les valeurs observées entre 0 et 1."""
    spread = series.max() - series.min()
    return (series - series.min()) / spread if spread != 0 else series * 0


def scale_zscore(series):
    """Centrer et réduire avec l'écart type pandas (ddof=1)."""
    std = series.std()
    return (series - series.mean()) / std if std != 0 else series * 0


def group_rare_categories(series, min_frequency=0.01, other_label='autre'):
    frequencies = series.value_counts(normalize=True)
    rare_labels = frequencies[frequencies < min_frequency].index
    return series.where(~series.isin(rare_labels), other_label)


def prepare_features(df, products):
    result = df.copy()
    result = result.merge(products, on='id_produit', how='left', validate='many_to_one')

    # Quelle valeur de vente reste après application de la remise ?
    result['montant_apres_remise'] = (
        result['quantite'] * result['prix_unitaire']
        * (1 - result['remise_pct'] / 100)
    )
    # Quel est le montant moyen des commandes de ce client dans ce jeu ?
    # Une commande peut avoir plusieurs lignes : sommer ses lignes d'abord.
    orders = result.groupby(['id_client', 'id_commande'])['montant_apres_remise'].sum(min_count=1)
    customer_means = orders.groupby('id_client').mean()
    result['panier_moyen_client'] = result['id_client'].map(customer_means)
    # La vente a-t-elle été annulée ou retournée ?
    result['commande_non_aboutie'] = result['statut'].isin(['annule', 'retourne']).astype(int)
    # Le prix est-il supérieur ou inférieur au prix médian de sa catégorie ?
    category_median = result.groupby('categorie')['prix_unitaire'].transform('median')
    result['ecart_prix_median_categorie'] = result['prix_unitaire'] - category_median

    result['marge_unitaire'] = result['prix_unitaire'] - result['cout_achat']
    nonzero_price = result['prix_unitaire'].where(result['prix_unitaire'] != 0)
    result['taux_marge'] = (result['marge_unitaire'] / nonzero_price).round(4)

    result['sous_categorie_regroupee'] = group_rare_categories(
        result['sous_categorie'], min_frequency=0.02
    )
    encoded = pd.get_dummies(
        result[['canal', 'statut', 'categorie', 'sous_categorie_regroupee']],
        prefix_sep='=', dtype=int,
    )
    result = pd.concat([result, encoded], axis=1)
    result['montant_zscore'] = scale_zscore(result['montant'])
    return result
