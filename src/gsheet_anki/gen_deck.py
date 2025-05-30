"""
Creates Anki decks
"""

import csv
import gspread
import hashlib
import json
import os
from io import BytesIO
from datetime import datetime

import genanki
from oauth2client.service_account import ServiceAccountCredentials


# Globally unique model ID
MODEL_ID = 1607392321
# Google Sheets API required scopes
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]
# Read from env var for local scripts
DEFAULT_SPREADSHEET_URL = os.environ.get("SPREADSHEET_URL", "")


def get_spreadsheet(spreadsheet_url=DEFAULT_SPREADSHEET_URL):
    """
    Returns a gspread client spreadsheet object given the environment.
    :param spreadsheet_url: The URL of the Google Sheet.
    :return: gspread client spreadsheet object
    """
    service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
    service_account_filename = os.environ.get(
        "SERVICE_ACCOUNT_FILENAME", "service_account.json"
    )
    service_account_credentials = None

    if service_account_json:
        try:
            service_account_credentials = json.loads(service_account_json)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from environment variable: {e}")

    if not service_account_credentials and os.path.exists(service_account_filename):
        with open(service_account_filename, "rb") as f:
            try:
                service_account_credentials = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Error decoding JSON from file {service_account_filename}: {e}"
                )

    if not service_account_credentials:
        raise ValueError(
            "Service account credentials not found. Please set the SERVICE_ACCOUNT_JSON environment variable or provide a service account JSON file."
        )

    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        service_account_credentials, SCOPE
    )
    client = gspread.authorize(credentials)
    return client.open_by_url(spreadsheet_url)


def valid_worksheet(worksheet):
    """
    Checks if the worksheet is valid. A worksheet is valid if it has the
    three required columns: ID, Front, Back. They do not necessarily
    need to be called that, but they need to be present.
    :param worksheet: The worksheet to check.
    :return: A tuple (bool, str) indicating if the worksheet is valid and an error message if not.
    """
    required_columns = ["ID", "Front", "Back"]
    rows = worksheet.get_all_values()
    if not rows:
        return False, "Worksheet is empty"
    header = rows[0]
    if len(header) < len(required_columns):
        return False, "Missing required columns"
    # Check at least one row with the required columns
    any_valid_row = False
    ids = set()
    for i, row in enumerate(rows[1:]):
        if len(row) < len(required_columns):
            continue
        id_ = row[0].strip()
        if not id_:
            return False, f"Row {i + 2} has empty ID column"
        if id_ in ids:
            return False, f"Row {i + 2} has duplicate ID column"
        ids.add(id_)
        any_valid_row = True
    if not any_valid_row:
        return False, "No valid cards found"

    return True, ""


def list_deck_names(url=DEFAULT_SPREADSHEET_URL):
    """
    Lists all the deck names (worksheet names).
    :return: A list of deck names.
    """
    if not url:
        return []
    spreadsheet = get_spreadsheet(url)
    worksheets = []
    for worksheet in spreadsheet.worksheets():
        valid, error = valid_worksheet(worksheet)
        if valid:
            worksheets.append((worksheet.title, ""))
        else:
            worksheets.append((worksheet.title, error))
    return worksheets


def sheet_to_deck(sheet):
    """
    Converts a Google Sheet to an Anki deck.
    :param sheet: The Google Sheet to convert.
    :return: The Anki deck.
    """
    rows = sheet.get_all_values()
    cards = []
    for row in rows[1:]:  # Skip the header row
        if len(row) >= 3:  # Ensure each row has at least two columns (ID, Front, Back)
            tags = (
                row[3].split(",") if len(row) > 3 else []
            )  # Tags are in the last column
            if all([row[1].strip(), row[2].strip()]):  # Skip blank entries
                cards.append((row[0], row[1], row[2], tags))

    model = genanki.Model(
        MODEL_ID,
        "Simple Card",
        fields=[
            {"name": "ID"},
            {"name": "Front"},
            {"name": "Back"},
        ],
        templates=[
            {
                "name": "Simple Card",
                "qfmt": '<div style="font-size: 24px; font-weight: bold; text-align: center">{{Front}}</div>',
                "afmt": '{{FrontSide}}<hr><div style="font-size: 20px; text-align: center">{{Back}}</div>',
            },
        ],
    )
    deck_id = int(hashlib.md5(sheet.title.encode("utf-8")).hexdigest(), 16) % (10**10)
    deck_name = sheet.title
    deck = genanki.Deck(deck_id, deck_name)
    for card_id, front, back, tags in cards:
        guid_keys = [deck.deck_id, card_id]
        guid = hashlib.md5("".join(map(str, guid_keys)).encode("utf-8")).hexdigest()
        id_ = f"{deck.deck_id}-{card_id}"

        note = genanki.Note(
            model=model,
            fields=[id_, front, back],
            tags=tags,
            guid=guid,
        )
        deck.add_note(note)
    return deck


def create_anki_decks():
    spreadsheet = get_spreadsheet()
    return [sheet_to_deck(worksheet) for worksheet in spreadsheet.worksheets()]


def export_deck_to_file(deck, filename, in_memory=False):
    if in_memory:
        file = BytesIO()
        genanki.Package(deck).write_to_file(file)
        file.seek(0)
    else:
        genanki.Package(deck).write_to_file(filename)
        print(f"Anki deck written to {filename}")
        file = open(filename, "rb")
    return file


def gen_filename(deck):
    """
    Generates a filename for the Anki deck.
    :param deck: The Anki deck.
    :return: The generated filename.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f'{deck.name.replace(" ", "_").lower()}_{timestamp}.apkg'


def gen_deck_file(deck_name, spreadsheet_url=DEFAULT_SPREADSHEET_URL, in_memory=False):
    """
    Generates an Anki deck from a Google Sheet.
    :param deck_name: The name of the deck to generate.
    :param spreadsheet_url: The URL of the Google Sheet.
    :return: The filename and file object of the generated Anki deck.
    """
    spreadsheet = get_spreadsheet(spreadsheet_url)
    worksheet = spreadsheet.worksheet(deck_name)
    deck = sheet_to_deck(worksheet)
    filename = gen_filename(deck)
    file_ = export_deck_to_file(deck, filename, in_memory=in_memory)
    return filename, file_


def main():
    for deck_name, error in list_deck_names():
        if not error:
            gen_deck_file(deck_name)
        else:
            print(f"! {deck_name} - Error: {error}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    main()
