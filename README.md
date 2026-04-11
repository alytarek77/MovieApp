# MovieApp  AI-Powered Movie Watchlist
Group 10

A web app to search movies, manage a personal watchlist, and get AI-powered movie recommendations based on mood and genre.

Live URL: https://movieapp-2-3vxt.onrender.com

Team Roles
- Aly Abouzeid: Full-Stack Development (Python/Flask, HTML, CSS, JavaScript), MongoDB Database, AI Integration (Google Gemini API), DevOps (CI/CD, Docker), and Testing.

Architecture Overview
- Client: A responsive web interface built with HTML, CSS, and JavaScript.
- Server: A Python Flask API that handles business logic and routes.
- AI Layer: Integration with Google Gemini API for dynamic movie recommendations based on mood and genre.
- Database: MongoDB Atlas for persistent storage of the user's watchlist.
- CI/CD: Automated pipeline using GitHub Actions to run tests and Docker for containerized deployment on Render.

Features
- Movie Search: Search any movie using the TMDB API.
- Movie Details: View title, overview, rating, runtime, and poster.
- Personal Watchlist: Add and remove movies stored persistently in MongoDB.
- AI Movie Recommendation (AI-powered): Enter a mood and genre to receive a personalized movie suggestion via Google Gemini.
- Health Check: /health endpoint to verify app and database status.

Setup and Installation
- Clone the repository: git clone https://github.com/alytarek77/MovieApp.git
- Install dependencies: pip install -r requirements.txt
- Configuration: Create a .env file with MONGO_URI, DB_NAME, TMDB_API_KEY, and GEMINI_API_KEY. In production, these are securely managed via the Render dashboard.
- Run locally: cd app && python3 app.py

Docker
- Build: docker build -t movie-app .
- Run: docker run -p 5000:5000 --env-file .env movie-app

Testing and CI/CD
- Unit Tests: 12+ unit tests validating backend routes, API responses, and database connectivity.
- Continuous Integration: GitHub Actions automatically runs the full test suite on every push or pull request to main and develop.
- Continuous Deployment: Once tests pass, the pipeline builds a Docker image and Render redeploys the live site automatically. Changes are visible within minutes.
- Run tests: pytest tests/
