import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import requests
import hashlib
import subprocess
import shutil
import time
import threading

def download_media_pack(base_url, target_directory, selected_media_pack, md5_checksums, status_var):
    console_name = os.path.splitext(selected_media_pack)[0].replace('-media', '')
    console_folder = os.path.join(target_directory, console_name)
    os.makedirs(console_folder, exist_ok=True)

    download_url = base_url + selected_media_pack
    file_path = os.path.join(target_directory, selected_media_pack)

    max_attempts = 4
    attempt = 0

    while attempt < max_attempts:
        attempt += 1
        status_var.set(f"Attempt {attempt} to download {selected_media_pack}...")

        response = requests.get(download_url, stream=True)
        with open(file_path, 'wb') as file:
            file.write(response.content)

        if response.status_code == 200:
            status_var.set(f"Download of {selected_media_pack} was successful.")
            break
        else:
            status_var.set(f"Download of {selected_media_pack} failed on attempt {attempt}.")
            if attempt < max_attempts:
                status_var.set("Retrying in 5 seconds...")
                time.sleep(5)
            else:
                status_var.set("Maximum download attempts reached. Download failed.")
                return None

    # Calculate the MD5 of the downloaded file
    actual_md5 = calculate_md5(file_path)

    # Check if MD5 matches the expected value
    expected_md5 = md5_checksums.get(selected_media_pack, "")
    if expected_md5 == actual_md5:
        status_var.set("Checksum verification successful.")
    else:
        status_var.set("Checksum verification failed. Exiting...")
        return None

    # Extraction process
    status_var.set("Extraction in progress...")

    # Extract the media pack using 7z
    if subprocess.run([r'C:\Program Files\7-Zip\7z.exe', 'x', f'-o{console_folder}', file_path]).returncode == 0:
        # Determine the target directory on the network share
        target_directory_network = r"\\RECALBOX\share\roms\{}".format(console_name)

        # Copy the extracted folder and its contents to the network share
        shutil.copytree(os.path.join(target_directory, console_folder), target_directory_network, dirs_exist_ok=True)

        status_var.set(f"{selected_media_pack} media pack copied to {target_directory_network}")
        status_var.set("Download and copy completed.")

        # CLEAN UP TEMP FILES
        status_var.set("Deleting temporary files and folders...")
        shutil.rmtree(os.path.join(target_directory, console_folder), ignore_errors=True)
        os.remove(file_path)

        # Clear status after a second or two
        time.sleep(2)
        status_var.set("")
    else:
        status_var.set("Extraction failed. Temporary files are not deleted.")

    return console_folder

def calculate_md5(file_path):
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            md5.update(chunk)
    return md5.hexdigest()

def open_file():
    browse_text.set("Downloading...")
    status_var.set("")  # Clear previous status
    download_thread_instance = threading.Thread(target=download_thread)
    download_thread_instance.start()

def download_thread():
    selected_media_pack = media_pack_combobox.get()

    if selected_media_pack:
        base_url = "https://forum.readycade.com/readycade_media/"
        target_directory = os.path.expandvars(r"%APPDATA%\readycade\mediapacks")
        console_folder = download_media_pack(base_url, target_directory, selected_media_pack, md5_checksums, status_var)
        if console_folder:
            browse_text.set("Download")
        else:
            browse_text.set("Download failed.")

root = tk.Tk()
root.title("Readycade")

# Logo
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')
logo = Image.open(logo_path)
logo = ImageTk.PhotoImage(logo)
logo_label = tk.Label(image=logo)
logo_label.image = logo
logo_label.grid(column=1, row=0)

# Instructions
Instructions = tk.Label(root, text="Select a media pack to download:", font="open-sans")
Instructions.grid(columnspan=3, column=0, row=1)

# Media pack selection dropdown
media_packs = [
    "64dd-media.7z",
    "amiga600-media.7z",
    "amiga1200-media.7z",
    "amstradcpc-media.7z",
    "apple2-media.7z",
    "apple2gs-media.7z",
    "arduboy-media.7z",
    "atari2600-media.7z",
    "atari5200-media.7z",
    "atari7800-media.7z",
    "atarist-media.7z",
    "atomiswave-media.7z",
    "bbcmicro-media.7z",
    "bk-media.7z",
    "c64-media.7z",
    "channelf-media.7z",
    "colecovision-media.7z",
    "daphne-media.7z",
    "dos-media.7z",
    "fds-media.7z",
    "gamegear-media.7z",
    "gba-media.7z",
    "gbc-media.7z",
    "gb-media.7z",
    "gbw-media.7z",
    "gx4000-media.7z",
    "intellivision-media.7z",
    "jaguar-media.7z",
    "lowresnx-media.7z",
    "lutro-media.7z",
    "mastersystem-media.7z",
    "megadrive-media.7z",
    "model3-media.7z",
    "msx1-media.7z",
    "msx2-media.7z",
    "msxturbor-media.7z",
    "multivision-media.7z",
    "n64-media.7z",
    "naomigd-media.7z",
    "naomi-media.7z",
    "neogeocd-media.7z",
    "neogeo-media.7z",
    "nes-media.7z",
    "ngpc-media.7z",
    "ngp-media.7z",
    "o2em-media.7z",
    "oricatmos-media.7z",
    "pcengine-media.7z",
    "pcenginecd-media.7z",
    "pcfx-media.7z",
    "pcv2-media.7z",
    "pokemini-media.7z",
    "ports-media.7z",
    "samcoupe-media.7z",
    "satellaview-media.7z",
    "scv-media.7z",
    "sega32x-media.7z",
    "sg1000-media.7z",
    "snes-media.7z",
    "solarus-media.7z",
    "spectravideo-media.7z",
    "sufami-media.7z",
    "supergrafx-media.7z",
    "supervision-media.7z",
    "thomson-media.7z",
    "tic80-media.7z",
    "trs80coco-media.7z",
    "uzebox-media.7z",
    "vectrex-media.7z",
    "vic20-media.7z",
    "videopacplus-media.7z",
    "virtualboy-media.7z",
    "wasm4-media.7z",
    "wswanc-media.7z",
    "wswan-media.7z",
    "x1-media.7z",
    "x68000-media.7z",
    "zx81-media.7z",
    "zxspectrum-media.7z"
]

md5_checksums = {
    "64dd-media.7z": "a2e36d62227447a9217b4a2b2c6bdef2",
    "amiga600-media.7z": "864c64b15e80ee992bf011894b5e5980",
    "amiga1200-media.7z": "35444479df16c4bad8476ce5e5fd2e76",
    "amstradcpc-media.7z": "211e304e1396e99c487f566ff5acd4ee"
}

media_pack_combobox = ttk.Combobox(root, values=media_packs)
media_pack_combobox.grid(column=1, row=2)
media_pack_combobox.set("Select a media pack")

# Browse Button
browse_text = tk.StringVar()
browse_btn = tk.Button(root, textvariable=browse_text, command=open_file, font="open-sans", bg="#ff6600", fg="white", height=2, width=15)
browse_text.set("Download")
browse_btn.grid(column=1, row=3)

# Status display
status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, font="open-sans")
status_label.grid(columnspan=3, column=0, row=4)

root.mainloop()
