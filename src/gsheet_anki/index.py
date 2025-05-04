from urllib.parse import unquote

from fasthtml.common import *

from .gen_deck import list_deck_names, gen_deck_file


SECRET_KEY = os.getenv("SECRET_KEY")
USERNAME = os.getenv("USERNAME", "admin")
PASSWORD = os.getenv("PASSWORD", "password")
auth = user_pwd_auth(
    {USERNAME: PASSWORD}, skip=["/favicon.ico", r"/static/.*", r".*\.css"]
)
app, rt = fast_app(secret_key=SECRET_KEY, middleware=[auth])


@rt("/")
def home():
    decks = list_deck_names()
    return Div(
        H1("gsheet-anki"),
        H2("Available Decks"),
        Ul(Li(A(deck, href=f"/download/{deck}")) for deck in decks),
    )


@rt("/download/{deck}")
def download(deck: str):
    deck = unquote(deck)
    filename, file_ = gen_deck_file(deck, in_memory=True)
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
