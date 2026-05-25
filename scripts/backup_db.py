# scripts/backup_db.py
# ПР7: Богдан — резервне копіювання бази даних з шифруванням
# Скрипт створює копію SQLite-бази, шифрує її через Fernet
# і зберігає результат у папку data/backups у форматі .enc


import os
import sys
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import Fernet
from app.crypto.key_manager import get_encryption_key


def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_path = "data/dean_office.db"
    backup_dir = "data/backups"

    os.makedirs(backup_dir, exist_ok=True)

    backup_path = f"{backup_dir}/dekanat_backup_{timestamp}.db"
    shutil.copy2(db_path, backup_path)

    f = Fernet(get_encryption_key())

    with open(backup_path, "rb") as file:
        data = file.read()

    encrypted_data = f.encrypt(data)
    encrypted_path = f"{backup_path}.enc"

    with open(encrypted_path, "wb") as file:
        file.write(encrypted_data)

    os.remove(backup_path)

    print(f"Зашифрована копія: {encrypted_path}")
    return encrypted_path


if __name__ == "__main__":
    create_backup()
