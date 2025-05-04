from urllib.parse import unquote

from fasthtml.common import *
from fasthtml.svg import *
from fa6_icons import svgs

from .gen_deck import list_deck_names, gen_deck_file


SECRET_KEY = os.getenv("SECRET_KEY")
app, rt = fast_app(
    secret_key=SECRET_KEY,
    pico=False,
    hdrs=[Style("h1, h2 { margin: 0; }")],
)


def input_form(spreadsheet_url=""):
    return Form(
        Input(
            type="text",
            name="spreadsheet_url",
            placeholder="Enter Spreadsheet URL",
            value=spreadsheet_url,
            style="width: 100%",
        ),
        Button("Submit", type="submit"),
        hx_post="/decks",
        hx_trigger="submit",
        hx_target="#decks",
        style="display: flex; flex-direction: row; gap: 10px; width: 800px",
    )


@rt("/")
async def home(request: Request, session):
    spreadsheet_url = session.get("spreadsheet_url", "")
    all_decks = await decks(request, session)
    return Body(
        H1("gsheet-anki"),
        input_form(spreadsheet_url),
        Div(
            all_decks,
            id="decks",
        ),
        style="width: 800px; display: flex; flex-direction: column; gap: 20px; font-family: sans-serif",
    )


@rt("/decks")
async def decks(request: Request, session):
    form = await request.form()
    spreadsheet_url = form.get("spreadsheet_url") or session.get("spreadsheet_url", "")

    if not spreadsheet_url:
        return None

    try:
        deck_names = list_deck_names(spreadsheet_url)
    except:
        deck_names = []

    if not deck_names:
        return (
            H2("Error"),
            P("No decks found or invalid spreadsheet URL."),
        )

    session["spreadsheet_url"] = spreadsheet_url
    available_decks = (
        H2(
            "Available Decks",
            A(
                svgs.arrows_rotate.solid,
                style="font-weight: normal; color: inherit; max-width: 20px; width:100%; max-height: 20px; height: 100%; display: flex",
                href="/",
            ),
            style="display: flex; align-items: center; gap: 8px",
        ),
        Ul(Li(A(deck, href=f"/download/{deck}")) for deck in deck_names),
    )
    return available_decks


@rt("/download/{deck}")
async def download(deck: str, session):
    deck = unquote(deck)
    spreadsheet_url = session.get("spreadsheet_url")
    filename, file_ = gen_deck_file(deck, spreadsheet_url, in_memory=True)
    return StreamingResponse(
        file_,
        media_type="application/vnd.anki.apkg",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Content-Length": str(file_.getbuffer().nbytes),
        },
    )


def main():
    from dotenv import load_dotenv

    load_dotenv()
    serve()
