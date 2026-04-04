from pymongo import MongoClient
from dotenv import load_dotenv
import os
from flask import Flask
import requests
from flask import request, jsonify, render_template

load_dotenv()

app = Flask(__name__)

@app.route("/")
def home():
    return "App is running"

@app.route("/health")
def health():
    return {"status": "ok"}, 200


#MongoDB connection 
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]
movies_collection = db["movies"]

@app.route("/test-db")
def test_db():
    client.admin.command("ping")
    return {"status": "Database connected"}, 200

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