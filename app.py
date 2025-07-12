import os
import sys
import zipfile
import subprocess
import threading
import time
from flask import Flask, request, render_template, jsonify, send_from_directory, send_file

# Ensure paths work when running as a script or .exe
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "build")
os.makedirs(BUILD_DIR, exist_ok=True)
sys.path.insert(0, BASE_DIR)

from manual.manual_config import process_manual_connections
from Cloud.aws.aws_config import process_aws_credentials
from crypto.encryptor import encrypt_json

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

@app.route("/", methods=["GET"])
def index():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    method = request.form.get("method", "manual")

    if method == "manual":
        connections = []
        for key in request.form:
            if key.startswith("connections["):
                index = int(key.split("[")[1].split("]")[0])
                field = key.split("[")[2].split("]")[0]
                while len(connections) <= index:
                    connections.append({})
                connections[index][field] = request.form[key]
        output = process_manual_connections(connections, base_dir=BUILD_DIR)

    elif method == "aws":
        profile = request.form.get("aws_profile")
        region = request.form.get("aws_region")
        mfa_arn = request.form.get("aws_mfa_arn")
        token_code = request.form.get("aws_mfa_token")
        output = process_aws_credentials(profile, region, mfa_arn, token_code)

    else:
        return jsonify({"status": "error", "message": "Unknown method"}), 400

    # Encrypt JSON
    json_path = output["path"]
    enc_path = os.path.join(BUILD_DIR, "config.lock")
    key_path = os.path.join(BUILD_DIR, "config.key")
    encrypt_json(json_path, enc_path, key_path)

    # Generate exe
    exe_script_path = os.path.join(BASE_DIR, "crypto", "decryptor.py")  # should decrypt `config.lock`
    command = f'pyinstaller --onefile --noconsole --distpath "{BUILD_DIR}" --workpath "{os.path.join(BUILD_DIR, "temp")}" --specpath "{BUILD_DIR}" "{exe_script_path}"'
    subprocess.run(command, shell=True)

    return jsonify({
        "status": "success",
        "message": "Encrypted and exe created.",
        "download_url": "/download-exe"
    })


@app.route("/download-exe")
def download_exe():
    conn_name = "Inventory_DB"  # You can also get this from session or request if dynamic
    build_dir = os.path.join(BASE_DIR, "build")

    # Normalize the name for filesystem safety
    safe_name = conn_name.strip().replace(" ", "_").lower()

    # Rename the .exe file
    original_exe = os.path.join(build_dir, "decryptor.exe")
    renamed_exe = os.path.join(build_dir, f"decryptor_{safe_name}.exe")
    if os.path.exists(original_exe):
        if os.path.exists(renamed_exe):
            os.remove(renamed_exe)
        os.rename(original_exe, renamed_exe)


    # Define ZIP file path
    zip_filename = f"db_config_{safe_name}.zip"
    zip_path = os.path.join(build_dir, zip_filename)

    # Files to include
    files_to_zip = [
        os.path.join(build_dir, "config.lock"),
        os.path.join(build_dir, "config.key"),
        renamed_exe
    ]

    # Create the ZIP archive
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in files_to_zip:
            zipf.write(file, arcname=os.path.basename(file))

    # Schedule cleanup in 2 minutes
    def delayed_cleanup(paths):
        time.sleep(15)
        for path in paths:
            try:
                if os.path.exists(path):
                    print("PATH+======================", path)
                    os.remove(path)
                    print(f"🧹 Deleted: {path}")
            except Exception as e:
                print(f"⚠️ Error deleting {path}: {e}")

    cleanup_paths = files_to_zip + [zip_path]
    threading.Thread(target=delayed_cleanup, args=(cleanup_paths,), daemon=True).start()

    # Serve the ZIP file
    return send_file(zip_path, as_attachment=True, download_name=zip_filename)



if __name__ == "__main__":
    app.run(debug=True)
