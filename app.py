from flask import Flask, render_template, request, session, redirect, url_for, jsonify, Response
import pandas as pd
from config import Config
import database
import spotify_api
from recommendation_engine import engine

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize Database on Startup
database.init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    # Load basic catalogs for filters & dropdowns
    unique_genres = engine.get_unique_genres()
    all_song_names = engine.get_all_songs()
    
    recommendations = []
    selected_song = session.get("selected_song", None)
    search_query = ""
    
    # Check if filters, explicit seed, or strategy tuning is applied
    active_mood = request.args.get("mood", "").strip()
    active_genre = request.args.get("genre_filter", "").strip()
    active_artist = request.args.get("artist_filter", "").strip()
    active_strategy = request.args.get("strategy", "balanced").strip().lower()
    if active_strategy not in ["balanced", "serendipity", "energy", "acoustic"]:
        active_strategy = "balanced"
    try:
        active_limit = int(request.args.get("limit", 6))
        if active_limit not in [6, 12, 18]:
            active_limit = 6
    except ValueError:
        active_limit = 6
    seed_param = request.args.get("seed", "").strip()

    def format_recommendations(recs_list):
        formatted = []
        for i, r in enumerate(recs_list, 1):
            details = spotify_api.get_song_details(r["song"], r.get("artist", ""), r.get("genre", ""))
            details["rank_index"] = r.get("rank_index", f"{i:02d}")
            details["confidence"] = r.get("confidence", 85)
            details["cosine_score"] = r.get("cosine_score", round(r.get("confidence", 85) / 100.0, 4))
            details["explanation"] = r.get("explanation", "Recommended based on overall cosine similarity.")
            details["strategy"] = r.get("strategy", active_strategy)
            details["genre"] = r.get("genre", "Pop")
            details["danceability"] = int(r.get("danceability", 0.5) * 100)
            details["energy"] = int(r.get("energy", 0.5) * 100)
            details["valence"] = int(r.get("valence", 0.5) * 100)
            details["acousticness"] = int(r.get("acousticness", 0.5) * 100)
            details["tempo"] = int(r.get("tempo", 120))
            details["popularity"] = int(r.get("popularity", 50))
            formatted.append(details)
        return formatted

    # Get consistently ranked trending list (top 8 popular songs in the catalog)
    trending_list = []
    if engine.is_loaded:
        top_songs = engine.catalog.sort_values(by='popularity', ascending=False).head(8)
        for _, row in top_songs.iterrows():
            details = spotify_api.get_song_details(row['song'], row['artist'], row['genre'])
            details["genre"] = row['genre']
            trending_list.append(details)

    # ---------------------------------------------
    # POST METHOD (Search or Direct Action)
    # ---------------------------------------------
    if request.method == "POST":
        search_query = request.form.get("song", "").strip()
        if search_query:
            database.add_search(search_query)
            session["last_search_query"] = search_query
            
            matched_song = engine.fuzzy_match_song(search_query)
            if matched_song:
                recs = engine.recommend(
                    matched_song, 
                    genre_filter=active_genre if active_genre else None,
                    artist_filter=active_artist if active_artist else None,
                    strategy=active_strategy,
                    limit=active_limit
                )
                recommendations = format_recommendations(recs)
                session["last_recommendations"] = recommendations
                session["last_searched_song"] = matched_song
                session.modified = True
            else:
                recommendations = []
                session["last_recommendations"] = []
                session["last_searched_song"] = None
                session.modified = True
                
    # ---------------------------------------------
    # GET METHOD (Load Dashboard, Apply Filters, Re-Seed)
    # ---------------------------------------------
    else:
        if seed_param:
            matched_seed = engine.fuzzy_match_song(seed_param)
            if matched_seed:
                database.add_search(matched_seed)
                session["last_searched_song"] = matched_seed
                session["last_search_query"] = matched_seed
                session.modified = True
                search_query = matched_seed
                recs = engine.recommend(
                    matched_seed,
                    genre_filter=active_genre if active_genre else None,
                    artist_filter=active_artist if active_artist else None,
                    strategy=active_strategy,
                    limit=active_limit
                )
                recommendations = format_recommendations(recs)
                session["last_recommendations"] = recommendations

        if not recommendations:
            last_searched = session.get("last_searched_song")
            search_query = session.get("last_search_query", "")
            
            if active_mood:
                mood_songs = engine.recommend_by_mood(active_mood)
                recommendations = format_recommendations(mood_songs)
            elif last_searched:
                recs = engine.recommend(
                    last_searched, 
                    genre_filter=active_genre if active_genre else None,
                    artist_filter=active_artist if active_artist else None,
                    strategy=active_strategy,
                    limit=active_limit
                )
                recommendations = format_recommendations(recs)
            else:
                # Default to top catalog track as initial seed so recommender is never empty
                default_seed = trending_list[0]['song'] if trending_list else "Believer"
                session["last_searched_song"] = default_seed
                session["last_search_query"] = default_seed
                search_query = default_seed
                recs = engine.recommend(
                    default_seed,
                    genre_filter=active_genre if active_genre else None,
                    artist_filter=active_artist if active_artist else None,
                    strategy=active_strategy,
                    limit=active_limit
                )
                recommendations = format_recommendations(recs)
                session["last_recommendations"] = recommendations
                session.modified = True

    # Compute Active Seed Song Vector Information for comparison
    active_seed = session.get("last_searched_song")
    seed_song_info = None
    seed_radar_data = None
    if active_seed:
        seed_raw = engine.get_song_info(active_seed)
        if seed_raw:
            seed_details = spotify_api.get_song_details(seed_raw["song"], seed_raw.get("artist", ""), seed_raw.get("genre", ""))
            seed_details["genre"] = seed_raw.get("genre", "Pop")
            seed_details["danceability"] = int(seed_raw.get("danceability", 0.5) * 100)
            seed_details["energy"] = int(seed_raw.get("energy", 0.5) * 100)
            seed_details["valence"] = int(seed_raw.get("valence", 0.5) * 100)
            seed_details["acousticness"] = int(seed_raw.get("acousticness", 0.5) * 100)
            seed_details["tempo"] = int(seed_raw.get("tempo", 120))
            seed_details["popularity"] = int(seed_raw.get("popularity", 50))
            seed_song_info = seed_details
            seed_radar_data = engine.get_vector_radar_data(active_seed)

    # Curated Quick Seeds for fast exploration
    quick_seeds = ["Believer", "Shape of You", "Starboy", "Blinding Lights", "Closer", "Bad Guy"]

    # Recommender System Engine Metadata
    engine_stats = {
        "model": "Hybrid Vector Embedding (CountVec + Norm Audio)",
        "version": "v2.4-Production",
        "metric": "Cosine Similarity (L2 Normalized)",
        "dimensions": "8 Dimensions (Tags + Audio)",
        "tracks_indexed": len(engine.catalog) if engine.is_loaded else 15000,
        "latency_ms": "< 6 ms",
        "strategy": active_strategy.capitalize(),
        "limit": active_limit
    }

    # Dynamic Top Artists
    artists_raw = engine.get_dynamic_top_artists(limit=5)
    popular_artists = []
    for a in artists_raw:
        img_url = spotify_api.get_artist_image(a["name"])
        popular_artists.append({
            "name": a["name"],
            "image": img_url,
            "tracks_count": a["tracks_count"],
            "popularity": a["popularity"]
        })

    # Fetch lists from database
    favorites = database.get_favorites()
    play_history = database.get_history(limit=8)
    search_history = database.get_search_history(limit=6)
    playlists = database.get_playlists()
    stats = database.get_dashboard_stats()

    # Highlight active sidebar route
    active_tab = "recommender"
    if active_mood:
        active_tab = "moods"

    return render_template(
        "index.html",
        songs=all_song_names,
        genres=unique_genres,
        recommendations=recommendations,
        trending=trending_list,
        favorites=favorites,
        history=play_history,
        search_history=search_history,
        playlists=playlists,
        stats=stats,
        selected_song=selected_song,
        search_query=search_query,
        active_tab=active_tab,
        active_mood=active_mood,
        active_genre=active_genre,
        active_artist=active_artist,
        active_strategy=active_strategy,
        active_limit=active_limit,
        seed_song_info=seed_song_info,
        seed_radar_data=seed_radar_data,
        quick_seeds=quick_seeds,
        engine_stats=engine_stats,
        popular_artists=popular_artists
    )

