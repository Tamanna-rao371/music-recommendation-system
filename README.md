# TuneSphere AI - Music Recommendation System 🎵

<div align="center">

[![Live Demo](https://img.shields.io/badge/🚀_Live_Demo-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://tunesphere-ai.onrender.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Spotify API](https://img.shields.io/badge/Spotify_API-1DB954?style=for-the-badge&logo=spotify&logoColor=white)](https://developer.spotify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple?style=for-the-badge)](LICENSE)

### 🌐 **Live Web Application**: [https://tunesphere-ai.onrender.com/](https://tunesphere-ai.onrender.com/)

</div>

---

# Project Overview
**TuneSphere AI** is a production-grade, content-based music recommendation platform built with **Python**, **Flask**, **Scikit-Learn**, and the **Spotify Web API**. It combines natural language text vectorization with normalized 6-dimensional acoustic latent vectors (danceability, energy, valence, acousticness, tempo, and popularity) to compute high-precision cosine similarities across a catalog of **15,000+ tracks** in under **3 milliseconds**.

The application features a simple, modern dark-slate user interface, 4 dynamic inference strategies, real-time search autocomplete, targeted mood query matching, personalized playlist management with CSV/JSON exports, and robust offline fallback support.

---

# Features
- **🧠 Hybrid Vectorization Engine**: Combines metadata tokens (artist + genre) with normalized numerical audio vectors to calculate cosine similarity across a hybrid 3,006-dimensional sparse latent space.
- **⚡ 4 Dynamic Inference Strategies**:
  - **Balanced (Default)**: Pure cosine similarity across metadata tags and normalized audio metrics.
  - **Discovery / Serendipity**: Dampens popularity bias to discover hidden gems and lesser-known indie tracks.
  - **High Energy**: Boosts tracks with aggressive energy and fast tempo (BPM).
  - **Acoustic Depth**: Emphasizes organic timbre, acoustic instrumentation, and softer acoustics.
- **🔍 Real-Time Autocomplete Search**: Sub-millisecond fuzzy query matching with instant drop-down suggestions as you type.
- **🎭 Mood & Vibe Vector Matcher**: Query music by psychological valence and energy bounds (*Happy*, *Workout*, *Chill*, *Party*, *Melancholy*, *Romantic*).
- **📶 Robust Offline Mode & Curated Fallbacks**: If Spotify API credentials are not provided or rate-limited, the system automatically uses inline dynamic vinyl gradient artwork and offline metadata from `dataset/songs.csv` without network timeouts or crashes.
- **🖼️ Curated Spotify Album Covers**: Connects to the Spotify Web API via Spotipy with smart local caching (`spotify_cache.json`) for instant (0 ms) rendering of official album artwork and artist photos.
- **📂 Complete Playlist Management**: Create, curate, and export custom playlists to CSV and JSON formats.
- **❤️ Rich Favorites System**: Bookmarks songs to an SQLite database with title, artist, genre, and artwork metadata.
- **📊 Detailed Track Intelligence**: Inspect Danceability, Energy, Mood/Valence, Acousticness, and Tempo signatures with clean interactive progress meters.
- **🎨 Simple, Clean Modern UI**: Distraction-free, responsive dark-themed interface designed for simplicity, elegance, and speed.

---

# Tech Stack
- **Core Languages**: Python 3
- **Web Framework**: Flask 3.0
- **Machine Learning & Vector Math**: Scikit-Learn (`CountVectorizer`, `cosine_similarity`), SciPy (`csr_matrix`, `hstack`), NumPy, Pandas
- **Database**: SQLite3
- **API Request Handling**: Spotipy (Spotify Web API), Requests, Python-dotenv
- **Production Server**: Gunicorn
- **Deployment Platform**: Render ([Live Link](https://tunesphere-ai.onrender.com/))

---

# Screenshots

### Branding Logo
![TuneSphere Logo](assets/logo.png)

*(Place your application screenshots in `assets/screenshots/` and update paths below)*
- **Main Recommendation Dashboard & Search**: `assets/screenshots/dashboard.png`
- **Song Details & Acoustic Feature Signatures**: `assets/screenshots/song_details.png`
- **Playlist Manager & Data Export**: `assets/screenshots/playlists.png`

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

> [!NOTE]
> `model_builder.py` validates the dataset integrity, fits the 3,000-feature `CountVectorizer`, normalizes the 6D audio vector space, and benchmarks inference latency (~2.7 ms) on sample queries.

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

---

# Environment Variables

The application supports secure, production-safe API key resolution. 

Create a `.env` file in the root directory (you can copy `.env.example` as a template):
```env
# Spotify Web API Credentials (Optional - for live album art and artist metadata)
SPOTIPY_CLIENT_ID=your_spotify_client_id_here
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret_here

# Flask Application Secret Key
FLASK_SECRET_KEY=your_secret_key_here

# Dataset Configuration
DATASET_PATH=dataset/songs.csv
CATALOG_SIZE=15000
```

*(If no credentials are provided, TuneSphere automatically runs in Offline Mode using built-in high-resolution gradient vinyl artwork without crashing).*

### Cloud Deployment (Render)
When deploying to Render, set these under **Environment Variables** in the Render Dashboard:
- `SPOTIPY_CLIENT_ID`
- `SPOTIPY_CLIENT_SECRET`
- `FLASK_SECRET_KEY`

---

# Project Structure
```text
music-recommendation-system/
├── assets/                     # Custom assets, logos & screenshots
│   ├── logo.png                # TuneSphere AI branding logo
│   └── screenshots/            # UI screenshots
│
├── dataset/                    # Track catalog
│   └── songs.csv               # 15,000 track music dataset
│
├── static/                     # Frontend styling & scripts
│   ├── style.css               # Clean modern design system
│   └── script.js               # Autocomplete & UI interactions
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Main recommendation dashboard
│   ├── song_details.html       # Track metrics & signatures
│   ├── playlists.html          # Playlist collection overview
│   └── playlist_view.html      # Playlist track table & export
│
├── utils/                      # Modular backend packages
│   ├── __init__.py             # Package initializer
│   ├── recommender.py          # Hybrid ML recommendation engine
│   ├── api.py                  # Spotify metadata & artwork handler
│   └── database.py             # SQLite database management
│
├── .env.example                # Sample environment variables template
├── .gitignore                  # Git tracking exclusion rules
├── app.py                      # Main Flask application entrypoint
├── config.py                   # App configuration & settings
├── model_builder.py            # ML pipeline verification & benchmark
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

# Future Improvements
1. **👥 Collaborative Filtering**: Incorporate user listening session matrix factorization (SVD / Implicit Alternating Least Squares) to blend collaborative user signals with acoustic content.
2. **🔐 User Authentication**: Support multi-user accounts and auth (OAuth2, Firebase) to sync playlists and favorites to a cloud database (PostgreSQL/Supabase).
3. **💬 Sentiment Analysis**: Process live lyrics and user comments using NLP (BERT/VADER) to score and filter recommended titles.
4. **📈 Audio Spectrogram Analysis**: Integrate Librosa for audio waveform feature extraction directly from user MP3 uploads.

---

# Author
**Tamanna Rao**  
- **GitHub**: [@Tamanna-rao371](https://github.com/Tamanna-rao371)  
- **Live Demo**: [https://tunesphere-ai.onrender.com/](https://tunesphere-ai.onrender.com/)

---

# License
This project is open source and available under the [MIT License](LICENSE).
