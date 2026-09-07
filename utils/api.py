import json
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import urllib.parse
from config import Config

CACHE_FILE = "spotify_cache.json"

# Load local cache
def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_cache(cache):
    try:
        def default_serializer(obj):
            if hasattr(obj, 'item'):
                return obj.item()
            return str(obj)

        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=4, ensure_ascii=False, default=default_serializer)
    except Exception as e:
        print(f"Error saving Spotify cache: {e}")

_cache = load_cache()

def generate_gradient_cover(song_name, genre=""):
    # Pre-defined professional gradient pairs (start, end)
    gradients = [
        ("#7b61ff", "#ff4081"),  # Purple/Pink
        ("#1db954", "#121824"),  # Spotify Green/Dark Blue
        ("#2196f3", "#00bcd4"),  # Blue/Teal
        ("#ff9800", "#ff5722"),  # Orange/Red
        ("#9c27b0", "#e91e63"),  # Violet/Magenta
        ("#3f51b5", "#1a237e"),  # Indigo/Deep Blue
        ("#00f2fe", "#4facfe"),  # Bright Cyan/Blue
        ("#f093fb", "#f5576c"),  # Pink/Coral
        ("#f6d365", "#fda085"),  # Light Gold/Coral
        ("#11998e", "#38ef7d")   # Deep Teal/Neon Green
    ]
    
    # Hash the song name to select a gradient
    idx = sum(ord(c) for c in song_name) % len(gradients)
    start_color, end_color = gradients[idx]
    
    # Clean up genre for presentation
    genre_display = genre.upper() if genre else "MUSIC"
    
    # Inline SVG representing a vinyl record
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300" viewBox="0 0 300 300">
      <defs>
        <linearGradient id="grad-{idx}" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="{start_color}" />
          <stop offset="100%" stop-color="{end_color}" />
        </linearGradient>
      </defs>
      <rect width="100%" height="100%" fill="url(#grad-{idx})" />
      
      <!-- Vinyl record background outline -->
      <circle cx="150" cy="150" r="110" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="20" />
      <circle cx="150" cy="150" r="90" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="15" />
      <circle cx="150" cy="150" r="70" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="10" />
      
      <!-- Center Vinyl Label -->
      <circle cx="150" cy="150" r="45" fill="#121824" />
      <circle cx="150" cy="150" r="40" fill="rgba(255, 255, 255, 0.05)" />
      
      <!-- Center Spindle Hole -->
      <circle cx="150" cy="150" r="10" fill="url(#grad-{idx})" />
      <circle cx="150" cy="150" r="4" fill="#0b0e17" />
      
      <!-- Genre Label Banner -->
      <text x="150" y="275" font-family="'Outfit', sans-serif" font-weight="800" font-size="12" fill="white" letter-spacing="3" text-anchor="middle" opacity="0.6">{genre_display}</text>
      
      <!-- Double Musical Note Icon -->
      <g transform="translate(138, 120) scale(0.9)" fill="white" opacity="0.85">
        <path d="M10 30 A 10 10 0 1 1 0 20 A 10 10 0 0 1 10 30 M35 25 A 10 10 0 1 1 25 15 A 10 10 0 0 1 35 25 M10 12 L10 30 M35 7 L35 25 M10 12 L35 7 L35 13 L10 18 Z"/>
      </g>
    </svg>"""
    
    # URL encode the SVG and return as a data url
    encoded_svg = urllib.parse.quote(svg.strip())
    return f"data:image/svg+xml,{encoded_svg}"

# Get Spotipy client if credentials are valid
def get_spotify_client():
    if not Config.SPOTIFY_CLIENT_ID or not Config.SPOTIFY_CLIENT_SECRET:
        return None
    if "YOUR_CLIENT_ID" in Config.SPOTIFY_CLIENT_ID or "YOUR_CLIENT_SECRET" in Config.SPOTIFY_CLIENT_SECRET:
        return None
    try:
        auth_manager = SpotifyClientCredentials(
            client_id=Config.SPOTIFY_CLIENT_ID,
            client_secret=Config.SPOTIFY_CLIENT_SECRET
        )
        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        print(f"Failed to authenticate with Spotify API: {e}")
        return None

def get_artist_image(artist_name):
    # Check cache first
    cache_key = f"artist_img:::{artist_name.lower()}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        if cached.startswith("https://") or not get_spotify_client():
            return cached
        
    image_url = None
    sp = get_spotify_client()
    if sp:
        try:
            results = sp.search(q=f"artist:\"{artist_name}\"", type="artist", limit=1)
            if results['artists']['items']:
                artist_data = results['artists']['items'][0]
                if artist_data['images']:
                    image_url = artist_data['images'][0]['url']
        except Exception as e:
            print(f"Spotify artist lookup error for '{artist_name}': {e}")
            
    if not image_url:
        # Fallback SVG initial circle cover
        image_url = generate_gradient_cover(artist_name, "Artist")
        
    _cache[cache_key] = image_url
    save_cache(_cache)
    return image_url

def get_song_details(song_name, artist_name="", genre=""):
    # Check cache first
    cache_key = f"{song_name.lower()}:::{artist_name.lower()}"
    if cache_key in _cache:
        cached = _cache[cache_key]
        if cached.get("image", "").startswith("https://") or not get_spotify_client():
            return cached
        
    details = {
        "song": song_name,
        "artist": artist_name if artist_name else "Unknown Artist",
        "album": genre.capitalize() if genre else "Single",
        "image": generate_gradient_cover(song_name, genre),
        "preview": None
    }
    
    sp = get_spotify_client()
    if sp:
        try:
            # Query Spotify
            query = f"track:\"{song_name}\""
            if artist_name:
                query += f" artist:\"{artist_name}\""
            
            results = sp.search(q=query, limit=1)
            
            # If not found with strict filter, search broadly
            if not results['tracks']['items']:
                results = sp.search(q=f"{song_name} {artist_name}", limit=1)
                
            if results['tracks']['items']:
                track = results['tracks']['items'][0]
                
                # Extract image
                image_url = details["image"]
                if track['album']['images']:
                    image_url = track['album']['images'][0]['url']
                
                details = {
                    "song": track['name'],
                    "artist": track['artists'][0]['name'],
                    "album": track['album']['name'],
                    "image": image_url,
                    "preview": track.get('preview_url')
                }
        except Exception as e:
            print(f"Spotify lookup error for '{song_name}': {e}")
            
    # Cache details
    _cache[cache_key] = details
    save_cache(_cache)
    return details
