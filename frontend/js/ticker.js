async function fetchTicker() {
    const tickerDom = document.getElementById('ticker-content');
    try {
        const response = await fetch(`${API_BASE}/ticker`);
        const data = await response.json();
        tickerDom.textContent = data.message;
    } catch (err) {
        console.error("Ticker fetch error:", err);
        tickerDom.textContent = "Safe travels! No major disruptions reported right now.";
    }
}

fetchTicker();

// Refresh ticker every 15 minutes
setInterval(fetchTicker, 900000);
