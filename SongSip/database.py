
import sqlite3
from pathlib import Path
from contextlib import closing

DATABASE_PATH = Path(__file__).resolve().parent / "songsip.sqlite3"


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def init_db():
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS song_ratings (
                session_id TEXT NOT NULL,
                track_id TEXT NOT NULL,
                rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
                PRIMARY KEY (session_id, track_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS listened_tracks (
                session_id TEXT NOT NULL,
                track_id TEXT NOT NULL,
                PRIMARY KEY (session_id, track_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS recommended_tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                track_id TEXT NOT NULL,
                track_name TEXT NOT NULL,
                artists TEXT NOT NULL,
                album_name TEXT NOT NULL,
                recommended_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_rating(session_id, track_id, rating):
    if rating not in (-1, 1):
        raise ValueError("Rating moet 1 (leuk) of -1 (niet leuk) zijn.")

    with closing(get_connection()) as connection, connection:
        connection.execute("""
            INSERT INTO song_ratings (session_id, track_id, rating)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id, track_id)
            DO UPDATE SET rating = excluded.rating
        """, (session_id, track_id, rating))


def migrate_session_history(session_id, account_id):
    if not session_id or not account_id or session_id == account_id:
        return

    init_db()
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            INSERT OR IGNORE INTO song_ratings (session_id, track_id, rating)
            SELECT ?, track_id, rating
            FROM song_ratings
            WHERE session_id = ?
        """, (account_id, session_id))
        connection.execute("""
            INSERT INTO recommended_tracks
                (session_id, track_id, track_name, artists, album_name, recommended_at)
            SELECT ?, track_id, track_name, artists, album_name, recommended_at
            FROM recommended_tracks
            WHERE session_id = ?
        """, (account_id, session_id))
        connection.execute(
            "DELETE FROM song_ratings WHERE session_id = ?", (session_id,)
        )
        connection.execute(
            "DELETE FROM recommended_tracks WHERE session_id = ?", (session_id,)
        )


def mark_listened(session_id, track_id):
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            INSERT OR IGNORE INTO listened_tracks (session_id, track_id)
            VALUES (?, ?)
        """, (session_id, track_id))


def record_recommendation(session_id, track):
    init_db()
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            INSERT INTO recommended_tracks
                (session_id, track_id, track_name, artists, album_name)
            VALUES (?, ?, ?, ?, ?)
        """, (
            session_id,
            track["track_id"],
            track.get("track_name") or "",
            track.get("artists") or "",
            track.get("album_name") or "",
        ))


def get_recommendations(session_id):
    init_db()
    with closing(get_connection()) as connection:
        rows = connection.execute("""
            SELECT recommended_tracks.track_id,
                   recommended_tracks.track_name,
                   recommended_tracks.artists,
                   recommended_tracks.album_name,
                   recommended_tracks.recommended_at,
                   song_ratings.rating
            FROM recommended_tracks
            LEFT JOIN song_ratings
                ON song_ratings.session_id = recommended_tracks.session_id
                AND song_ratings.track_id = recommended_tracks.track_id
            WHERE recommended_tracks.session_id = ?
            ORDER BY recommended_tracks.id DESC
        """, (session_id,)).fetchall()

    return [
        {
            "track_id": row[0],
            "track_name": row[1],
            "artists": row[2],
            "album_name": row[3],
            "recommended_at": row[4],
            "rating": row[5],
        }
        for row in rows
    ]


def get_listened_track_ids(session_id):
    with closing(get_connection()) as connection:
        rows = connection.execute("""
            SELECT track_id
            FROM listened_tracks
            WHERE session_id = ?
        """, (session_id,)).fetchall()

    return {row[0] for row in rows}
