import base64
import csv
from collections import Counter
import io
import json
import os
import random
import secrets
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from contextlib import closing
from pathlib import Path
from database import (
    get_recommendations,
    init_db,
    record_recommendation,
    save_rating,
)

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)

BASE_DIR = Path(__file__).resolve().parent
CSV_ZIP_PATH = BASE_DIR / "spotify_tracks.csv.zip"
CSV_NAME = "spotify-tracks-dataset-detailed.csv"
SPOTIFY_REDIRECT_URI = "http://127.0.0.1:5000/callback"
SPOTIFY_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SAVED_TRACKS_URL = "https://api.spotify.com/v1/me/tracks"
SPOTIFY_RECENT_TRACKS_URL = "https://api.spotify.com/v1/me/player/recently-played"
DATABASE_PATH = BASE_DIR / "songsip.sqlite3"


class SpotifyApiError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code


def clear_pending_spotify_login():
    session.pop("spotify_oauth_state", None)
    session.pop("spotify_session_id", None)
    session.pop("spotify_user", None)


def ensure_database_schema(connection):
    connection.execute(
        """CREATE TABLE IF NOT EXISTS spotify_saved_tracks (
            session_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            PRIMARY KEY (session_id, track_id)
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS spotify_library_snapshots (
            session_id TEXT PRIMARY KEY,
            matching_track_count INTEGER NOT NULL
        )"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS spotify_recent_genres (
            session_id TEXT NOT NULL,
            genre TEXT NOT NULL,
            play_count INTEGER NOT NULL,
            PRIMARY KEY (session_id, genre)
        )"""
    )
    
    connection.execute(
        """CREATE TABLE IF NOT EXISTS song_ratings (
            session_id TEXT NOT NULL,
            track_id TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
            PRIMARY KEY (session_id, track_id)
        )"""
    )



def fetch_saved_dataset_track_ids(access_token):
    dataset_track_ids = {track["track_id"] for track in load_tracks() if track.get("track_id")}
    saved_track_ids = set()
    offset = 0

    for _ in range(1000):
        url = f"{SPOTIFY_SAVED_TRACKS_URL}?limit=50&offset={offset}"
        saved_tracks_request = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        try:
            with urllib.request.urlopen(saved_tracks_request, timeout=15) as response:
                page = json.loads(response.read().decode())
        except urllib.error.HTTPError as exc:
            raise SpotifyApiError(exc.code) from exc
        except urllib.error.URLError as exc:
            raise SpotifyApiError(0) from exc

        items = page.get("items")
        if not isinstance(items, list):
            raise SpotifyApiError(0)

        for item in items:
            track = item.get("track") or {}
            track_id = track.get("id")
            if track_id in dataset_track_ids:
                saved_track_ids.add(track_id)

        if not page.get("next"):
            return saved_track_ids
        if not items:
            raise SpotifyApiError(0)
        offset = page.get("offset", offset) + len(items)

    raise SpotifyApiError(0)


def fetch_recent_dataset_genres(access_token):
    dataset_genres_by_id = {
        track["track_id"]: track["track_genre"]
        for track in load_tracks()
        if track.get("track_id") and track.get("track_genre")
    }
    url = f"{SPOTIFY_RECENT_TRACKS_URL}?limit=50"
    recent_request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(recent_request, timeout=15) as response:
            page = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise SpotifyApiError(exc.code) from exc
    except urllib.error.URLError as exc:
        raise SpotifyApiError(0) from exc

    items = page.get("items")
    if not isinstance(items, list):
        raise SpotifyApiError(0)

    recent_genres = Counter()
    for item in items:
        track = item.get("track") or {}
        genre = dataset_genres_by_id.get(track.get("id"))
        if genre:
            recent_genres[genre] += 1
    return recent_genres


def save_saved_track_ids(session_id, track_ids):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        ensure_database_schema(connection)
        connection.execute(
            "DELETE FROM spotify_saved_tracks WHERE session_id = ?", (session_id,)
        )
        connection.execute(
            "DELETE FROM spotify_library_snapshots WHERE session_id = ?", (session_id,)
        )
        connection.executemany(
            "INSERT INTO spotify_saved_tracks (session_id, track_id) VALUES (?, ?)",
            ((session_id, track_id) for track_id in track_ids),
        )
        connection.execute(
            """INSERT INTO spotify_library_snapshots
                (session_id, matching_track_count) VALUES (?, ?)""",
            (session_id, len(track_ids)),
        )


