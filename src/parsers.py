from pathlib import Path

import pandas as pd


def parse_banque_populaire_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    df = pd.read_csv(path, sep=";")

    # remove unnecessary categories for budgeting
    df.drop(
        columns=[
            "Libelle simplifie",
            "Libelle operation",
            "Pointage operation",
            "Date de valeur",
            "Reference",
            "Informations complementaires",
            "Type operation",
            "Date de comptabilisation",
        ],
        inplace=True,
    )

    # Combine Credit and Debit into a single column to get rid of NaNs
    df.fillna({"Debit": df["Credit"]}, inplace=True)
    del df["Credit"]

    df.rename(
        columns={
            "Categorie": "Category",
            "Sous categorie": "Subcategory",
            "Date operation": "Date",
            "Debit": "Operation",
        },
        inplace=True,
    )

    # Series are stored as str from the csv
    df["Operation"] = df["Operation"].astype("float")
    df["Date"] = pd.to_datetime(df["Date"], format=r"%d/%m/%Y")

    return df
