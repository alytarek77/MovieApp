
import requests
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from google import genai

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

# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json() or {}
    mood = data.get("mood", "").strip()
    genre = data.get("genre", "").strip()

    if not mood and not genre:
        return jsonify({"error": "Mood or genre is required"}), 400

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY is not set in .env"}), 500

        # Correct new SDK usage
        client = genai.Client(api_key=api_key)

        prompt = f"Recommend one movie for someone feeling {mood} who likes {genre} genre. "
        prompt += "Reply with ONLY the movie title on the first line, followed by a one-sentence reason."

        # Recommended way: contents as list
        response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=[prompt]
        )

        recommendation_text = response.text.strip() if response.text else ""

        return jsonify({
            "recommendation": recommendation_text
        }), 200

    except Exception as e:
        error_msg = str(e).lower()

        if "429" in error_msg or "rate limit" in error_msg or "quota" in error_msg:
            return jsonify({
                "error": "Gemini is currently at capacity (rate limit). Please wait a few seconds and try again."
            }), 429

        if "404" in error_msg or "not found" in error_msg or "model" in error_msg:
            return jsonify({
                "error": "Model not found. Try changing the model name in code."
            }), 400

        print(f"Gemini API Error: {str(e)}")   # Keep for debugging
        return jsonify({
            "error": "AI recommendation is temporarily unavailable. Please try again later."
        }), 500

@app.route("/health")
def health():
    try:
        mongo_client.admin.command("ping")
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)