// Add to Watchlist
async function addToWatchlist(tmdbId, title, posterPath) {
    // FIXED: Changed '/watchlist' to '/api/watchlist' to match your new Python route
    const res = await fetch('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tmdb_id: tmdbId, title: title, poster_path: posterPath })
    });
    
    const data = await res.json();
    if (res.ok) {
        alert(`${title} added to watchlist!`);
    } else {
        alert(data.error || 'Failed to add to watchlist');
    }
}

// Remove from Watchlist
async function removeFromWatchlist(tmdbId) {
    // FIXED: Pointing to the new API structure
    const res = await fetch(`/api/watchlist/${tmdbId}`, {
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

    const res = await fetch('/recommend', {
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