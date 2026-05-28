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

    df = df[
        ~df["Mitarbeiter"].str.contains(
            "Order Anywhere",
            case=False,
            na=False
        )
    ]

    df = df[
        df["Typ"] == "SALE"
    ]

    df = df[
        df["Mng"] > 0
    ]
    
    df["Mitarbeiter"] = (
    df["Mitarbeiter"]
    .str.replace(
        r"\(\d+\)",
        "",
        regex=True
    )
    .str.strip()
)

    burrata = df[
        df["Artikel"] == "mit-Burrata+"
    ]

    burrata_counts = (
        burrata
        .groupby("Mitarbeiter")
        .size()
    )

    wasser = df[
        df["Artikel"].str.contains(
            "morelli|aqua|acqua",
            case=False,
            na=False
        )
        &
        df["Artikel"].str.contains(
            "0,75|0.75",
            case=False,
            na=False
        )
    ]

    wasser_counts = (
        wasser
        .groupby("Mitarbeiter")
        .size()
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
            f"{wasser_quote}%\n"
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
