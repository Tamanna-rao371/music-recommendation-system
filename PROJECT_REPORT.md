# ■ TuneSphere AI - Music Recommendation System
### Comprehensive Project Report: Technical Architecture, Machine Learning Pipeline & Deployment

---

<div align="center">

| Attribute | Details |
| :--- | :--- |
| **Live Application URL** | [https://tunesphere-ai.onrender.com/](https://tunesphere-ai.onrender.com/) |
| **GitHub Repository** | [https://github.com/Tamanna-rao371/music-recommendation-system](https://github.com/Tamanna-rao371/music-recommendation-system) |
| **Project Author** | **Tamanna Rao** (Production Build v1.0 \| September 2026) |

</div>

---

## 1. Project Overview

**TuneSphere AI** is a high-performance content-based music recommendation platform. Built using **Python**, **Flask**, **Scikit-Learn**, and the **Spotify Web API**, the application processes metadata and acoustic dimensions across **15,000 tracks** from the Spotify dataset to provide instant, personalized song recommendations.

Unlike basic recommendation projects, TuneSphere AI features a **Hybrid 3,006-Dimensional Latent Space** (combining 1.8x-weighted artist and genre tags with normalized 6D audio vectors), **4 Dynamic Inference Strategies** (Balanced, Serendipity, High Energy, and Acoustic Depth), real-time search autocomplete with sub-millisecond fuzzy matching, mood-targeted psychological valence filtering, and a **Robust Offline Mode** that guarantees zero network latency even when external API connectivity is unavailable.

---

## 2. Complete Tech Stack

| Category | Technologies & Libraries | Purpose / Role in Project |
| :--- | :--- | :--- |
| **Frontend & UI** | Jinja2, HTML5, CSS3, JavaScript (Vanilla ES6) | Responsive dark-slate UI, SVG acoustic radar visualizations, dynamic vinyl artwork, real-time debounce autocomplete. |
| **Web Framework** | Flask 3.0, Werkzeug, Gunicorn | Production WSGI backend, RESTful endpoint routing, session management, CSRF-safe forms, and JSON API payloads. |
| **Machine Learning** | Scikit-Learn (`CountVectorizer`, `cosine_similarity`) | Computes sparse metadata tag vectors (3,000 features scaled 1.8x) and computes sub-3ms cosine similarity vectors. |
| **Vector Math** | SciPy (`csr_matrix`, `hstack`), NumPy, Pandas | Sparse matrix operations, horizontal feature concatenation into 3,006-D latent space, and dataset cleaning. |
| **Data Management** | SQLite3, JSON, CSV | Persistent favorites tracking, custom playlist management with CSV/JSON exports, and Spotify cache persistence. |
| **API & Networking** | Spotipy (Spotify Web API), Requests, Python-Dotenv | Spotify metadata querying, 0-ms local album art caching (`spotify_cache.json`), and secret resolution. |
| **Deployment** | Render Cloud, GitHub, Git | Cloud hosting, dynamic `$PORT` binding, worker process management, and zero-downtime deployment setup. |

---

## 3. How It Works (System Architecture & Pipeline)

The TuneSphere AI system operates in four core stages: **Data Preprocessing & Entity Normalization**, **Hybrid Latent Space & Cosine Similarity**, **Dynamic Inference & Strategy Ranking**, and **Explainable Audio Feature Extraction**.

### Stage 1: Preprocessing & Entity Normalization
1. Ingests 15,000 tracks from `dataset/songs.csv` containing track names, artist, genre, popularity, and 5 acoustic dimensions.
2. Cleans text attributes, handles missing fields (imputing 'Pop' for null genres), filters special characters, and deduplicates identical `(song, artist)` pairs.
3. Synthesizes dense composite metadata tokens by concatenating normalized artist and genre attributes (`artist + " " + genre`).
4. Applies `MinMaxScaler` across 6 continuous audio dimensions (popularity, danceability, energy, valence, acousticness, tempo) to map all values uniformly into $[0.0, 1.0]$.

### Stage 2: Hybrid Latent Space & Cosine Similarity
The system extracts 3,000 distinct text features and combines them with normalized audio vectors:
- **`CountVectorizer` Engine**: Extracts top 3,000 n-gram metadata tokens and scales text weight by 1.8x to establish foundational genre identity.
- **6D Audio Matrix**: Converts normalized acoustic dimensions to `csr_matrix` and concatenates horizontally via `scipy.sparse.hstack` to form a 3,006-D space.

Similarity between query track vector $A$ and catalog vector $B$ is computed via standard cosine metric:
$$\text{Cosine Similarity}(A, B) = \frac{A \cdot B}{\|A\| \times \|B\|}$$

### Stage 3: Dynamic Inference & Strategy Ranking
When a user selects a song, TuneSphere queries the top 300 nearest neighbors in vector space and dynamically re-ranks them using 4 selectable strategies:
- **Balanced (Default)**: Pure cosine similarity across metadata tags and normalized audio metrics ($S_{\text{final}} = S_{\text{cosine}}$).
- **Discovery / Serendipity**: Penalizes mainstream popularity bias ($S_{\text{final}} = 0.65 \cdot S_{\text{cosine}} + 0.35 \cdot (1.0 - \text{Pop}_{\text{norm}})$) to surface indie gems.
- **High Energy**: Blends cosine similarity with energy and tempo congruence ($S_{\text{final}} = 0.55 \cdot S_{\text{cosine}} + 0.30 \cdot (1 - |\Delta\text{Energy}|) + 0.15 \cdot (1 - |\Delta\text{Tempo}|)$).
- **Acoustic Depth**: Prioritizes organic acoustic instrumentation and timbre ($S_{\text{final}} = 0.60 \cdot S_{\text{cosine}} + 0.40 \cdot (1 - |\Delta\text{Acousticness}|)$).

---

## 4. Key Innovations & Standout Features

- 🧠 **Hybrid 3,006-D Latent Space**: Combines 3,000 NLP text features (1.8x weighted) with 6 normalized acoustic dimensions for high-fidelity sonic matching.
- ⚡ **4 Dynamic Inference Strategies**: Enables live user switching between Balanced, Serendipity (anti-popularity), High Energy, and Acoustic Depth.
- 🔍 **Real-Time Autocomplete Search**: Instant sub-millisecond search suggestions powered by client-side debounce and server-side fuzzy string matching (`difflib`).
- 🎭 **Mood & Vibe Vector Matcher**: Directly filters tracks matching psychological valence and energy zones (*Happy*, *Workout*, *Chill*, *Party*, *Melancholy*, *Romantic*).
- 📶 **Robust Offline Mode & Instant Fallback**: Zero external API dependencies required for core functionality; generates inline vinyl gradient art if Spotify is unreachable.
- 🖼️ **Curated Spotify Album Covers & Smart Caching**: Connects to Spotify Web API with local cache (`spotify_cache.json`) for 0-ms instant poster rendering.
- 📂 **Full-Featured Playlist Suite & SQLite Favorites**: Relational database storage for user bookmarks with complete acoustic radar signatures and CSV/JSON playlist exports.

---

## 5. Render Cloud Automatic Deployment Mechanics

Deploying ML recommendation models with high-dimensional feature spaces on cloud PaaS environments (like Render) presents unique challenges with memory limits and port resolution. TuneSphere AI solves this cleanly with an in-memory sparse compilation workflow and dynamic binding:

```python
# Render Dynamic Port Binding & Production Execution (app.py)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Model Pipeline Benchmark (model_builder.py)
# Combined feature space: (15000, 3006) | Cosine similarity inference latency: 2.72 ms
similarity_scores = cosine_similarity(song_vector, X_combined).flatten()
top_indices = similarity_scores.argsort()[::-1][1:7]
```

### Deployment Benefits:
1. **Zero Cold-Start Pre-Compilation**: The hybrid sparse matrix is constructed in memory at startup in ~1.8 seconds, eliminating external disk I/O bottlenecks and preventing large 200MB+ binary model files from cluttering the Git repository.
2. **Sub-3ms Inference Latency**: Utilizing `scipy.sparse.csr_matrix` and Scikit-Learn vectorized C-level matrix multiplications achieves instantaneous recommendation response times (<3 ms) on budget cloud hardware (Render 512MB RAM free tier).
3. **Zero Hardcoded Secrets**: Resolves Spotify Web API client credentials securely via environment variables (`SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`) while maintaining crash-proof offline fallback operation if unconfigured.

---

## 6. Project Repository & Live Deployment Links

| Resource | Link / Access Path |
| :--- | :--- |
| **Live Render Application** | [https://tunesphere-ai.onrender.com/](https://tunesphere-ai.onrender.com/) |
| **GitHub Repository** | [https://github.com/Tamanna-rao371/music-recommendation-system](https://github.com/Tamanna-rao371/music-recommendation-system) |
| **Deployment Status** | `READY FOR RENDER CLOUD DEPLOYMENT (LIVE)` |
| **Verification & Benchmark** | `python model_builder.py` (15,000 Tracks Verified \| 2.72 ms Latency) |

---
*Author: Tamanna Rao \| Render & GitHub Documentation \| Build v1.0*
