import os
import re

from dotenv import load_dotenv
from flask import Flask, request, redirect, session, url_for, render_template, jsonify
from flask_cors import CORS

import lyricsgenius
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from spotipy.exceptions import SpotifyException

from transformers import pipeline


load_dotenv()


def env(name, default=None):
    value = os.getenv(name, default)
    if value is None:
        return None
    return value.strip().strip('"').strip("'")


app = Flask(__name__)
CORS(app)

app.secret_key = env("FLASK_SECRET_KEY", "change-this-secret-key")

SPOTIPY_CLIENT_ID = env("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = env("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = env("SPOTIPY_REDIRECT_URI")
GENIUS_ACCESS_TOKEN = env("GENIUS_ACCESS_TOKEN")

SPOTIFY_SCOPE = "user-library-read playlist-modify-public playlist-modify-private"

genius = lyricsgenius.Genius(
    GENIUS_ACCESS_TOKEN,
    skip_non_songs=True,
    excluded_terms=["(Remix)", "(Live)", "(Cover)"],
    remove_section_headers=True,
    verbose=False,
    timeout=15,
)

mood_classifier = pipeline(
    "text-classification",
    model="bhadresh-savani/bert-base-uncased-emotion",
    top_k=None,
)


def get_auth_manager():
    return SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIFY_SCOPE,
        cache_handler=FlaskSessionCacheHandler(session),
        show_dialog=True,
    )


def get_spotify_client():
    auth_manager = get_auth_manager()
    token_info = auth_manager.cache_handler.get_cached_token()

    if not auth_manager.validate_token(token_info):
        return None

    return spotipy.Spotify(auth_manager=auth_manager)


@app.route("/")
def index():
    auth_manager = get_auth_manager()
    token_info = auth_manager.cache_handler.get_cached_token()
    login_required = not auth_manager.validate_token(token_info)

    return render_template("index.html", login_required=login_required)


@app.route("/login")
def login():
    return redirect(get_auth_manager().get_authorize_url())


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/callback")
def callback():
    try:
        code = request.args.get("code")

        if not code:
            return jsonify({"error": "Spotify authorization code missing"}), 400

        get_auth_manager().get_access_token(code, as_dict=True)
        return redirect(url_for("index"))

    except Exception as e:
        return jsonify({"error": f"Callback error: {e}"}), 400


def analyze_mood(text):
    try:
        if not text or not text.strip():
            return "neutral"

        result = mood_classifier(text[:512])[0]

        best = max(result, key=lambda item: item["score"])
        mood = best["label"].lower()

        print(f"Detected mood: {mood} | confidence: {best['score']:.2f}")
        return mood

    except Exception as e:
        print(f"Error detecting mood: {e}")
        return "neutral"


def get_user_liked_songs(sp):
    songs = []

    try:
        results = sp.current_user_saved_tracks(limit=50)

        while results:
            for item in results.get("items", []):
                track = item.get("track")

                if not track or not track.get("id"):
                    continue

                artists = track.get("artists", [])
                artist_name = artists[0]["name"] if artists else "Unknown Artist"

                songs.append({
                    "name": track["name"],
                    "artist": artist_name,
                    "id": track["id"],
                    "url": track["external_urls"]["spotify"],
                })

            if results.get("next"):
                results = sp.next(results)
            else:
                break

        print(f"Fetched liked songs: {len(songs)}")
        return songs

    except Exception as e:
        print(f"Error fetching liked songs: {e}")
        return []


def clean_lyrics(lyrics):
    lyrics = re.sub(r"\d*Embed$", "", lyrics)
    lyrics = re.sub(r"You might also like", "", lyrics, flags=re.IGNORECASE)
    lyrics = re.sub(r"\[.*?\]", "", lyrics)
    lyrics = re.sub(r"\s+", " ", lyrics)
    return lyrics.strip()


def get_song_lyrics(song_name, artist_name):
    try:
        song = genius.search_song(song_name, artist_name)

        if not song or not song.lyrics:
            return None

        return clean_lyrics(song.lyrics)

    except Exception as e:
        print(f"Error fetching lyrics for {song_name} by {artist_name}: {e}")
        return None


def match_songs_to_mood(target_mood, liked_songs, max_matches=25):
    matched_songs = []

    for song in liked_songs:
        lyrics = get_song_lyrics(song["name"], song["artist"])

        if not lyrics:
            continue

        song_mood = analyze_mood(lyrics)

        print(f"{song['name']} - {song['artist']} => {song_mood}")

        if song_mood == target_mood:
            matched_songs.append(song)

        if len(matched_songs) >= max_matches:
            break

    print(f"Matched songs: {len(matched_songs)}")
    return matched_songs


def create_playlist(sp, mood, songs):
    try:
        valid_songs = [song for song in songs if song.get("id")]

        if not valid_songs:
            return None, "No valid Spotify tracks found."

        current_user = sp.current_user()
        print(f"Creating playlist for Spotify user: {current_user.get('id')}")

        playlist = sp.current_user_playlist_create(
            name=f"{mood.capitalize()} Vibes",
            public=False,
            description=f"Auto-generated playlist based on your {mood} mood.",
        )

        track_uris = [f"spotify:track:{song['id']}" for song in valid_songs]

        for i in range(0, len(track_uris), 100):
            sp.playlist_add_items(playlist["id"], track_uris[i:i + 100])

        return playlist["external_urls"]["spotify"], None

    except SpotifyException as e:
        error_message = f"Spotify error {e.http_status}: {e.msg}"
        print(error_message)
        return None, error_message

    except Exception as e:
        error_message = f"Playlist creation error: {e}"
        print(error_message)
        return None, error_message


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        sp = get_spotify_client()

        if not sp:
            return jsonify({
                "error": "Please login with Spotify first.",
                "login_url": url_for("login"),
            }), 401

        data = request.get_json(silent=True) if request.is_json else request.form
        user_input = data.get("text", "").strip() if data else ""

        if not user_input:
            return jsonify({"error": "No mood text provided."}), 400

        mood = analyze_mood(user_input)
        liked_songs = get_user_liked_songs(sp)

        if not liked_songs:
            return jsonify({
                "mood": mood,
                "message": "No liked songs found in your Spotify library.",
            }), 200

        recommended_songs = match_songs_to_mood(mood, liked_songs)

        if not recommended_songs:
            return jsonify({
                "mood": mood,
                "message": "Mood detected, but no matching liked songs were found.",
            }), 200

        playlist_url, error = create_playlist(sp, mood, recommended_songs)

        if error:
            return jsonify({
                "mood": mood,
                "songs_found": len(recommended_songs),
                "error": error,
                "message": "Songs matched, but playlist creation failed.",
            }), 500

        return jsonify({
            "mood": mood,
            "songs_found": len(recommended_songs),
            "playlist": playlist_url,
            "songs": recommended_songs,
        }), 200

    except Exception as e:
        print(f"Error in recommendation route: {e}")
        return jsonify({"error": f"Recommendation error: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)

