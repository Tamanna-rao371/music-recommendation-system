# TuneSphere AI - Music Recommendation System

# Project Overview
**TuneSphere AI** is a content-based music recommendation engine built with **Python**, **Flask**, **Scikit-Learn**, and a modern, responsive user interface. It leverages metadata text vectorization and normalized 6D acoustic features (danceability, energy, valence, acousticness, tempo, and popularity) to deliver accurate, real-time song recommendations across a catalog of 15,000+ tracks.

---

# Features
- **🧠 Hybrid Vectorization Engine**: Combines metadata tags (artist + genre) with normalized audio vectors to compute cosine similarity across an 8-dimensional feature space.
- **⚡ Multiple Inference Strategies**:
  - **Balanced (Default)**: Standard cosine similarity across tags and audio vectors.
  - **Discovery / Serendipity**: Surfaces lesser-known indie gems by dampening popularity bias.
  - **High Energy**: Prioritizes higher tempo and high-energy acoustic matches.
  - **Acoustic**: Focuses on organic acoustic timbre and acoustic instruments.
- **🔍 Real-Time Autocomplete Search**: Interactive search input updates matching tracks instantly as you type.
- **🎭 Mood & Vibe Vector Matcher**: Query music by psychological valence and energy bounds (Happy, Workout, Chill, Party, Melancholy, Romantic).
- **📂 Playlist Management**: Create, curate, and export custom playlists to CSV and JSON formats.
- **⭐ Favorites System**: Bookmark songs with a single click and access them anytime.
- **📊 Detailed Track Intelligence**: Inspect Danceability, Energy, Valence (Mood), Acousticness, and Tempo signatures for any track.
- **🎨 Simple, Clean Modern UI**: Distraction-free, responsive dark-themed interface designed for simplicity and speed.

---

# Tech Stack
- **Core Language**: Python 3
- **Web Framework**: Flask
- **Machine Learning & Data**: Scikit-Learn (`CountVectorizer`, `cosine_similarity`), Pandas, NumPy, SciPy
- **Frontend**: HTML5, CSS3 (Custom responsive design system), Vanilla JavaScript
- **APIs**: Spotify Web API integration (via Spotipy) with curated fallback vinyl gradient art

---

# Screenshots

### Branding Logo
![TuneSphere Logo](assets/logo.png)

*(Place your application screenshots in `assets/screenshots/`)*
- **Dashboard & Search Suggestions**: `assets/screenshots/dashboard.png`
- **Song Details & Audio Signatures**: `assets/screenshots/song_details.png`
- **Playlists & Exports**: `assets/screenshots/playlists.png`

---

# Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Tamanna-rao371/music-recommendation-system.git
cd music-recommendation-system
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# On Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify & Benchmark ML Pipeline
Run the model builder script to validate dataset preprocessing, feature normalization, and recommendation latency:
```bash
python model_builder.py
```

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

# Environment Variables
The application supports optional Spotify API credentials for fetching live album art and artist metadata.

Create a `.env` file in the root directory (you can copy `.env.example` as a template):
```env
SPOTIPY_CLIENT_ID=your_spotify_client_id_here
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret_here
FLASK_SECRET_KEY=your_secret_key_here
```
*(If no credentials are provided, TuneSphere automatically uses built-in high-resolution gradient vinyl artwork without crashing).*

---

# Project Structure
```text
music-recommendation-system/
├── assets/                     # Custom assets, logos & screenshots
│   ├── logo.png                # TuneSphere AI branding logo
│   └── screenshots/            # UI screenshots
├── dataset/                    # Track catalog
│   └── songs.csv               # 15,000 track music dataset
├── static/                     # Frontend styling & scripts
│   ├── style.css               # Clean modern design system
│   └── script.js               # Autocomplete & UI interactions
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Main recommendation dashboard
│   ├── song_details.html       # Track metrics & signatures
│   ├── playlists.html          # Playlist collection overview
│   └── playlist_view.html      # Playlist track table & export
├── utils/                      # Modular backend packages
│   ├── __init__.py             # Package initializer
│   ├── recommender.py          # Hybrid recommendation engine
│   ├── api.py                  # Spotify metadata & artwork handler
│   └── database.py             # SQLite database management
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignored files & directories
├── app.py                      # Main Flask application entrypoint
├── config.py                   # App configuration & settings
├── model_builder.py            # ML pipeline verification & benchmark
└── requirements.txt            # Python dependencies
```

---

# License
This project is open source and available under the [MIT License](LICENSE).
