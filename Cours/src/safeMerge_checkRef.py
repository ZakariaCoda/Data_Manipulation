import pandas as pd

def safe_merge(left, right, **kwargs):
    n_before = len(left)

    # Ajouter une colonne indiquant si la correspondance a été trouvée.
    result = left.merge(right, indicator=True, **kwargs)

    # Pour un left join, vérifier que le nombre de lignes est conservé.
    if kwargs.get('how', 'inner') == 'left':
        if len(result) != n_before:
            raise ValueError(
                f"La jointure a changé le nombre de lignes : "
                f"{n_before} → {len(result)}"
            )

    unmatched = result['_merge'] == 'left_only'

    if n_before > 0:
        unmatched_rate = unmatched.sum() / n_before
    else:
        unmatched_rate = 0

    print(f"Lignes de gauche sans correspondance : {unmatched_rate:.2%}")

    # Retirer la colonne technique avant de renvoyer le résultat.
    return result.drop(columns='_merge')


def check_referential_integrity(fact_table, dimensions):
    """dimensions : dict {nom_colonne_cle: dataframe_dimension}"""

    for cle, dimension in dimensions.items():
        orphelines = ~fact_table[cle].isin(dimension[cle])
        nb_orphelines = orphelines.sum()

    if nb_orphelines == 0:
        print("Integritè OK")
    else :
        print({len(nb_orphelines)}," ligne(s) orpheline(s) détectée(s) !")