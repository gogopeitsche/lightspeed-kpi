import pandas as pd
from pathlib import Path

# -----------------------------
# CSV automatisch finden
# -----------------------------

input_folder = Path("../input")

csv_files = list(input_folder.glob("*.csv"))

if len(csv_files) == 0:
    raise Exception("Keine CSV im input Ordner gefunden")

csv_file = csv_files[0]

print("Datei gefunden:", csv_file)

# -----------------------------
# CSV laden
# -----------------------------

df = pd.read_csv(csv_file)

# -----------------------------
# Nur echte Verkäufe
# -----------------------------

df = df[
    (df["Typ"] == "SALE")
    &
    (df["Mng"] > 0)
]

# Online Orders entfernen
df = df[
    ~df["Mitarbeiter"]
    .str.contains(
        "Online",
        case=False,
        na=False
    )
]
# Mitarbeiternamen säubern
df["Mitarbeiter"] = (
    df["Mitarbeiter"]
    .str.replace(
        r"\(.*\)",
        "",
        regex=True
    )
    .str.strip()
)
# -----------------------------
# Umsatz pro Mitarbeiter
# -----------------------------

umsatz = (
    df.groupby(
        "Mitarbeiter"
    )["VorSteuern"]
    .sum()
    .reset_index()
)

report = umsatz.rename(
    columns={
        "VorSteuern": "Gesamtumsatz"
    }
)

# -----------------------------
# Produkte abfragen
# -----------------------------

produkte_input = input(
    "Produkte eingeben (mit Komma trennen): "
)

produkte = [
    p.strip()
    for p in produkte_input.split(",")
]

# -----------------------------
# Produktauswertung
# -----------------------------

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
            "Mng": "sum",
            "VorSteuern": "sum"
        })
        .reset_index()
    )

    produkt_sum = produkt_sum.rename(
        columns={
            "Mng": f"{produkt}_Stk",
            "VorSteuern": f"{produkt}_Umsatz"
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

# -----------------------------
# Sortieren
# -----------------------------

report = report.sort_values(
    "Gesamtumsatz",
    ascending=False
)

# -----------------------------
# Export
# -----------------------------

output_file = (
    "../output/report.xlsx"
)
# Zahlen runden
report = report.round(2)
report.to_excel(
    output_file,
    index=False
)

print("FERTIG")
print("Datei gespeichert:", output_file)
