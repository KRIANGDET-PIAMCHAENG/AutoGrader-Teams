from pathlib import Path

target_dir = Path("Submitted_file")

if not target_dir.exists():
    raise FileNotFoundError(f"folder {target_dir} not found")

for student in target_dir.iterdir():

    if student.is_dir():
        for hw in student.iterdir():

            if hw.is_dir() and hw.name == "HW 4":
                version_folders = []

                for v in hw.iterdir():

                    if v.is_dir():
                        version_folders.append(v)

                if version_folders:

                    version_folders = sorted(version_folders)

                    latest_version_path = version_folders[-1]

                    print(
                        f"student: {student.name} -> last version: {latest_version_path.name}"
                    )
