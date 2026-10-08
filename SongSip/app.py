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

    if genre and genre not in {"random", "willekeurig"}:
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