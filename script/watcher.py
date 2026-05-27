import time
from pathlib import Path
import subprocess

INPUT = Path("../input")

print("Watcher gestartet...")

bearbeitet = set()

while True:

    csv_files = list(
        INPUT.glob("*.csv")
    )

    for file in csv_files:

        if file.name not in bearbeitet:

            print(
                "Neue Datei:",
                file.name
            )

            subprocess.run(
                [
                    "python",
                    "auto_worker.py"
                ]
            )

            bearbeitet.add(
                file.name
            )

    time.sleep(10)