def save_recent_genres(session_id, genre_counts):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        ensure_database_schema(connection)
        connection.execute(
            "DELETE FROM spotify_recent_genres WHERE session_id = ?", (session_id,)
        )
        connection.executemany(
            "INSERT INTO spotify_recent_genres (session_id, genre, play_count) "
            "VALUES (?, ?, ?)",
            (
                (session_id, genre, count)
                for genre, count in genre_counts.items()
                if count > 0
            ),
        )


def get_recent_genres(session_id):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        ensure_database_schema(connection)
        rows = connection.execute(
            "SELECT genre, play_count FROM spotify_recent_genres WHERE session_id = ?",
            (session_id,),
        )
        return Counter(dict(rows))


def get_saved_track_ids(session_id):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        ensure_database_schema(connection)
        snapshot = connection.execute(
            "SELECT matching_track_count FROM spotify_library_snapshots WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if snapshot is None:
            return None
        rows = connection.execute(
            "SELECT track_id FROM spotify_saved_tracks WHERE session_id = ?",
            (session_id,),
        )
        return {row[0] for row in rows}


def delete_saved_track_ids(session_id):
    with closing(sqlite3.connect(DATABASE_PATH)) as connection, connection:
        ensure_database_schema(connection)
        connection.execute(
            "DELETE FROM spotify_saved_tracks WHERE session_id = ?", (session_id,)
        )
        connection.execute(
            "DELETE FROM spotify_library_snapshots WHERE session_id = ?", (session_id,)
        )
        connection.execute(
            "DELETE FROM spotify_recent_genres WHERE session_id = ?", (session_id,)
        )

GENRE_GROUPS = {
    "rock-metal": {
        "alt-rock", "alternative", "black-metal", "death-metal", "emo", "goth",
        "grindcore", "grunge", "hard-rock", "hardcore", "heavy-metal", "industrial",
        "metal", "metalcore", "psych-rock", "punk", "punk-rock", "rock",
        "rock-n-roll", "rockabilly", "ska",
    },
    "pop-indie": {
        "disney", "indie", "indie-pop", "pop", "pop-film", "power-pop", "synth-pop",
    },
    "asian": {
        "anime", "cantopop", "indian", "j-idol", "j-pop", "j-rock", "k-pop",
        "mandopop",
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
        "british", "french", "german", "iranian", "malay", "spanish",
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
    session_id = session.get("spotify_session_id")
    if session_id and get_saved_track_ids(session_id) is None:
        session.pop("spotify_user", None)
        session.pop("spotify_session_id", None)
        flash("Log opnieuw in om je opgeslagen Spotify-nummers te controleren.", "error")
    return render_template("index.html")


@app.route("/home")
def home():
    session_id = session.get("spotify_session_id")
    if not session.get("spotify_user") or not session_id:
        flash("Log in met Spotify om nummers te ontdekken.", "error")
        return redirect(url_for("index"))
    if get_saved_track_ids(session_id) is None:
        flash("Log opnieuw in zodat SongSip je opgeslagen nummers kan controleren.", "error")
        return redirect(url_for("index"))
    return render_template("home.html")


@app.route("/login/spotify")
def spotify_login():
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    if not client_id or not os.environ.get("SPOTIFY_CLIENT_SECRET"):
        flash(
            "Spotify is nog niet ingesteld. Stel SPOTIFY_CLIENT_ID en "
            "SPOTIFY_CLIENT_SECRET in de terminal in en start de app opnieuw.",
            "error",
        )
        return redirect(url_for("index"))

    previous_session_id = session.get("spotify_session_id")
    if previous_session_id:
        delete_saved_track_ids(previous_session_id)

    state = secrets.token_urlsafe(32)
    session["spotify_oauth_state"] = state
    session["spotify_session_id"] = secrets.token_urlsafe(32)
    authorization_url = SPOTIFY_AUTHORIZE_URL + "?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": SPOTIFY_REDIRECT_URI,
            "scope": "user-read-private user-library-read user-read-recently-played",
            "state": state,
            "show_dialog": "true",
        }
    )
    return redirect(authorization_url)


@app.route("/callback")
def spotify_callback():
    error = request.args.get("error")
    if error:
        flash(f"Spotify-login is niet voltooid: {error}.", "error")
        return redirect(url_for("index"))

    expected_state = session.pop("spotify_oauth_state", None)
    returned_state = request.args.get("state", "")
    authorization_code = request.args.get("code")
    if not expected_state or not secrets.compare_digest(expected_state, returned_state):
        flash("De Spotify-login kon niet veilig worden bevestigd. Probeer opnieuw.", "error")
        return redirect(url_for("index"))
    if not authorization_code:
        flash("Spotify heeft geen autorisatiecode teruggestuurd. Probeer opnieuw.", "error")
        return redirect(url_for("index"))

    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    if not client_id or not client_secret:
        flash("De Spotify-appgegevens ontbreken. Stel ze in en probeer opnieuw.", "error")
        return redirect(url_for("index"))

    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    token_request = urllib.request.Request(
        SPOTIFY_TOKEN_URL,
        data=urllib.parse.urlencode(
            {
                "grant_type": "authorization_code",
                "code": authorization_code,
                "redirect_uri": SPOTIFY_REDIRECT_URI,
            }
        ).encode(),
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(token_request, timeout=15) as response:
            token_data = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        app.logger.warning("Spotify token exchange returned HTTP %s", exc.code)
        flash("Spotify kon de login niet afronden. Controleer de app-instellingen.", "error")
        return redirect(url_for("index"))
    except urllib.error.URLError:
        app.logger.exception("Could not reach Spotify token endpoint")
        flash("Spotify is tijdelijk niet bereikbaar. Probeer het later opnieuw.", "error")
        return redirect(url_for("index"))

    access_token = token_data.get("access_token")
    if not access_token:
        app.logger.error("Spotify token response did not contain an access token")
        flash("Spotify heeft geen toegangstoken teruggestuurd. Probeer opnieuw.", "error")
        return redirect(url_for("index"))
    granted_scopes = set(token_data.get("scope", "").split())
    if not {"user-library-read", "user-read-recently-played"} <= granted_scopes:
        session.pop("spotify_session_id", None)
        flash(
            "SongSip heeft niet alle benodigde Spotify-toestemmingen gekregen. "
            "Log opnieuw in en geef die toestemming.",
            "error",
        )
        return redirect(url_for("index"))

    profile_request = urllib.request.Request(
        "https://api.spotify.com/v1/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    try:
        with urllib.request.urlopen(profile_request, timeout=15) as response:
            profile = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        app.logger.warning("Spotify profile request returned HTTP %s", exc.code)
        clear_pending_spotify_login()
        flash(
            f"Je Spotify-profiel kon niet worden opgehaald (HTTP {exc.code}). "
            "Controleer de Spotify-app en probeer opnieuw.",
            "error",
        )
        return redirect(url_for("index"))
    except urllib.error.URLError:
        app.logger.exception("Could not reach Spotify profile endpoint")
        clear_pending_spotify_login()
        flash("Spotify is tijdelijk niet bereikbaar. Probeer het later opnieuw.", "error")
        return redirect(url_for("index"))

    session_id = session.get("spotify_session_id")
    if not session_id:
        flash("De SongSip-sessie is verlopen. Log opnieuw in met Spotify.", "error")
        return redirect(url_for("index"))
    try:
        saved_track_ids = fetch_saved_dataset_track_ids(access_token)
    except SpotifyApiError as exc:
        if exc.status_code == 403:
            app.logger.warning("Spotify denied access to saved tracks (HTTP 403)")
            flash(
                "Spotify heeft de toegang tot opgeslagen nummers geweigerd. "
                "Controleer de app-toegang en probeer opnieuw.",
                "error",
            )
        elif exc.status_code == 401:
            app.logger.warning("Spotify access token was rejected for saved tracks")
            flash("Spotify-login is verlopen. Log opnieuw in.", "error")
        elif exc.status_code:
            app.logger.warning(
                "Spotify saved-tracks request returned HTTP %s", exc.status_code
            )
            flash("De opgeslagen Spotify-nummers konden niet worden opgehaald.", "error")
        else:
            app.logger.exception("Could not retrieve the complete Spotify saved-tracks list")
            flash(
                "De volledige opgeslagen Spotify-lijst kon niet veilig worden opgehaald. "
                "Probeer het later opnieuw.",
                "error",
            )
        return redirect(url_for("index"))

    try:
        recent_genres = fetch_recent_dataset_genres(access_token)
    except SpotifyApiError as exc:
        if exc.status_code == 403:
            app.logger.warning("Spotify denied access to recently played tracks (HTTP 403)")
            flash(
                "Spotify heeft de toegang tot recent afgespeelde nummers geweigerd. "
                "Controleer de app-toegang en probeer opnieuw.",
                "error",
            )
        elif exc.status_code == 401:
            app.logger.warning("Spotify access token was rejected for recently played tracks")
            flash("Spotify-login is verlopen. Log opnieuw in.", "error")
        elif exc.status_code:
            app.logger.warning(
                "Spotify recently-played request returned HTTP %s", exc.status_code
            )
            flash("Recente Spotify-nummers konden niet worden opgehaald.", "error")
        else:
            app.logger.exception("Could not retrieve recently played Spotify tracks")
            flash(
                "De recente Spotify-nummers konden niet veilig worden opgehaald. "
                "Probeer het later opnieuw.",
                "error",
            )
        return redirect(url_for("index"))

    save_saved_track_ids(session_id, saved_track_ids)
    save_recent_genres(session_id, recent_genres)
    session["spotify_user"] = {
        "display_name": profile.get("display_name") or profile.get("id") or "Spotify-gebruiker",
        "saved_dataset_track_count": len(saved_track_ids),
        "recent_dataset_track_count": sum(recent_genres.values()),
    }
    flash(
        f"Spotify-login gelukt! {len(saved_track_ids)} opgeslagen nummers worden overgeslagen "
        f"en {sum(recent_genres.values())} recente afspeelbeurten helpen bij de aanbevelingen.",
        "success",
    )
    return redirect(url_for("index"))


@app.route("/logout/spotify", methods=["POST"])
def spotify_logout():
    session_id = session.pop("spotify_session_id", None)
    if session_id:
        delete_saved_track_ids(session_id)
    session.pop("spotify_user", None)
    flash("Je bent uitgelogd bij SongSip.", "success")
    return redirect(url_for("index"))


@app.route("/api/songs")
def songs_api():
    session_id = session.get("spotify_session_id")
    if not session.get("spotify_user") or not session_id:
        return jsonify({"error": "Log in met Spotify om opgeslagen nummers te controleren."}), 401
    saved_track_ids = get_saved_track_ids(session_id)
    if saved_track_ids is None:
        return jsonify({"error": "Log opnieuw in om je Spotify-bibliotheek te controleren."}), 401

    genre = (request.args.get("genre") or "").strip().lower()
    all_tracks = load_tracks()
    saved_genres = Counter(
        track["track_genre"]
        for track in all_tracks
        if track.get("track_id") in saved_track_ids and track.get("track_genre")
    )
    recent_genres = get_recent_genres(session_id)
    preference_genres = saved_genres.copy()
    preference_genres.update(
        {genre: play_count * 3 for genre, play_count in recent_genres.items()}
    )
    tracks = all_tracks

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

    tracks = [track for track in tracks if track.get("track_id") not in saved_track_ids]
    if not tracks:
        return jsonify(
            {"error": "Alle nummers in deze categorie zijn al opgeslagen in je Spotify-bibliotheek."}
        ), 404

    candidate_counts = Counter(track.get("track_genre") for track in tracks)
    personalized = any(
        preference_genres.get(track.get("track_genre"), 0) for track in tracks
    )

    if personalized:
        weights = [
            (1 + preference_genres.get(track.get("track_genre"), 0))
            / candidate_counts[track.get("track_genre")]
            for track in tracks
        ]
        song = random.choices(tracks, weights=weights, k=1)[0]
    else:
        song = random.choice(tracks)

    record_recommendation(session_id, song)

    return jsonify(
        {
            "song": song,
            "personalized": personalized,
        }
    )



@app.route("/api/rating", methods=["POST"])
def rate_song():
    session_id = session.get("spotify_session_id")

    if not session_id or not session.get("spotify_user"):
        return jsonify({"error": "Log eerst in."}), 401

    data = request.get_json(silent=True) or {}
    track_id = data.get("track_id")
    rating = data.get("rating")

    if not isinstance(track_id, str) or not track_id.strip():
        return jsonify({"error": "Ongeldig nummer."}), 400

    if type(rating) is not int or rating not in (-1, 1):
        return jsonify({"error": "Ongeldige beoordeling."}), 400

    save_rating(session_id, track_id, rating)

    return jsonify({"success": True, "rating": rating})
@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/history")
def history():
    session_id = session.get("spotify_session_id")
    if not session.get("spotify_user") or not session_id:
        flash("Log in met Spotify om je aanbevolen nummers te bekijken.", "error")
        return redirect(url_for("index"))
    return render_template(
        "history.html",
        recommendations=get_recommendations(session_id),
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)