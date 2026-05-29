import pandas as pd
import shutil
from pathlib import Path

INPUT = Path("../input")
OUTPUT = Path("../output")
ARCHIVE = Path("../archive")
REPORT_TEXTS = Path("../report_texts")

INPUT.mkdir(exist_ok=True)
OUTPUT.mkdir(exist_ok=True)
ARCHIVE.mkdir(exist_ok=True)
REPORT_TEXTS.mkdir(exist_ok=True)

csv_files = list(
    INPUT.glob("*.csv")
)

if len(csv_files) == 0:

    print(
        "Keine Dateien gefunden"
    )

    quit()

for file in csv_files:

    print(
        "Bearbeite:",
        file.name
    )

    df = pd.read_csv(
        file
    )

    dateiname = file.stem.lower()

    if "zurich" in dateiname:

        store = "zurich"

    elif "freiburg" in dateiname:

        store = "freiburg"

    elif "stuttgart" in dateiname:

        store = "stuttgart"

    elif "konstanz" in dateiname:

        store = "konstanz"

    else:

        store = "unbekannt"

    datum = (
        str(df["Datum"].iloc[0])
        .split(" ")[0]
        .replace("-", ".")
    )

    output_name = (
        OUTPUT /
        f"{store}_{datum}.xlsx"
    )

    report = df[
        [
            "Datum",
            "Mitarbeiter",
            "Artikel",
            "FinalPreis",
            "Identifikator"
        ]
    ]

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
    df["Mitarbeiter"] = (
    df["Mitarbeiter"]
    .str.replace(
        r"\(\d+\)",
        "",
        regex=True
    )
    .str.strip()
)

    produktmix_df = df.copy()

    produktmix_df["Mitarbeiter"] = (
        produktmix_df["Mitarbeiter"]
        .str.replace(
            r"\(\d+\)",
            "",
            regex=True
        )
        .str.strip()
    )

    produktmix_df = produktmix_df[
        produktmix_df["Mitarbeiter"] != "Order Anywhere"
    ]

    df = df[
        df["Typ"] == "SALE"
    ]

    burrata = produktmix_df[
    produktmix_df["Artikel"].isin(
        [
            "mit Burrata",
            "mit-Burrata+"
        ]
    )
]

    burrata_counts = (
        burrata
        .groupby("Mitarbeiter")["Mng"]
        .sum()
        .round(0)
        .astype(int)
    )
    wasser = produktmix_df[
        produktmix_df["Artikel"].str.contains(
            "morelli|aqua|acqua",
            case=False,
            na=False
        )
        &
        produktmix_df["Artikel"].str.contains(
            "0,75|0.75",
            case=False,
            na=False
        )
    ]

    wasser_counts = (
        wasser
        .groupby("Mitarbeiter")
        ["Mng"]
        .sum()
        .round(0)
        .astype(int)
    )
    bons = (
        df
        .groupby("Mitarbeiter")
        ["Identifikator"]
        .nunique()
    )

    txt_file = (
        REPORT_TEXTS /
        f"{store}_{datum}.txt"
    )

    mail_text = f"""
📊 {store.title()} – {datum}

🥇 Burrata
"""
    for mitarbeiter in bons.index:

        anzahl = (
            burrata_counts.get(
                mitarbeiter,
                0
            )
        )

        quote = round(
            (
                anzahl /
                bons[mitarbeiter]
            ) * 100,
            2
        )

        mail_text += (
            f"{mitarbeiter} – "
            f"{anzahl} "
            f"({quote}%)\n"
        )

    mail_text += "\n🥤 Wasserquote\n"

    for mitarbeiter in bons.index:

        wasser_anzahl = (
            wasser_counts.get(
                mitarbeiter,
                0
            )
        )

        wasser_quote = round(
            (
                wasser_anzahl /
                bons[mitarbeiter]
            ) * 100,
            2
        )

        mail_text += (
            f"{mitarbeiter} – "
            f"{wasser_anzahl} "
            f"({wasser_quote}%)\n"
        )

    with open(
        txt_file,
        "w"
    ) as f:

        f.write(
            mail_text
        )

    print(
        "Text erstellt:",
        txt_file
    )
