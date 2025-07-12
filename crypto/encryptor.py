from cryptography.fernet import Fernet
import os
import subprocess

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD_DIR = os.path.join(BASE_DIR, "build")

def ensure_build_dir():
    os.makedirs(BUILD_DIR, exist_ok=True)
    return BUILD_DIR

def encrypt_json(input_file, output_file, key_file):
    key = Fernet.generate_key()

    with open(key_file, "wb") as kf:
        kf.write(key)

    with open(input_file, "rb") as f:
        data = f.read()

    encrypted_data = Fernet(key).encrypt(data)

    with open(output_file, "wb") as ef:
        ef.write(encrypted_data)

    print(f"✅ Encrypted: {output_file}")
    print(f"🗝️  Key: {key_file}")

def build_unlock_exe():
    script_path = os.path.join(os.path.dirname(__file__), "decryptor.py")
    dist_dir = ensure_build_dir()

    subprocess.run([
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name", "UnlockConfig",
        "--distpath", dist_dir,
        script_path
    ], check=True)

    return os.path.join(dist_dir, "UnlockConfig.exe")


# from cryptography.fernet import Fernet
# import os
# import sys

# def get_desktop_path():
#     return os.path.join(os.path.expanduser("~"), "Desktop")

# def encrypt_json(input_file, output_file, key_file):
#     """Encrypt a JSON file using Fernet symmetric encryption."""
#     if not os.path.exists(input_file):
#         print(f"❌ Input file not found: {input_file}")
#         sys.exit(1)

#     # Create directory for encrypted and key files if not exists
#     os.makedirs(os.path.dirname(output_file), exist_ok=True)
#     os.makedirs(os.path.dirname(key_file), exist_ok=True)

#     # Generate encryption key
#     key = Fernet.generate_key()

#     # Save key to file
#     with open(key_file, "wb") as kf:
#         kf.write(key)

#     # Read original JSON file
#     with open(input_file, "rb") as f:
#         data = f.read()

#     # Encrypt data
#     encrypted_data = Fernet(key).encrypt(data)

#     # Save encrypted file
#     with open(output_file, "wb") as ef:
#         ef.write(encrypted_data)

#     print(f"\n✅ Encrypted successfully!")
#     print(f"🔐 Encrypted File : {output_file}")
#     print(f"🗝️  Key File       : {key_file}")
