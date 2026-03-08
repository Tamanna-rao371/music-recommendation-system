from flask import Flask, render_template, request, session, redirect
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
app.secret_key = "music_recommender_secret"

# -------------------------------
# Spotify API
# -------------------------------

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id="",
    client_secret=""
))

# -------------------------------
# Load Dataset
# -------------------------------

songs = pd.read_csv("dataset/songs.csv")

# Reduce dataset size
songs = songs.head(10000)

# Keep only English song names
songs = songs[songs['track_name'].str.contains('^[A-Za-z0-9 ]+$', regex=True)]

# Select columns
songs = songs[['artist_name','track_name','genre']]

songs = songs.rename(columns={
    'artist_name':'artist',
    'track_name':'song'
})

# Create tags
songs["tags"] = songs["artist"] + " " + songs["genre"]

# Vectorization
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(songs['tags']).toarray()

# Similarity
similarity = cosine_similarity(vectors)

# -------------------------------
# Get Spotify Song Details
# -------------------------------

def get_song_details(song):

    results = sp.search(q=song, limit=1)

    if results['tracks']['items']:

        track = results['tracks']['items'][0]

        return {
            "song": track['name'],
            "artist": track['artists'][0]['name'],
            "image": track['album']['images'][0]['url'],
            "preview": track['preview_url']
        }

    return None


# -------------------------------
# Recommendation Function
# -------------------------------

def recommend(song):

    if song not in songs['song'].values:
        return []

    song_index = songs[songs['song'] == song].index[0]

    distances = similarity[song_index]

    songs_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended = []

    for i in songs_list:

        song_name = songs.iloc[i[0]].song
        details = get_song_details(song_name)

        if details:
            recommended.append(details)

    return recommended


# -------------------------------
# Routes
# -------------------------------

@app.route("/", methods=["GET","POST"])
def index():

    recommendations = []

    if request.method == "POST":

        song = request.form["song"]
        recommendations = recommend(song)

    trending = songs.sample(6)['song'].tolist()

    favorites = session.get("favorites", [])

    return render_template(
        "index.html",
        songs=list(songs['song'].values),
        recommendations=recommendations,
        trending=trending,
        favorites=favorites
    )


@app.route("/favorite/<song>")
def favorite(song):

    if "favorites" not in session:
        session["favorites"] = []

    session["favorites"].append(song)
    session.modified = True

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)