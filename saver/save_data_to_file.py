#сохраняет в формате для файла

import csv
import os
from typing import List, Dict, Optional

def save_data_to_file_api(data: List[Dict], file_path: str, overwrite: bool = False) -> str:
    if not data:
        raise ValueError("No data to save")

    if not file_path.endswith(".csv"):
        file_path = file_path + ".csv"

    if os.path.exists(file_path) and not overwrite:
        raise FileExistsError(f"File already exists: {file_path}")

    fieldnames = list(data[0].keys())
    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    return file_path


# --- Старая CLI-функция (чтобы main.py не ломать) ---
def save_data_to_file(data: list):
    if not data:
        print("Not data!")
        return

    print("\nSave data")
    file_name = input("Enter name of the file: ").strip()
    while not file_name:
        file_name = input("File name cannot be empty. Enter name of the file: ").strip()

    filename = f"{file_name}.csv"
    overwrite = False
    if os.path.exists(filename):
        ans = input("File already exists. Overwrite? (y/n): ").strip().lower()
        if ans != "y":
            print("Save cancelled")
            return
        overwrite = True

    try:
        path = save_data_to_file_api(data, filename, overwrite=overwrite)
        print(f"Data save to file {path}")
    except Exception as e:
        print(f"Save error: {e}")