import os
from pathlib import Path

import requests
import resend
from dotenv import load_dotenv

load_dotenv()

# Resend API Key
resend.api_key = os.getenv("RESEND_API_KEY")

INPUT = Path("../input")

INPUT.mkdir(
    exist_ok=True
)

processed_file = "../processed_mails.txt"

processed_ids = set()

if os.path.exists(
    processed_file
):

    with open(
        processed_file,
        "r"
    ) as f:

        processed_ids = set(
            line.strip()
            for line in f
        )

try:

    print(os.getenv("RESEND_API_KEY")[:15])
    response = resend.EmailsReceiving.list()

except Exception as e:

    print(
        f"Fehler beim Abrufen der Mails: {e}"
    )

    raise

mails = response.get(
    "data",
    []
)

print(
    "Neue Mails gefunden:",
    len(mails)
)

for mail in mails:

    mail_id = mail.get("id")

    if not mail_id:
        continue

    if mail_id in processed_ids:

        print(
            "Bereits verarbeitet:",
            mail_id
        )

        continue

    try:

        full_mail = resend.EmailsReceiving.get(
            mail_id
        )

    except Exception as e:

        print(
            f"Fehler beim Abrufen von Mail {mail_id}: {e}"
        )

        continue

    subject = full_mail.get(
        "subject",
        ""
    )

    print(
        "Betreff:",
        subject
    )

    attachments = full_mail.get(
        "attachments",
        []
    )
    print("Attachments:")
    print(attachments)

    if not attachments:

        print(
            "Keine Anhänge gefunden."
        )

        with open(
            processed_file,
            "a"
        ) as f:

            f.write(
                mail_id + "\n"
            )

        continue

    attachment = resend.EmailsReceiving.Attachments.get(
        email_id=mail_id,
        attachment_id=attachments[0]["id"]
    )

    download_url = attachment["download_url"]

    try:

        r = requests.get(
            download_url,
            timeout=60
        )

        r.raise_for_status()

    except Exception as e:

        print(
            f"Fehler beim Download: {e}"
        )

        continue

    for attachment in attachments:

        filename = attachment.get(
            "filename"
        )

        if not filename:
            continue

        if not filename.lower().endswith(
            ".csv"
        ):
            continue

        file_path = (
            INPUT /
            filename
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                r.content
            )

        print(
            "Gespeichert:",
            filename
        )

    with open(
        processed_file,
        "a"
    ) as f:

        f.write(
            mail_id + "\n"
        )

print(
    "Fertig."
)
