
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


def mark_listened(session_id, track_id):
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            INSERT OR IGNORE INTO listened_tracks (session_id, track_id)
            VALUES (?, ?)
        """, (session_id, track_id))


def get_listened_track_ids(session_id):
    with closing(get_connection()) as connection:
        rows = connection.execute("""
            SELECT track_id
            FROM listened_tracks
            WHERE session_id = ?
        """, (session_id,)).fetchall()

    return {row[0] for row in rows}
