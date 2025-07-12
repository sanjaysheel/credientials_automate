import os
import sys
from cryptography.fernet import Fernet

def decrypt_config():
    # 📂 Get directory where this .exe is running
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

    lock_path = os.path.join(base_dir, "config.lock")
    key_path = os.path.join(base_dir, "config.key")
    output_path = os.path.join(base_dir, "db_config.json")

    if not os.path.exists(lock_path):
        print("❌ config.lock not found.")
        return
    if not os.path.exists(key_path):
        print("❌ config.key not found.")
        return

    try:
        with open(key_path, "rb") as kf:
            key = kf.read()
        with open(lock_path, "rb") as lf:
            encrypted_data = lf.read()

        decrypted = Fernet(key).decrypt(encrypted_data)

        with open(output_path, "wb") as outf:
            outf.write(decrypted)

        print(f"✅ Decrypted to: {output_path}")
    except Exception as e:
        print("❌ Failed to decrypt:", e)

if __name__ == "__main__":
    decrypt_config()
