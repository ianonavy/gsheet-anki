from urllib.parse import unquote

from dotenv import load_dotenv
from flask import Flask, send_file, render_template

from .auth import auth
from .gen_deck import list_deck_names, gen_deck_file


load_dotenv()
app = Flask(__name__)


@app.route('/')
@auth.login_required
def home():
    decks = list_deck_names()
    return render_template('home.html', decks=decks)


@app.route('/download/<deck>')
@auth.login_required
def download(deck):
    deck_name = unquote(deck)
    filename, file_ = gen_deck_file(deck_name)
    if file_:
        return send_file(file_, download_name=filename, as_attachment=True)
    elif not filename:
        return "Deck not found", 404
    return "Error generating deck", 500


if __name__ == '__main__':
    app.run(debug=True)
