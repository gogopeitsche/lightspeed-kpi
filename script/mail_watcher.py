import time
import subprocess

print("Mail Watcher gestartet...")

while True:

    print(
        "Prüfe Mails..."
    )

    subprocess.run(
        [
            "python",
            "mail_reader.py"
        ]
    )

    time.sleep(300)
