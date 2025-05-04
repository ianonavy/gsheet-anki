import os
import glob
import subprocess

def import_to_anki(apkg_folder):
    # Get the latest .apkg file for each deck
    apkg_files = glob.glob(os.path.join(apkg_folder, "*.apkg"))
    if not apkg_files:
        print("No .apkg files found in the specified folder.")
        return

    # Sort files by modification time (newest first)
    apkg_files.sort(key=os.path.getmtime, reverse=True)

    for apkg_file in apkg_files:
        # Extract deck name by removing the timestamp and extension
        deck_name = "_".join(os.path.basename(apkg_file).split("_")[:-2])
        # Check if this is the latest file for the deck
        if apkg_file != max(
            (f for f in apkg_files if deck_name in f),
            key=os.path.getmtime
        ):
            continue
        print(f"Importing {apkg_file} into Anki...")
        try:
            # Use subprocess to call Anki's import functionality
            subprocess.run(["open", "-a", "Anki", apkg_file], check=True)
            print(f"Successfully imported {apkg_file}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to import {apkg_file}: {e}")

if __name__ == "__main__":
    # Replace with the folder containing your .apkg files
    apkg_folder = "."
    import_to_anki(apkg_folder)
