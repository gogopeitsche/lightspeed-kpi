import resend
import shutil
from pathlib import Path
from dotenv import load_dotenv
import os
import base64

load_dotenv()

resend.api_key = os.getenv(
    "RESEND_API_KEY"
)

OUTPUT = Path("../output")

SENT = Path("../sent")
SENT.mkdir(
    exist_ok=True
)

empfaenger = {
    "stuttgart":
    "stuttgart@60stn.de",

    "konstanz":
    "konstanz@60stn.de",

    "freiburg":
    "freiburg@60stn.de",

    "zurich":
    "zuerich@60stn.ch",
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

    with open(
        file,
        "rb"
    ) as f:

        anhang = base64.b64encode(
            f.read()
        ).decode("utf-8")
    resend.Emails.send({

        "from":
        "reports@reports60stn.org",

        "to":
        ziel,

        "subject":
        f"KPI Report {file.stem}",

        "text":
        "Automatischer KPI Report",

        "attachments": [
            {
                "filename":
                file.name,

                "content":
                anhang
            }
        ]
    })

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
