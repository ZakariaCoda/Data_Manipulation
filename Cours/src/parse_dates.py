import pandas as pd

def parse_dates(series, min_success_rate=0.95):

    n_already_missing = int(series.isna().sum())

    dates = pd.to_datetime(series,
                             format='mixed', dayfirst=True, errors='coerce')

    n_total = len(series)
    n_missing_after = int(dates.isna().sum())
    n_failed = n_missing_after - n_already_missing

    # Calculer le taux uniquement sur les valeurs renseignées.
    n_to_parse = n_total - n_already_missing

    if n_to_parse > 0:
        success_rate = (n_to_parse - n_failed) / n_to_parse
    else:
        success_rate = 1.0

    report = {
        'n_total': n_total,
        'n_already_missing': n_already_missing,
        'n_failed': n_failed,
        'success_rate': success_rate,
        'min_date': dates.min(),
        'max_date': dates.max(),
    }

    if success_rate < min_success_rate:
        raise ValueError(
            f"Taux de réussite insuffisant : {success_rate:.1%}"
        )

    return dates, report