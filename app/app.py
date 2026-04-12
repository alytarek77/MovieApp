import json
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient

from app.ai import generate_recommendaton_ai

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

app = Flask(__name__,
            template_folder='../templates',
            static_folder='../static')

# MongoDB Connection
mongo_client = MongoClient(
    os.getenv("MONGO_URI"),
    tls=True,
    tlsAllowInvalidCertificates=True
)
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
    return render_template("watchlist.html")


@app.route("/api/watchlist", methods=["GET"])
def get_watchlist_data():
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
    result = watchlist_collection.delete_one({"tmdb_id": tmdb_id})

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
        movies = json.loads(ai_response)
        return jsonify(movies), 200

    except Exception as e:
        return jsonify({"message": "Error", "error": str(e)}), 500


@app.route("/health")
def health():
    try:
        mongo_client.admin.command("ping")
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception:
        return jsonify({"status": "ok", "db": "disconnected"}), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)