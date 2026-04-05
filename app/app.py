from pymongo import MongoClient
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
import requests
import os
import google.generativeai as genai


load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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


@app.route("/watchlist/view")
def watchlist_page():
    return render_template("watchlist.html")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    mood = data.get("mood", "")
    genre = data.get("genre", "")
    if not mood and not genre:
        return jsonify({"error": "mood or genre is required"}), 400
    prompt = f"Recommend one movie for someone feeling {mood} who likes {genre}. Reply with just the title and a one-sentence reason."
    try:
        response = gemini_model.generate_content(prompt)
        return jsonify({"recommendation": response.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




if __name__ == "__main__":
    app.run(debug=True)

