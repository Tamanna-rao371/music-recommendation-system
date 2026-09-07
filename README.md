# TuneSphere AI - Music Recommendation System 🎵

TuneSphere AI is an intelligent, content-based music recommendation engine built with Python, Flask, scikit-learn, and a clean, responsive modern UI. It leverages natural language text features and normalized acoustic vectors (danceability, energy, valence, acousticness, tempo) to recommend matching songs from a catalog of 15,000+ tracks.

---

## ✨ Features

- **Hybrid Content-Based Filtering**: Combines metadata tags (artist, genre) with normalized audio features to compute cosine similarity across an 8-dimensional space.
- **Inference Strategies**:
  - **Balanced**: Standard cosine similarity across tags and audio vectors.
  - **Discovery / Serendipity**: Surfaces lesser-known indie tracks by dampening popularity bias.
  - **High Energy**: Prioritizes higher tempo and high-energy tracks.
  - **Acoustic**: Focuses on organic acoustic timbre.
- **Interactive Search & Autocomplete**: Real-time track suggestions as you type.
- **Mood & Vibe Vector Matcher**: Query music by targeted mood bounds (Happy, Workout, Chill, Party, Melancholy, Romantic).
- **Personalized Playlists**: Create, manage, and export custom playlists to CSV and JSON formats.
- **Favorites & History**: Save favorite tracks with single-click bookmarking.
- **Detailed Song Intelligence**: Inspect danceability, energy, mood/valence, acousticness, and BPM signatures for each track.
- **Clean & Simple Dark UI**: Responsive single-column interface with zero clutter.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, SQLite
- **Machine Learning**: scikit-learn (`CountVectorizer`, `cosine_similarity`), pandas, numpy
- **Frontend**: HTML5, CSS3 (Modern custom design system), Vanilla JavaScript
- **APIs**: Spotify Web API integration (via Spotipy) with fallback gradient art generation

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/Tamanna-rao371/music-recommendation-system.git
cd music-recommendation-system
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Configure Spotify API Credentials
To fetch live Spotify album covers and artist images, create a `.env` file in the root directory:
```env
FLASK_SECRET_KEY=your_secret_key_here
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
```
*(If omitted, TuneSphere automatically uses high-resolution gradient vinyl artwork generation.)*

### 5. Run the application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 📁 Project Structure

```
music-recommendation-system/
├── app.py                     # Flask application routes and controllers
├── recommendation_engine.py   # Hybrid ML recommendation engine
├── spotify_api.py             # Spotify metadata & artwork handler
├── database.py                # SQLite database management
├── config.py                  # Application configuration
├── requirements.txt           # Python dependencies
├── dataset/
│   └── songs.csv              # Track catalog dataset (15,000 tracks)
├── static/
│   ├── style.css              # Clean, modern design system
│   └── script.js              # Autocomplete and UI interactions
└── templates/
    ├── index.html             # Main recommendation dashboard
    ├── song_details.html      # Track intelligence & metrics
    ├── playlists.html         # User playlists overview
    └── playlist_view.html     # Playlist track listing & exports
```

---

## 📄 License
This project is open source and available under the [MIT License](LICENSE).
