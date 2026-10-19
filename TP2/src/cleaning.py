import numpy as np
import pandas as pd
from pathlib import Path

def normalize_text(series):
    """Casse, espaces et accents : trois sources de faux niveaux."""
    text = series.astype(str).str.strip().str.lower()
    text = text.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8')
    return text.str.replace(r'\s+', ' ', regex=True)

def parse_price(series):
    """Convertit une colonne de prix mixte (nombre ou texte '123,45 EUR') en float."""
    text = series.astype(str).str.replace(' EUR', '', regex=False)
    return pd.to_numeric(text.str.replace(',', '.', regex=False).str.strip(),
                         errors='coerce')


def clean_sales(df, drop_negative_quantities=True, max_quantity=None, verbose=True):
    """Nettoie les ventes et renvoie le DataFrame nettoyé et son journal."""
    df = df.copy()
    log = {'lignes_initiales': len(df)}

    # 1. Convertir les prix avec la fonction déjà définie au début.
    log['prix_manquants_avant'] = int(df['prix_unitaire'].isna().sum())
    df['prix_unitaire'] = parse_price(df['prix_unitaire'])
    log['prix_manquants_apres'] = int(df['prix_unitaire'].isna().sum())

    # 2. Normaliser uniquement les colonnes descriptives.
    for column in ['canal', 'statut', 'ville_livraison']:
        normalized = normalize_text(df[column])
        log[column + '_modifications'] = int((df[column] != normalized).sum())
        df[column] = normalized

    # 3. Supprimer les doublons stricts.
    log['doublons_supprimes'] = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    # 4. Convertir les cinq formats de date présents dans le fichier.
    original_dates = df['date_commande'].copy()
    df['date_commande'] = pd.to_datetime(
        original_dates, format='%Y-%m-%d', errors='coerce'
    )
    for date_format in ['%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d %H:%M', '%d %b %Y']:
        parsed_dates = pd.to_datetime(
            original_dates, format=date_format, errors='coerce'
        )
        df['date_commande'] = df['date_commande'].fillna(parsed_dates)

    missing_date = df['date_commande'].isna()
    log['lignes_sans_date_supprimees'] = int(missing_date.sum())
    df = df.loc[~missing_date].copy()

    # 5. Une remise absente est supposée correspondre à aucune remise.
    log['remises_remplacees_par_zero'] = int(df['remise_pct'].isna().sum())
    df['remise_pct'] = df['remise_pct'].fillna(0)

    # 6. Supprimer les quantités négatives si demandé.
    log['quantites_negatives_supprimees'] = 0
    if drop_negative_quantities:
        negative = df['quantite'] < 0
        log['quantites_negatives_supprimees'] = int(negative.sum())
        df = df.loc[~negative].copy()

    # 7. Appliquer un plafond fixe uniquement s'il est renseigné.
    log['quantites_plafonnees'] = 0
    if max_quantity is not None:
        too_high = df['quantite'] > max_quantity
        log['quantites_plafonnees'] = int(too_high.sum())
        df.loc[too_high, 'quantite'] = max_quantity

    # 8. Calculer le montant après remise.
    df['montant'] = (
        df['quantite'] * df['prix_unitaire']
        * (1 - df['remise_pct'] / 100)
    )
    log['montants_calcules'] = int(df['montant'].notna().sum())

    # Les transformations peuvent rendre de nouvelles lignes identiques.
    log['doublons_apres_nettoyage'] = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()
    log['lignes_finales'] = len(df)

    if verbose:
        for key, value in log.items():
            print(f'  {key:<36} {value}')

    return df, log

ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
RAW_DIR = ROOT / 'data' / 'raw'
PROCESSED_DIR = ROOT / 'data' / 'processed'
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
clean_sales_df, cleaning_log = clean_sales(pd.read_csv(RAW_DIR / 'ventes_brutes.csv'))