import sqlite3
from datetime import datetime
from config import Config

def get_db_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Favorites Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song TEXT UNIQUE,
        artist TEXT,
        genre TEXT,
        image TEXT,
        preview TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Recently Played Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recently_played (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song TEXT,
        artist TEXT,
        genre TEXT,
        image TEXT,
        preview TEXT,
        played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Search History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT,
        searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Playlists Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Playlist Songs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER,
        song TEXT,
        artist TEXT,
        genre TEXT,
        image TEXT,
        preview TEXT,
        FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
        UNIQUE(playlist_id, song)
    )
    """)
    
    conn.commit()
    conn.close()

# ---------------------------------------------
# Favorites Operations
# ---------------------------------------------

def add_favorite(song, artist="", genre="", image="", preview=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT OR IGNORE INTO favorites (song, artist, genre, image, preview) VALUES (?, ?, ?, ?, ?)",
            (song, artist, genre, image, preview)
        )
        conn.commit()
    except Exception as e:
        print(f"Error adding favorite: {e}")
    finally:
        conn.close()

def remove_favorite(song):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM favorites WHERE song = ?", (song,))
        conn.commit()
    except Exception as e:
        print(f"Error removing favorite: {e}")
    finally:
        conn.close()

def get_favorites():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM favorites ORDER BY created_at DESC")
    rows = cursor.fetchall()
    favorites = [dict(row) for row in rows]
    conn.close()
    return favorites

def is_favorite(song):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE song = ?", (song,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

# ---------------------------------------------
# Recently Played Operations
# ---------------------------------------------

def add_history(song, artist="", genre="", image="", preview=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Avoid duplicate consecutive entries if played again
        cursor.execute("SELECT song FROM recently_played ORDER BY played_at DESC LIMIT 1")
        last_song = cursor.fetchone()
        if not last_song or last_song['song'] != song:
            cursor.execute(
                "INSERT INTO recently_played (song, artist, genre, image, preview) VALUES (?, ?, ?, ?, ?)",
                (song, artist, genre, image, preview)
            )
            conn.commit()
    except Exception as e:
        print(f"Error adding play history: {e}")
    finally:
        conn.close()

def get_history(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recently_played ORDER BY played_at DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    conn.close()
    return history

# ---------------------------------------------
# Search History Operations
# ---------------------------------------------

def add_search(query):
    if not query or not query.strip():
        return
    query = query.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Avoid spamming duplicates consecutively
        cursor.execute("SELECT query FROM search_history ORDER BY searched_at DESC LIMIT 1")
        last_query = cursor.fetchone()
        if not last_query or last_query['query'].lower() != query.lower():
            cursor.execute("INSERT INTO search_history (query) VALUES (?)", (query,))
            conn.commit()
    except Exception as e:
        print(f"Error adding search history: {e}")
    finally:
        conn.close()

def get_search_history(limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT query, count(query) as search_count, max(searched_at) as last_searched FROM search_history GROUP BY query ORDER BY last_searched DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    searches = [dict(row) for row in rows]
    conn.close()
    return searches

# ---------------------------------------------
# Playlist Operations
# ---------------------------------------------

def create_playlist(name):
    if not name or not name.strip():
        return False
    name = name.strip()
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    try:
        cursor.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        conn.commit()
        success = True
    except Exception as e:
        print(f"Error creating playlist: {e}")
    finally:
        conn.close()
    return success

def delete_playlist(name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM playlists WHERE name = ?", (name,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting playlist: {e}")
    finally:
        conn.close()

def get_playlists():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM playlists ORDER BY name ASC")
    rows = cursor.fetchall()
    playlists = [dict(row) for row in rows]
    conn.close()
    return playlists

def add_to_playlist(playlist_name, song, artist="", genre="", image="", preview=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    success = False
    try:
        cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
        row = cursor.fetchone()
        if row:
            playlist_id = row['id']
            cursor.execute(
                "INSERT OR IGNORE INTO playlist_songs (playlist_id, song, artist, genre, image, preview) VALUES (?, ?, ?, ?, ?, ?)",
                (playlist_id, song, artist, genre, image, preview)
            )
            conn.commit()
            success = True
    except Exception as e:
        print(f"Error adding to playlist: {e}")
    finally:
        conn.close()
    return success

def remove_from_playlist(playlist_name, song):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
        row = cursor.fetchone()
        if row:
            playlist_id = row['id']
            cursor.execute(
                "DELETE FROM playlist_songs WHERE playlist_id = ? AND song = ?",
                (playlist_id, song)
            )
            conn.commit()
    except Exception as e:
        print(f"Error removing from playlist: {e}")
    finally:
        conn.close()

def get_playlist_songs(playlist_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    songs = []
    try:
        cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
        row = cursor.fetchone()
        if row:
            playlist_id = row['id']
            cursor.execute("SELECT * FROM playlist_songs WHERE playlist_id = ? ORDER BY id DESC", (playlist_id,))
            rows = cursor.fetchall()
            songs = [dict(r) for r in rows]
    except Exception as e:
        print(f"Error getting playlist songs: {e}")
    finally:
        conn.close()
    return songs

# ---------------------------------------------
# Statistics Operations
# ---------------------------------------------

def get_dashboard_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    stats = {
        "total_favorites": 0,
        "total_played": 0,
        "most_played_artist": "N/A",
        "search_count": 0,
        "popular_genres": []
    }
    try:
        # Total favorites
        cursor.execute("SELECT COUNT(*) FROM favorites")
        stats["total_favorites"] = cursor.fetchone()[0]
        
        # Total played
        cursor.execute("SELECT COUNT(*) FROM recently_played")
        stats["total_played"] = cursor.fetchone()[0]
        
        # Most played artist
        cursor.execute("SELECT artist, COUNT(artist) as play_count FROM recently_played GROUP BY artist ORDER BY play_count DESC LIMIT 1")
        row = cursor.fetchone()
        if row and row['artist']:
            stats["most_played_artist"] = f"{row['artist']} ({row['play_count']} plays)"
            
        # Search count
        cursor.execute("SELECT COUNT(*) FROM search_history")
        stats["search_count"] = cursor.fetchone()[0]
        
        # Popular genres (combine genres from favorites and recently_played)
        cursor.execute("""
            SELECT genre, COUNT(genre) as count FROM (
                SELECT genre FROM favorites WHERE genre != '' AND genre IS NOT NULL
                UNION ALL
                SELECT genre FROM recently_played WHERE genre != '' AND genre IS NOT NULL
            ) GROUP BY genre ORDER BY count DESC LIMIT 5
        """)
        rows = cursor.fetchall()
        stats["popular_genres"] = [{"genre": r['genre'], "count": r['count']} for r in rows]
        
    except Exception as e:
        print(f"Error fetching dashboard statistics: {e}")
    finally:
        conn.close()
    return stats
