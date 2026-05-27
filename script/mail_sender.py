import smtplib
import shutil
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv("../.env")

MAIL = os.getenv("MAIL")
PASSWORT = os.getenv("MAIL_PASSWORD")

OUTPUT = Path("../output")

SENT = Path("../sent")
SENT.mkdir(
    exist_ok=True
)

empfaenger = {
    "stuttgart":
    "mert.gng9@gmail.com",

    "konstanz":
    "mert.gng9@gmail.com",

    "freiburg":
    "mert.gng9@gmail.com",

    "zurich":
    "mert.gng9@gmail.com"
}

xlsx_files = list(
    OUTPUT.glob("*.xlsx")
)

if len(xlsx_files) == 0:

    print(
        "Keine Reports gefunden"
    )

    quit()

for file in xlsx_files:

    if "unbekannt" in file.name.lower():

        print(
            "Ignoriert:",
            file.name
        )

        shutil.move(
            file,
            SENT / file.name
        )

        continue

    store = None

    for key in empfaenger:

        if key in file.stem.lower():

            store = key
            break

    if store is None:

        print(
            "Kein Empfänger:",
            file.name
        )

        continue

    ziel = empfaenger[
        store
    ]

    msg = EmailMessage()

    msg[
        "Subject"
    ] = (
        f"KPI Report {file.stem}"
    )

    msg[
        "From"
    ] = MAIL

    msg[
        "To"
    ] = ziel

    msg.set_content(
        "Automatischer KPI Report"
    )

    with open(
        file,
        "rb"
    ) as f:

        daten = f.read()

    msg.add_attachment(
        daten,
        maintype="application",
        subtype="octet-stream",
        filename=file.name
    )

    smtp = smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    )

    smtp.login(
        MAIL,
        PASSWORT
    )

    smtp.send_message(
        msg
    )

    smtp.quit()

    print(
        "Gesendet:",
        file.name,
        "→",
        ziel
    )

    shutil.move(
        file,
        SENT / file.name
    )

    print(
        "Archiviert:",
        file.name
    )
