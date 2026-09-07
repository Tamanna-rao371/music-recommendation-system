import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
songs = pd.read_csv("dataset/songs.csv")

# Reduce dataset size (for memory safety)
songs = songs.head(5000)

# Select useful columns
songs = songs[['artist_name', 'track_name', 'genre']]

# Rename columns
songs = songs.rename(columns={
    'artist_name': 'artist',
    'track_name': 'song'
})

# Create tags column
songs["tags"] = songs["artist"] + " " + songs["genre"]

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(songs['tags']).toarray()

# Similarity matrix
similarity = cosine_similarity(vectors)


def recommend(song):

    # Check if song exists
    if song not in songs['song'].values:
        print("Song not found in dataset.")
        return

    # Find song index
    song_index = songs[songs['song'] == song].index[0]

    # Get similarity scores
    distances = similarity[song_index]

    # Sort songs by similarity
    songs_list = sorted(list(enumerate(distances)),
                        reverse=True,
                        key=lambda x: x[1])[1:6]

    print("\nRecommended Songs:\n")

    for i in songs_list:
        print(songs.iloc[i[0]].song)


# Show some songs available in dataset
print("\nSample Songs From Dataset:\n")
print(songs['song'].head(20))

# Test recommendation (use a song from above list)
recommend(songs['song'].iloc[0])