import pandas as pd
def profile_dataframe(df, name='jeu de données', max_cardinality=25):
    """Affiche un rapport d'exploration standard.

    Doit produire, dans cet ordre :
      1. le nom, les dimensions et l'empreinte mémoire ;
      2. le nombre de lignes strictement dupliquées ;
      3. un tableau par colonne : type, nombre de valeurs manquantes, taux en %,
         nombre de valeurs distinctes ;
      4. les statistiques descriptives des colonnes numériques ;
      5. pour chaque colonne texte de cardinalité inférieure à max_cardinality,
         la répartition des modalités.

    Ne renvoie rien : la fonction affiche.
    """
    # TODO
    print("Nom : ",name,"\n")
    print("Dimensions : ",df.shape,"\n")
    print("Taille : ",df.size,"\n")
    print("Lignes strictement dupliquées :", df.duplicated().sum())

    summary = pd.DataFrame({
        'type': df.dtypes,
        'nb_valeurs_manquantes': df.isna().sum(),
        'taux_en_%': (df.isna().mean() * 100).round(2),
        'nb_valeurs_distinctes': df.nunique(dropna=True),
    })
    print('\n--- synthèse par colonne ---')
    print(summary)


    print("\n--- Statistique des colonnes numeriques ---")
    #stat_num = pd.DataFrame({
    #   'moyenne': df.select_dtypes(include=['number']).mean(),
    #    'min': df.select_dtypes(include=['number']).min(),
    #    'max':  df.select_dtypes(include=['number']).max(),
    #    'ecart_type': sales.select_dtypes(include=['number']).std(),
    #    'mediane' :
    #}
    print(df.select_dtypes(include=['number']).describe())


    print('\n--- cardinalité des colonnes texte ---')
    for column in df.select_dtypes(include='str').columns:
        print(" ------------- \n")
        if df[column].nunique() < max_cardinality:
            print(f'  {column:<18} {df[column].nunique()} modalités')
            print(df[column].value_counts())
