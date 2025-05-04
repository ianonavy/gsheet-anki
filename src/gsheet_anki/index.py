from urllib.parse import unquote

from fasthtml.common import *
from fasthtml.svg import *
from fa6_icons import svgs

from .gen_deck import list_deck_names, gen_deck_file


SECRET_KEY = os.getenv("SECRET_KEY")
app, rt = fast_app(
    secret_key=SECRET_KEY,
    hdrs=[
        Link(
            rel="stylesheet",
            href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.colors.min.css",
        ),
    ],
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
        Button("Submit", type="submit", style="flex: 0"),
        hx_post="/decks",
        hx_trigger="submit",
        hx_target="#decks",
        style="display: flex; flex-direction: row; gap: 0.5rem",
    )


@rt("/")
async def home(request: Request, session):
    spreadsheet_url = session.get("spreadsheet_url", "")
    all_decks = await decks(request, session)
    return (
        Title("gsheet-anki"),
        Body(
            Div(
                H1("gsheet-anki"),
                P(
                    "Generate ",
                    ExtA("Anki decks", href="https://apps.ankiweb.net/"),
                    " from ",
                    ExtA("Google Sheets", href="https://www.google.com/sheets/about/"),
                    ".",
                ),
                P(
                    "Create a new workbook. For each deck, create a worksheet with a header of four columns:"
                ),
                Ol(
                    Li(
                        Em("ID: "),
                        "Incrementing number starting from 1. Used for updating existing cards.",
                    ),
                    Li(Em("Front: "), "The front side of the card."),
                    Li(Em("Back: "), "The back side of the card."),
                    Li(
                        Em("Tags (optional): "),
                        "Comma-separated list of tags for each card.",
                    ),
                    type="A",
                ),
                P(
                    "Make the spreadsheet public, or invite ",
                    Code("live-demo@gsheet-anki.iam.gserviceaccount.com"),
                    " to your sheet and paste the link here.",
                ),
                input_form(spreadsheet_url),
                id="form",
            ),
            Div(
                all_decks,
                id="decks",
            ),
            footer(),
            style=(
                "display: flex; flex-direction: column; gap: 1rem;"
                "max-width: 800px; width: 100vw; padding: 1rem; margin: auto;"
                "font-family: sans-serif;"
            ),
        ),
    )


def ExtA(*args, **kwargs):
    kwargs["target"] = "_blank"
    kwargs["rel"] = "noopener noreferrer"
    return A(*args, **kwargs)


def footer():
    return Footer(
        Hr(),
        P(
            "Made with ",
            ExtA("FastHTML", href="https://fastht.ml/"),
            " and deployed with ",
            ExtA("Vercel", href="https://vercel.com/"),
            ".",
            style="margin-bottom: 0.5rem;",
        ),
        P(
            "Like this project? ",
            ExtA(
                "Star it on GitHub",
                href="https://github.com/ianonavy/gsheet-anki",
            ),
            " or ",
            ExtA(
                "buy me a potato",
                href="https://buymeacoffee.com/justapotato",
            ),
            ".",
            style="margin-bottom: 0.5rem;",
        ),
        style="font-size: 0.8rem; text-align: center; color: var(--pico-secondary);",
    )


@rt("/decks")
async def decks(request: Request, session):
    form = await request.form()
    spreadsheet_url = form.get("spreadsheet_url") or session.get("spreadsheet_url", "")

    if not spreadsheet_url:
        return None

    try:
        deck_names = list_deck_names(spreadsheet_url)
    except Exception as e:
        print(f"Error: {e}")
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
                style=(
                    "display: flex; flex-direction: column;"
                    "align-items: center; justify-content: center;"
                    "max-width: 20px; width:100%;"
                    "color: inherit;"
                ),
                href="/",
            ),
            style="display: flex; align-items: center; gap: 0.5rem",
        ),
        Ul(
            Li(
                (deck if error else A(deck, href=f"/download/{deck}")),
                (
                    (
                        " [",
                        Span(
                            Strong("Error: "), style="color: var(--pico-color-red-500)"
                        ),
                        error,
                        "]",
                    )
                    if error
                    else None
                ),
            )
            for (deck, error) in deck_names
        ),
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