# ---------------------------------------------
# Favorites Routes
# ---------------------------------------------

@app.route("/favorite/<song>")
def favorite(song):
    artist = request.args.get("artist", "")
    genre = request.args.get("genre", "")
    
    # Get details
    details = spotify_api.get_song_details(song, artist, genre)
    
    # Add to SQLite DB
    database.add_favorite(details["song"], details["artist"], genre, details["image"], details["preview"])
    
    referrer = request.referrer or "/"
    return redirect(referrer)

@app.route("/remove_favorite/<song>")
def remove_favorite(song):
    # Remove from SQLite DB
    database.remove_favorite(song)
    
    referrer = request.referrer or "/"
    return redirect(referrer)

# ---------------------------------------------
# Playback Route
# ---------------------------------------------

@app.route("/play/<song>")
def play(song):
    artist = request.args.get("artist", "")
    return redirect(url_for("song_details", song=song, artist=artist))

# ---------------------------------------------
# Song Details Route
# ---------------------------------------------

@app.route("/song/<song>")
def song_details(song):
    artist = request.args.get("artist", "")
    
    # Lookup info from catalog
    info = engine.get_song_info(song)
    genre = info["genre"] if info else ""
    
    details = spotify_api.get_song_details(song, artist, genre)
    
    # Bind numerical metrics
    if info:
        details["popularity"] = info.get("popularity", 50)
        details["genre"] = info.get("genre", "Unknown")
        details["danceability"] = int(info.get("danceability", 0.0) * 100)
        details["energy"] = int(info.get("energy", 0.0) * 100)
        details["valence"] = int(info.get("valence", 0.0) * 100)
        details["acousticness"] = int(info.get("acousticness", 0.0) * 100)
        details["tempo"] = int(info.get("tempo", 120))
    else:
        details["popularity"] = 50
        details["genre"] = genre or "Unknown"
        details["danceability"] = 50
        details["energy"] = 50
        details["valence"] = 50
        details["acousticness"] = 50
        details["tempo"] = 120

    # Get recommendations for details page
    recs = engine.recommend(song, limit=6)
    detailed_recs = []
    for r in recs:
        rec_details = spotify_api.get_song_details(r["song"], r["artist"], r["genre"])
        rec_details["rank_index"] = r.get("rank_index", "01")
        rec_details["confidence"] = r["confidence"]
        rec_details["cosine_score"] = r.get("cosine_score", round(r["confidence"] / 100.0, 4))
        rec_details["explanation"] = r["explanation"]
        rec_details["genre"] = r["genre"]
        rec_details["danceability"] = int(r.get("danceability", 0.5) * 100)
        rec_details["energy"] = int(r.get("energy", 0.5) * 100)
        rec_details["valence"] = int(r.get("valence", 0.5) * 100)
        detailed_recs.append(rec_details)

    # Calculate 6D Vector Radar
    song_radar = engine.get_vector_radar_data(song)

    # Get playlists list for "Add to playlist" support
    playlists = database.get_playlists()
    
    # Load player track
    selected_song = session.get("selected_song", None)

    return render_template(
        "song_details.html",
        song=details,
        recommendations=detailed_recs,
        playlists=playlists,
        selected_song=selected_song,
        song_radar=song_radar
    )

