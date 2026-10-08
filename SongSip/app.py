import csv
import io
import random
import zipfile
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
CSV_ZIP_PATH = BASE_DIR / "spotify_tracks.csv.zip"
CSV_NAME = "spotify-tracks-dataset-detailed.csv"

GENRE_GROUPS = {
    "rock-metal": {
        "alt-rock", "alternative", "black-metal", "death-metal", "emo", "goth",
        "grindcore", "grunge", "hard-rock", "hardcore", "heavy-metal", "industrial",
        "j-rock", "metal", "metalcore", "psych-rock", "punk", "punk-rock", "rock",
        "rock-n-roll", "rockabilly", "ska",
    },
    "pop-indie": {
        "anime", "cantopop", "disney", "indie", "indie-pop", "j-idol", "j-pop",
        "k-pop", "mandopop", "pop", "pop-film", "power-pop", "synth-pop",
    },
    "electronic-dance": {
        "ambient", "breakbeat", "chicago-house", "club", "dance", "deep-house",
        "detroit-techno", "disco", "drum-and-bass", "dubstep", "edm", "electro",
        "electronic", "garage", "hardstyle", "house", "idm", "j-dance",
        "minimal-techno", "progressive-house", "techno", "trance",
    },
    "hip-hop-rnb": {"hip-hop", "r-n-b", "trip-hop"},
    "jazz-blues-funk-soul": {"blues", "funk", "gospel", "groove", "jazz", "soul"},
    "folk-country-acoustic": {
        "acoustic", "bluegrass", "country", "folk", "guitar", "honky-tonk",
        "singer-songwriter", "songwriter",
    },
    "latin-south-america": {
        "brazil", "forro", "latin", "latino", "mpb", "pagode", "salsa", "samba",
        "sertanejo", "tango",
    },
    "reggae-afro-caribbean": {"afrobeat", "dancehall", "dub", "reggae", "reggaeton"},
    "regional-international": {
        "british", "french", "german", "indian", "iranian", "malay", "spanish",
        "swedish", "turkish", "world-music",
    },
    "classical-instrumental": {"classical", "new-age", "opera", "piano"},
    "mood-activities-other": {
        "children", "chill", "comedy", "happy", "kids", "party", "romance", "sad",
        "show-tunes", "sleep", "study",
    },
}


def load_tracks():
    with zipfile.ZipFile(CSV_ZIP_PATH) as archive:
        with archive.open(CSV_NAME) as csv_file:
            text_stream = io.TextIOWrapper(csv_file, encoding="utf-8")
            return list(csv.DictReader(text_stream))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/api/songs")
def songs_api():
    genre = (request.args.get("genre") or "").strip().lower()
    tracks = load_tracks()

    if genre in GENRE_GROUPS:
        group_genres = GENRE_GROUPS[genre]
        tracks = [track for track in tracks if track.get("track_genre") in group_genres]
    elif genre and genre not in {"random", "willekeurig"}:
        normalized_genre = "".join(character for character in genre if character.isalnum())
        if not normalized_genre:
            return jsonify({"error": f"Ongeldig genre '{genre}'"}), 400
        tracks = [
            track
            for track in tracks
            if normalized_genre
            in "".join(
                character
                for character in (track.get("track_genre") or "").lower()
                if character.isalnum()
            )
        ]

    if not tracks:
        return jsonify({"error": f"Geen nummers gevonden voor genre '{genre}'"}), 404

    return jsonify(random.sample(tracks, min(10, len(tracks))))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/dailysong")
def dailysong():
    return render_template("dailysong.html")


@app.route("/history")
def history():
    return render_template("history.html")


if __name__ == "__main__":
    app.run(debug=True)