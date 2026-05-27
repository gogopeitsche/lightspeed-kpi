import imaplib
import email
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

MAIL = os.getenv("MAIL")
PASSWORT = os.getenv("MAIL_PASSWORD")

INPUT = Path("../input")

imap = imaplib.IMAP4_SSL(
    "imap.gmail.com"
)

imap.login(
    MAIL,
    PASSWORT
)

imap.select("INBOX")

status, messages = imap.search(
    None,
    '(UNSEEN SUBJECT "Lightspeed")'
)

mail_ids = messages[0].split()

print(
    "Neue Mails:",
    len(mail_ids)
)

for mail_id in mail_ids:

    _, msg_data = imap.fetch(
        mail_id,
        "(RFC822)"
    )

    for response in msg_data:

        if not isinstance(
            response,
            tuple
        ):
            continue

        msg = email.message_from_bytes(
            response[1]
        )

        subject = msg.get(
            "Subject",
            ""
        )

        print(
            "Betreff:",
            subject
        )

        for part in msg.walk():

            filename = part.get_filename()

            if not filename:
                continue

            if not filename.endswith(
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
                    part.get_payload(
                        decode=True
                    )
                )

            print(
                "Gespeichert:",
                filename
            )

            imap.store(
            mail_id,
            "+FLAGS",
            "\\Seen"
            )

imap.logout()
