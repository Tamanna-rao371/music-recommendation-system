import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, hstack
import difflib
import random
import math
from config import Config

class RecommendationEngine:
    def __init__(self):
        self.catalog = None
        self.X_combined = None
        self.cv = None
        self.is_loaded = False
        self.initialize_engine()
        
    def initialize_engine(self):
        try:
            # 1. Load Dataset
            songs_df = pd.read_csv(Config.DATASET_PATH)
            
            # Clean columns and rename
            songs_df = songs_df.dropna(subset=['track_name', 'artist_name', 'genre'])
            
            # Rename to match our conventions
            songs_df = songs_df.rename(columns={
                'artist_name': 'artist',
                'track_name': 'song'
            })
            
            # Keep only English characters in track name for clean presentation
            songs_df = songs_df[songs_df['song'].str.contains('^[A-Za-z0-9 ]+$', regex=True, na=False)]
            
            # Drop duplicates based on song & artist
            songs_df = songs_df.drop_duplicates(subset=['song', 'artist'])
            
            # Take top N popular songs
            self.catalog = songs_df.sort_values(by='popularity', ascending=False).head(Config.CATALOG_SIZE).reset_index(drop=True)
            
            # 2. Normalize Numerical Features
            numerical_cols = ['popularity', 'danceability', 'energy', 'valence', 'acousticness', 'tempo']
            for col in numerical_cols:
                min_val = self.catalog[col].min()
                max_val = self.catalog[col].max()
                if max_val > min_val:
                    self.catalog[col + '_norm'] = (self.catalog[col] - min_val) / (max_val - min_val)
                else:
                    self.catalog[col + '_norm'] = 0.0
            
            # 3. Vectorize Text Features (Artist + Genre)
            self.catalog['tags'] = self.catalog['artist'] + " " + self.catalog['genre']
            self.cv = CountVectorizer(max_features=3000, stop_words='english')
            X_text = self.cv.fit_transform(self.catalog['tags'])
            
            # Apply weights: Text features represent 1.8x, numerical features 1.0x
            X_text_scaled = X_text * 1.8
            
            # Create numerical matrix
            norm_cols = [col + '_norm' for col in numerical_cols]
            X_num = self.catalog[norm_cols].values
            X_num_sparse = csr_matrix(X_num)
            
            # Combine matrices
            self.X_combined = hstack([X_text_scaled, X_num_sparse]).tocsr()
            
            self.is_loaded = True
            print(f"Recommendation engine successfully initialized with {len(self.catalog)} tracks.")
        except Exception as e:
            print(f"Error initializing recommendation engine: {e}")
            self.is_loaded = False
            
    def get_all_songs(self):
        if not self.is_loaded:
            return []
        return list(self.catalog['song'].values)
        
    def fuzzy_match_song(self, song_name):
        if not self.is_loaded or not song_name:
            return None
        
        song_name_lower = song_name.strip().lower()
        
        # Check exact matches case-insensitive first
        exact_matches = self.catalog[self.catalog['song'].str.lower() == song_name_lower]
        if not exact_matches.empty:
            return exact_matches.iloc[0]['song']
            
        # Try starts-with matches
        starts_matches = self.catalog[self.catalog['song'].str.lower().str.startswith(song_name_lower)]
        if not starts_matches.empty:
            return starts_matches.iloc[0]['song']
            
        # Use difflib for fuzzy match
        song_list = self.catalog['song'].tolist()
        close_matches = difflib.get_close_matches(song_name, song_list, n=1, cutoff=0.5)
        if close_matches:
            return close_matches[0]
            
        return None

    def get_song_info(self, song_name):
        if not self.is_loaded:
            return None
        matched_song = self.fuzzy_match_song(song_name)
        if not matched_song:
            return None
        row = self.catalog[self.catalog['song'] == matched_song].iloc[0]
        return dict(row)

    def generate_explanation(self, seed, target):
        """Generates natural language description for the recommendation reason"""
        if seed['artist'] == target['artist']:
            return f"Recommended because you listened to other tracks by {seed['artist']}."
            
        if seed['genre'] == target['genre']:
            # Compare popularity or fallback
            return f"Recommended because you listened to similar {seed['genre']} songs by {seed['artist']}."
            
        # Compare numerical properties to find the strongest similarity driver
        # Energy
        if abs(seed['energy'] - target['energy']) < 0.15:
            if seed['energy'] > 0.65:
                return f"Recommended because this song matches the high energy and tempo of {seed['song']}."
            elif seed['energy'] < 0.35:
                return f"Recommended because this matches the mellow, calm energy of {seed['song']}."
                
        # Acousticness
        if abs(seed['acousticness'] - target['acousticness']) < 0.15 and seed['acousticness'] > 0.5:
            return f"Recommended because this matches the acoustic, unplugged feel of {seed['song']}."
            
        # Danceability
        if abs(seed['danceability'] - target['danceability']) < 0.15 and seed['danceability'] > 0.65:
            return f"Recommended because this matches the groove and danceable rhythm of {seed['song']}."
            
        # Valence (Mood)
        if abs(seed['valence'] - target['valence']) < 0.15:
            if seed['valence'] > 0.65:
                return f"Recommended because it shares a similar bright, positive mood with {seed['song']}."
            elif seed['valence'] < 0.35:
                return f"Recommended because it shares the same deep, emotional mood as {seed['song']}."
                
        return f"Recommended based on its similar instrumentation, tempo, and style to {seed['song']}."

    def recommend(self, song_name, genre_filter=None, artist_filter=None, strategy="balanced", limit=6):
        if not self.is_loaded:
            return []
            
        matched_song = self.fuzzy_match_song(song_name)
        if not matched_song:
            return []
            
        song_index = self.catalog[self.catalog['song'] == matched_song].index[0]
        seed_song = dict(self.catalog.iloc[song_index])
        
        # Get query vector and calculate cosine similarities
        query_vector = self.X_combined[song_index]
        similarities = cosine_similarity(query_vector, self.X_combined)[0]
        
        # Candidate pool: top 300 highest cosine similarities (excluding seed)
        sorted_raw_indices = np.argsort(similarities)[::-1]
        pool_indices = [i for i in sorted_raw_indices if i != song_index][:300]
        
        candidates_scored = []
        for idx in pool_indices:
            candidate = dict(self.catalog.iloc[idx])
            
            # Filters
            if genre_filter and candidate['genre'].lower() != genre_filter.lower():
                continue
            if artist_filter and candidate['artist'].lower() != artist_filter.lower():
                continue
                
            raw_score = float(similarities[idx])
            
            # Apply strategy adjustments
            if strategy == "serendipity":
                pop_inv = 1.0 - candidate.get('popularity_norm', 0.5)
                final_rank_score = (raw_score * 0.65) + (pop_inv * 0.35)
                explanation_prefix = "✦ Serendipity Discovery: "
            elif strategy == "energy":
                energy_sim = 1.0 - abs(seed_song.get('energy', 0.5) - candidate.get('energy', 0.5))
                tempo_sim = 1.0 - abs(seed_song.get('tempo_norm', 0.5) - candidate.get('tempo_norm', 0.5))
                final_rank_score = (raw_score * 0.55) + (energy_sim * 0.30) + (tempo_sim * 0.15)
                explanation_prefix = "✦ High Energy & Rhythm Match: "
            elif strategy == "acoustic":
                ac_sim = 1.0 - abs(seed_song.get('acousticness', 0.5) - candidate.get('acousticness', 0.5))
                final_rank_score = (raw_score * 0.60) + (ac_sim * 0.40)
                explanation_prefix = "✦ Organic Timbre Match: "
            else:  # "balanced"
                final_rank_score = raw_score
                explanation_prefix = "✦ Vector Alignment: "
                
            confidence_percentage = int(min(99, max(68, (raw_score * 100) + 16)))
            
            candidate['confidence'] = confidence_percentage
            candidate['cosine_score'] = round(raw_score, 4)
            candidate['final_rank_score'] = final_rank_score
            candidate['explanation'] = explanation_prefix + self.generate_explanation(seed_song, candidate)
            candidate['strategy'] = strategy
            
            candidates_scored.append((final_rank_score, candidate))
            
        candidates_scored.sort(key=lambda x: x[0], reverse=True)
        recommended = [c[1] for c in candidates_scored[:limit]]
        
        for i, rec in enumerate(recommended, 1):
            rec['rank_index'] = f"{i:02d}"
            
        return recommended

    def get_vector_radar_data(self, song_name):
        """Calculates 6-axis normalized radar coordinates for SVG visualization"""
        if not self.is_loaded:
            return None
        info = self.get_song_info(song_name)
        if not info:
            return None
            
        dance = float(info.get('danceability', 0.5))
        energy = float(info.get('energy', 0.5))
        valence = float(info.get('valence', 0.5))
        acoustic = float(info.get('acousticness', 0.5))
        tempo_norm = float(info.get('tempo_norm', 0.5))
        pop_norm = float(info.get('popularity_norm', 0.5))
        
        dimensions = [
            {"name": "Danceability", "abbr": "DNC", "val": dance, "pct": int(dance * 100)},
            {"name": "Energy", "abbr": "NRG", "val": energy, "pct": int(energy * 100)},
            {"name": "Valence", "abbr": "VAL", "val": valence, "pct": int(valence * 100)},
            {"name": "Acousticness", "abbr": "ACO", "val": acoustic, "pct": int(acoustic * 100)},
            {"name": "Tempo", "abbr": "BPM", "val": tempo_norm, "pct": int(tempo_norm * 100)},
            {"name": "Popularity", "abbr": "POP", "val": pop_norm, "pct": int(pop_norm * 100)}
        ]
        
        cx, cy = 100, 100
        R = 70
        points = []
        axes = []
        
        for i, dim in enumerate(dimensions):
            angle = (i * 2 * math.pi / 6) - (math.pi / 2)
            r = max(0.12, dim["val"]) * R
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
            
            ax_x = cx + R * math.cos(angle)
            ax_y = cy + R * math.sin(angle)
            label_x = cx + (R + 15) * math.cos(angle)
            label_y = cy + (R + 15) * math.sin(angle)
            axes.append({
                "name": dim["name"],
                "abbr": dim["abbr"],
                "pct": dim["pct"],
                "x2": round(ax_x, 1),
                "y2": round(ax_y, 1),
                "lx": round(label_x, 1),
                "ly": round(label_y, 1)
            })
            
        return {
            "song": info.get("song"),
            "artist": info.get("artist"),
            "dimensions": dimensions,
            "polygon_points": " ".join(points),
            "axes": axes,
            "vector_coords": [round(d["val"], 3) for d in dimensions]
        }

    def recommend_by_mood(self, mood):
        if not self.is_loaded:
            return []
            
        mood = mood.lower()
        filtered = pd.DataFrame()
        
        if mood == "happy":
            filtered = self.catalog[(self.catalog['valence'] > 0.65) & (self.catalog['energy'] > 0.5)]
        elif mood == "sad":
            filtered = self.catalog[(self.catalog['valence'] < 0.35) & (self.catalog['energy'] < 0.4)]
        elif mood == "workout":
            filtered = self.catalog[(self.catalog['energy'] > 0.7) & (self.catalog['danceability'] > 0.6) & (self.catalog['tempo'] > 115)]
        elif mood == "chill":
            filtered = self.catalog[(self.catalog['energy'] < 0.45) & (self.catalog['acousticness'] > 0.3)]
        elif mood == "party":
            filtered = self.catalog[(self.catalog['danceability'] > 0.75) & (self.catalog['energy'] > 0.65)]
        elif mood == "romantic":
            filtered = self.catalog[(self.catalog['acousticness'] > 0.25) & (self.catalog['valence'].between(0.35, 0.7)) & (self.catalog['energy'].between(0.2, 0.6))]
            
        if filtered.empty:
            # Fallback
            filtered = self.catalog.head(100)
            
        # Take a random popular selection
        top_matches = filtered.sort_values(by='popularity', ascending=False).head(40)
        selected_rows = top_matches.sample(min(6, len(top_matches)))
        
        results = []
        for _, row in selected_rows.iterrows():
            track_dict = dict(row)
            track_dict['confidence'] = random.randint(85, 98)
            track_dict['explanation'] = f"Recommended because this track matches the vibes of the {mood.capitalize()} mood."
            results.append(track_dict)
            
        return results

    def get_search_suggestions(self, query, limit=5):
        if not self.is_loaded or not query:
            return []
            
        query_lower = query.strip().lower()
        
        # Match against song names or artist names
        matches = self.catalog[
            self.catalog['song'].str.lower().str.contains(query_lower, na=False) |
            self.catalog['artist'].str.lower().str.contains(query_lower, na=False)
        ]
        
        # Return top matches sorted by popularity
        top_matches = matches.sort_values(by='popularity', ascending=False).head(limit)
        
        suggestions = []
        for _, row in top_matches.iterrows():
            suggestions.append({
                "song": row['song'],
                "artist": row['artist'],
                "genre": row['genre']
            })
            
        return suggestions

    def get_unique_genres(self):
        if not self.is_loaded:
            return []
        return sorted(self.catalog['genre'].unique().tolist())

    def get_unique_artists(self):
        if not self.is_loaded:
            return []
        # Return top 30 most frequent popular artists
        return sorted(self.catalog['artist'].value_counts().head(30).index.tolist())

    def get_dynamic_top_artists(self, limit=5):
        if not self.is_loaded:
            return []
        
        # Calculate stats for each artist
        artist_stats = self.catalog.groupby('artist').agg(
            track_count=('song', 'count'),
            avg_pop=('popularity', 'mean')
        ).reset_index()
        
        # Combined Score
        artist_stats['score'] = artist_stats['track_count'] * 2.0 + artist_stats['avg_pop']
        top_artists = artist_stats.sort_values(by='score', ascending=False).head(limit)
        
        results = []
        for _, row in top_artists.iterrows():
            results.append({
                "name": row['artist'],
                "tracks_count": int(row['track_count']),
                "popularity": int(row['avg_pop'])
            })
        return results

    def get_dynamic_top_albums_tracks(self, limit=6):
        if not self.is_loaded:
            return []
        # Return top tracks that we can extract album data from
        top_tracks = self.catalog.sort_values(by='popularity', ascending=False).head(limit)
        results = []
        for _, row in top_tracks.iterrows():
            results.append(dict(row))
        return results

    def get_playlist_tracks(self, playlist_type, limit=6):
        if not self.is_loaded:
            return []
            
        playlist_type = playlist_type.lower()
        if playlist_type == "chill vibes":
            return self.recommend_by_mood("chill")
        elif playlist_type == "workout mix":
            return self.recommend_by_mood("workout")
        elif playlist_type == "party hits":
            return self.recommend_by_mood("party")
        elif playlist_type == "romantic":
            return self.recommend_by_mood("romantic")
        elif playlist_type == "top pop":
            pop_tracks = self.catalog[self.catalog['genre'].str.lower() == 'pop'].sort_values(by='popularity', ascending=False).head(limit)
            if pop_tracks.empty:
                pop_tracks = self.catalog[self.catalog['genre'].str.lower().str.contains('pop', na=False)].sort_values(by='popularity', ascending=False).head(limit)
            if pop_tracks.empty:
                pop_tracks = self.catalog.head(limit)
            return [dict(row) for _, row in pop_tracks.iterrows()]
        elif playlist_type == "coding sessions":
            coding_tracks = self.catalog[
                self.catalog['genre'].str.lower().isin(['electronic', 'dance', 'ambient', 'classical', 'jazz']) &
                (self.catalog['energy'] < 0.5)
            ].sort_values(by='popularity', ascending=False).head(limit)
            if coding_tracks.empty:
                coding_tracks = self.catalog[self.catalog['energy'] < 0.4].sort_values(by='popularity', ascending=False).head(limit)
            return [dict(row) for _, row in coding_tracks.iterrows()]
        
        return []

# Global singleton instance
engine = RecommendationEngine()
