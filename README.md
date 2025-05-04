# gsheet-anki

A simple app to translate Google Sheets to an Anki deck.

## Setup

Install uv and run `uv sync`. Install vercel CLI if you want to test the
server locally as well.

Set up a local .env:
```
SPREADSHEET_URL=https://docs.google.com/spreadsheets/d/.../edit?gid=0#gid=0
SERVICE_ACCOUNT_JSON=see below
USERNAME=admin
PASSWORD_HASH=see below
```

To get the service account JSON, create a Google Cloud Service Account,
enable the Sheets API, and invite the service account to your spreadsheet.

To get a password hash, run `uv run hash-pw`.

## Run local

### Scripts

To generate Anki decks for all sheets, run `uv run gen-deck`.

To import the most recently generated decks, run `uv run anki-import`.

### Web service

To run the web service locally, run `vercel dev`.

Alternative, to run without Vercel bits, run `uv run web`