# ---------------------------------------------
# Playlists Routes
# ---------------------------------------------

@app.route("/playlists", methods=["GET", "POST"])
def playlists():
    if request.method == "POST":
        # Create playlist
        name = request.form.get("name", "").strip()
        if name:
            database.create_playlist(name)
        return redirect(url_for("playlists"))
        
    playlists = database.get_playlists()
    selected_song = session.get("selected_song", None)
    
    # Get stats for dashboard
    stats = database.get_dashboard_stats()
    
    return render_template(
        "playlists.html",
        playlists=playlists,
        selected_song=selected_song,
        stats=stats,
        active_tab="playlists"
    )

@app.route("/playlists/<name>")
def playlist_view(name):
    playlist_songs = database.get_playlist_songs(name)
    all_playlists = database.get_playlists()
    selected_song = session.get("selected_song", None)
    
    return render_template(
        "playlist_view.html",
        playlist_name=name,
        songs=playlist_songs,
        playlists=all_playlists,
        selected_song=selected_song,
        active_tab="playlists"
    )

@app.route("/playlists/<name>/delete", methods=["POST"])
def playlist_delete(name):
    database.delete_playlist(name)
    return redirect(url_for("playlists"))

@app.route("/playlists/<name>/add/<song>")
def playlist_add_track(name, song):
    artist = request.args.get("artist", "")
    genre = request.args.get("genre", "")
    
    details = spotify_api.get_song_details(song, artist, genre)
    database.add_to_playlist(name, details["song"], details["artist"], genre, details["image"], details["preview"])
    
    referrer = request.referrer or "/"
    return redirect(referrer)

@app.route("/playlists/<name>/remove/<song>")
def playlist_remove_track(name, song):
    database.remove_from_playlist(name, song)
    referrer = request.referrer or "/"
    return redirect(referrer)

@app.route("/playlists/<name>/export/<file_format>")
def export_playlist(name, file_format):
    songs = database.get_playlist_songs(name)
    
    if file_format == "json":
        import json
        json_data = json.dumps(songs, indent=4)
        return Response(
            json_data,
            mimetype="application/json",
            headers={"Content-disposition": f"attachment; filename=playlist_{name}.json"}
        )
        
    elif file_format == "csv":
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Song", "Artist", "Genre", "Image URL", "Preview URL"])
        for s in songs:
            writer.writerow([s["song"], s["artist"], s["genre"], s["image"], s["preview"]])
            
        response = Response(
            output.getvalue(),
            mimetype="text/csv"
        )
        response.headers["Content-Disposition"] = f"attachment; filename=playlist_{name}.csv"
        return response
        
    return redirect(url_for("playlist_view", name=name))

# ---------------------------------------------
# API Endpoints
# ---------------------------------------------

@app.route("/api/search_suggestions")
def search_suggestions():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    suggestions = engine.get_search_suggestions(q, limit=6)
    return jsonify(suggestions)

@app.route("/api/vector_profile/<song>")
def api_vector_profile(song):
    profile = engine.get_vector_radar_data(song)
    if not profile:
        return jsonify({"error": "Track not found in vector space"}), 404
    return jsonify(profile)

# ---------------------------------------------
# Application Execution
# ---------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)