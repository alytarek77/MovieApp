from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import requests
import os

load_dotenv()

app = Flask(__name__, 
            template_folder='../templates',
            static_folder='../static')

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
watchlist_collection = db["watchlist"]

# TMDB
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = "https://api.themoviedb.org/3"


@app.route("/health")
def health():
    try:
        client.admin.command("ping")
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500


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


@app.route("/watchlist", methods=["GET"])
def get_watchlist():
    movies = list(watchlist_collection.find({}, {"_id": 0}))
    return jsonify(movies), 200


@app.route("/watchlist", methods=["POST"])
def add_to_watchlist():
    data = request.get_json()
    if not data or not data.get("tmdb_id") or not data.get("title"):
        return jsonify({"error": "tmdb_id and title are required"}), 400
    existing = watchlist_collection.find_one({"tmdb_id": data["tmdb_id"]})
    if existing:
        return jsonify({"error": "Movie already in watchlist"}), 409
    watchlist_collection.insert_one(data)
    return jsonify({"message": "Movie added to watchlist"}), 201


@app.route("/watchlist/<int:tmdb_id>", methods=["DELETE"])
def remove_from_watchlist(tmdb_id):
    result = watchlist_collection.delete_one({"tmdb_id": tmdb_id})
    if result.deleted_count == 0:
        return jsonify({"error": "Movie not found in watchlist"}), 404
    return jsonify({"message": "Movie removed from watchlist"}), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(debug=True)

