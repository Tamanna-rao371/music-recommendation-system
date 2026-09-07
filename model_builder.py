import os
import sys
import time

# Support UTF-8 console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from config import Config

print("=" * 65)
print("🎵 TuneSphere AI - Model Builder & Feature Pipeline")
print("=" * 65)

# 1. Verify Dataset
DATASET_PATH = os.environ.get("DATASET_PATH", Config.DATASET_PATH)
if not os.path.exists(DATASET_PATH):
    print(f"❌ Error: Dataset file not found at '{DATASET_PATH}'.")
    sys.exit(1)

print(f"\n[1/5] Loading track catalog from '{DATASET_PATH}'...")
start_time = time.time()
df = pd.read_csv(DATASET_PATH)
print(f"      ✓ Loaded {len(df):,} total raw records in {time.time() - start_time:.2f}s")

# 2. Data Cleaning & Feature Mapping
print("\n[2/5] Preprocessing metadata & acoustic features...")
clean_start = time.time()

# Rename raw Spotify dataset columns if needed
if 'track_name' in df.columns:
    df = df.rename(columns={'track_name': 'song', 'artist_name': 'artist'})

# Drop missing values
df = df.dropna(subset=['song', 'artist'])
if 'genre' in df.columns:
    df['genre'] = df['genre'].fillna('Pop').astype(str)
else:
    df['genre'] = 'Pop'

# Keep clean titles and drop duplicates
df = df[df['song'].str.contains('^[A-Za-z0-9 ]+$', regex=True, na=False)]
df = df.drop_duplicates(subset=['song', 'artist'])

# Sort by popularity and select top catalog
CATALOG_SIZE = Config.CATALOG_SIZE
catalog = df.sort_values(by='popularity', ascending=False).head(CATALOG_SIZE).reset_index(drop=True)

# Normalize Numerical Audio Features (0.0 to 1.0)
numerical_cols = ['popularity', 'danceability', 'energy', 'valence', 'acousticness', 'tempo']
for col in numerical_cols:
    if col in catalog.columns:
        min_val = catalog[col].min()
        max_val = catalog[col].max()
        if max_val > min_val:
            catalog[col + '_norm'] = (catalog[col] - min_val) / (max_val - min_val)
        else:
            catalog[col + '_norm'] = 0.0

print(f"      ✓ Preprocessed {len(catalog):,} catalog tracks in {time.time() - clean_start:.2f}s")

# 3. Vectorize Text Features (Artist + Genre)
print("\n[3/5] Vectorizing metadata tags with CountVectorizer...")
vec_start = time.time()
catalog['tags'] = catalog['artist'] + " " + catalog['genre']
cv = CountVectorizer(max_features=3000, stop_words='english')
X_text = cv.fit_transform(catalog['tags'])
print(f"      ✓ Built sparse tag matrix: {X_text.shape} in {time.time() - vec_start:.2f}s")

# 4. Dense Acoustic Feature Matrix & Hybrid Matrix
print("\n[4/5] Building hybrid sparse latent vector space...")
X_text_scaled = X_text * 1.8
norm_cols = [col + '_norm' for col in numerical_cols]
X_num = catalog[norm_cols].values
X_num_sparse = csr_matrix(X_num)
X_combined = hstack([X_text_scaled, X_num_sparse]).tocsr()
print(f"      ✓ Combined feature space shape: {X_combined.shape} (Dimensions: {X_combined.shape[1]})")

# 5. Recommendation Benchmark
print("\n[5/5] Benchmarking recommendation engine inference latency...")
benchmark_song = catalog.iloc[0]['song']
test_idx = 0

t0 = time.time()
song_vector = X_combined[test_idx]
similarity_scores = cosine_similarity(song_vector, X_combined).flatten()
top_indices = similarity_scores.argsort()[::-1][1:7]
latency_ms = (time.time() - t0) * 1000

print(f"      ✓ Test Query: '{benchmark_song}'")
print(f"      ✓ Inference Latency: {latency_ms:.2f} ms")
print(f"      ✓ Top 3 Similar Matches:")
for i, idx in enumerate(top_indices[:3], 1):
    rec_song = catalog.iloc[idx]['song']
    rec_artist = catalog.iloc[idx]['artist']
    rec_score = similarity_scores[idx]
    print(f"         #{i:02d} {rec_song} by {rec_artist} (Cosine Match: {rec_score * 100:.1f}%)")

print("\n" + "=" * 65)
print("✨ Model Builder complete: All ML pipelines verified and ready!")
print("=" * 65)
