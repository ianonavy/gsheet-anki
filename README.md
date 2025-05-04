# gsheet-anki

A simple app to translate Google Sheets to an Anki deck.

## Setup

Install uv and run `uv sync`. Install vercel CLI if you want to test the
server locally as well.

Set up a local .env:
```
SPREADSHEET_URL=[only needed for local scripts]
SERVICE_ACCOUNT_JSON=see below
```

To get the service account JSON, create a Google Cloud Service Account,
enable the Sheets API, and invite the service account to your spreadsheet.

## Run local

### Scripts

To generate Anki decks for all sheets, run `uv run gen-deck`.

To import the most recently generated decks, run `uv run anki-import`.

### Web service

To run the web service locally, run `vercel dev`.

Alternative, to run without Vercel bits, run `uv run web`

To sync the requirements.txt Vercel uses with uv.lock,

```bash
uv export --no-emit-project > requirements.txt
```
