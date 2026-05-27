import pandas as pd
from pathlib import Path
import shutil

INPUT = Path("../input")
OUTPUT = Path("../output")
ARCHIVE = Path("../archive")

produkte = [
    "mit-Burrata+",
    "Acqua Morelli Sparkling 0.75"
]

csv_files = list(INPUT.glob("*.csv"))

if len(csv_files) == 0:
    print("Keine Dateien gefunden")
    quit()

for file in csv_files:

    if file.name == "transaktionen.csv":

        print(
            "Archiviert:",
            file.name
        )

        shutil.move(
            file,
            ARCHIVE / file.name
        )

        continue

    print(
        "Bearbeite:",
        file.name
    )

    name = file.stem.lower()

    store = "unbekannt"    

    if "stuttgart" in name:
        store = "stuttgart"

    elif "konstanz" in name:
        store = "konstanz"

    elif "freiburg" in name:
        store = "freiburg"

    elif "zurich" in name:
        store = "zurich"

    df = pd.read_csv(file)

    df = df[
        (df["Typ"] == "SALE")
        &
        (df["Mng"] > 0)
    ]

    df = df[
        ~df["Mitarbeiter"]
        .str.contains(
            "Online",
            case=False,
            na=False
        )
    ]

    df["Mitarbeiter"] = (
        df["Mitarbeiter"]
        .str.replace(
            r"\(.*\)",
            "",
            regex=True
        )
        .str.strip()
    )

    umsatz = (
        df.groupby(
            "Mitarbeiter"
        )["VorSteuern"]
        .sum()
        .reset_index()
    )

    report = umsatz.rename(
        columns={
            "VorSteuern":
            "Gesamtumsatz"
        }
    )

    for produkt in produkte:

        produkt_df = df[
            df["Artikel"]
            ==
            produkt
        ]

        produkt_sum = (
            produkt_df.groupby(
                "Mitarbeiter"
            )
            .agg({
                "Mng":"sum",
                "VorSteuern":"sum"
            })
            .reset_index()
        )

        produkt_sum = produkt_sum.rename(
            columns={
                "Mng":
                f"{produkt}_Stk",

                "VorSteuern":
                f"{produkt}_Umsatz"
            }
        )

        report = report.merge(
            produkt_sum,
            on="Mitarbeiter",
            how="left"
        )

        report = report.fillna(0)

        report[
            f"{produkt}_%"
        ] = (
            report[
                f"{produkt}_Umsatz"
            ]
            /
            report[
                "Gesamtumsatz"
            ]
        ) * 100

    report = report.round(2)

    teile = file.stem.split("_")

    if len(teile) >= 2:
        datum = teile[-2]

    else:
        datum = "ohne_datum"

    output_name = (
        OUTPUT /
        f"{store}_{datum}.xlsx"
    )

    report.to_excel(
        output_name,
        index=False
    )

    shutil.move(
        file,
        ARCHIVE / file.name
    )

    print(
        "Fertig:",
        output_name
    )
