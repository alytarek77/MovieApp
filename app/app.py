
import requests
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from google import genai

import json
from ai import generate_recommendaton_ai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# Load environment variables

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# MongoDB Connection
# MongoDB Connection
mongo_client = MongoClient(os.getenv("MONGO_URI"), tls=True, tlsAllowInvalidCertificates=True)
db = mongo_client[os.getenv("DB_NAME")]
watchlist_collection = db["watchlist"]

# TMDB Configuration
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"


@app.route("/")
def home():
    query = request.args.get("q", "")
    movies = []
    if query:
        res = requests.get(f"{TMDB_BASE}/search/movie", params={
            "api_key": TMDB_API_KEY,
            "query": query
        })
        if res.status_code == 200:
            movies = res.json().get("results", [])
    return render_template("index.html", movies=movies, query=query)


@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):
    res = requests.get(f"{TMDB_BASE}/movie/{movie_id}", params={
        "api_key": TMDB_API_KEY
    })
    if res.status_code == 404:
        return jsonify({"error": "Movie not found"}), 404
    movie = res.json()
    return render_template("movie.html", movie=movie)


@app.route("/watchlist")
def watchlist_page():
    """This route serves the beautiful HTML grid."""
    return render_template("watchlist.html")


@app.route("/api/watchlist", methods=["GET"])
def get_watchlist_data():
    """This is the 'Brain' that the JavaScript calls to get movie data."""
    movies = list(watchlist_collection.find({}, {"_id": 0}))
    return jsonify(movies), 200


@app.route("/api/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.get_json()
    if not data or not data.get("tmdb_id") or not data.get("title"):
        return jsonify({"error": "tmdb_id and title are required"}), 400

    existing = watchlist_collection.find_one({"tmdb_id": data["tmdb_id"]})
    if existing:
        return jsonify({"error": "Movie already in watchlist"}), 409

    watchlist_collection.insert_one(data)
    return jsonify({"message": "Movie added to watchlist"}), 201


@app.route("/api/watchlist/<int:tmdb_id>", methods=["DELETE"])
def remove_from_watchlist(tmdb_id):
    # Try deleting as a Number first
    result = watchlist_collection.delete_one({"tmdb_id": tmdb_id})
    
    # If nothing was deleted, try deleting as a String
    if result.deleted_count == 0:
        result = watchlist_collection.delete_one({"tmdb_id": str(tmdb_id)})
        
    if result.deleted_count == 0:
        return jsonify({"error": "Movie not found in watchlist"}), 404
        
    return jsonify({"message": "Movie removed from watchlist"}), 200


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json() or {}
    mood = data.get('mood')
    genre = data.get('genre')

    if not mood or not genre:
        return jsonify({"message": "Mood and Genre are required"}), 400

    try:
        ai_response = generate_recommendaton_ai(mood, genre)
        print(f"AI RAW RESPONSE: {ai_response}") # Check what the AI actually said
        movies = json.loads(ai_response)
        return jsonify(movies), 200

    except Exception as e:
        print("!! CRASH ERROR:", e) # This will show the real error in your terminal
        return jsonify({"message": "Error", "error": str(e)}), 500

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)