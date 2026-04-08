// This automatically detects if you are local or on Render
const API_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:5001" 
    : ""; // Empty string means "use the current domain" (e.g., your-app.onrender.com)

// Add to Watchlist
async function addToWatchlist(tmdbId, title, posterPath) {
    console.log("Sending data:", { tmdbId, title, posterPath }); // DEBUGGING

    const res = await fetch(`${API_URL}/api/watchlist`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            tmdb_id: tmdbId,    // Must match Python's data.get("tmdb_id")
            title: title, 
            poster_path: posterPath 
        })
    });
    
    const data = await res.json();
    if (res.ok) {
        alert(`${title} added to watchlist!`);
    } else {
        console.error("Server Error:", data);
        alert(data.error || 'Failed to add to watchlist');
    }
}

// Remove from Watchlist
async function removeFromWatchlist(tmdbId) {
    // FIXED: Pointing to the new API structure
    const res = await fetch(`${API_URL}/api/watchlist/${tmdbId}`, {
        method: 'DELETE'
    });
    
    if (res.ok) {
        alert('Movie removed from watchlist');
        location.reload();
    } else {
        const data = await res.json();
        alert(data.error || 'Failed to remove');
    }
}

// AI Recommendation
async function getRecommendation() {
    const mood = document.getElementById('mood').value;
    const genre = document.getElementById('genre').value;
    const box = document.getElementById('recommendation');

    if (!mood && !genre) {
        alert('Please enter a mood or genre');
        return;
    }

    box.style.display = 'block';
    box.innerHTML = 'Getting recommendation...';

    const res = await fetch(`${API_URL}/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mood, genre })
    });

    const data = await res.json();
    if (res.ok) {
        box.innerHTML = `🎬 ${data.recommendation}`;
    } else {
        box.innerHTML = `Error: ${data.error}`;
    }
}