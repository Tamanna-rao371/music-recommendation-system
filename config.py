import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "portfolio_music_recommender_secret_key_123")
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "database.db")
    
    # Spotify API credentials
    SPOTIFY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET", "")
    
    # Dataset path
    DATASET_PATH = os.environ.get("DATASET_PATH", "dataset/songs.csv")
    CATALOG_SIZE = int(os.environ.get("CATALOG_SIZE", 15000))
