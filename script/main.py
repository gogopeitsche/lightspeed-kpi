import time
import subprocess
from pathlib import Path
from datetime import datetime

LOG = Path("../logs")
LOG.mkdir(exist_ok=True)

log_file = LOG / "system.log"
error_file = LOG / "errors.log"

print(
    "Logs:",
    log_file
)

print(
    "Fehler:",
    error_file
)

def log(text):

    zeit = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    eintrag = (
        f"[{zeit}] {text}\n"
    )

    print(text)

    with open(
        log_file,
        "a"
    ) as f:

        f.write(
            eintrag
        )

print(
    "Lightspeed KPI gestartet"
)

while True:

    try:

        log(
            "Mail Check"
        )

        subprocess.run(
            [
                "python3",
                "./mail_reader.py"
            ],
            check=True
        )

        log(
            "Report Verarbeitung"
        )

        subprocess.run(
            [
                "python3",
                "./auto_worker.py"
            ],
            check=True
        )
        log(
            "Sende Reports"
        )

        log(
            "Warte 5 Minuten"
        )

        time.sleep(
            300
        )

    except Exception as e:

        with open(
            error_file,
            "a"
        ) as f:

            f.write(
                f"{datetime.now()} {e}\n"
            )

        print(
            "FEHLER:",
            e
        )
