from pathlib import Path

target_dir = Path("Submitted_file")

for d in target_dir.iterdir(): 
    if d.is_dir():
        print(f"folder name is : {d.name}")