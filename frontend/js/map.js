const CHENNAI_COORDS = [13.0827, 80.2707];
const map = L.map('map').setView(CHENNAI_COORDS, 12);
const markerClusterGroup = L.markerClusterGroup();

// Use a dark-themed tile layer
L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20
}).addTo(map);

async function loadMarkers() {
    const params = new URLSearchParams(window.location.search);
    const targetId = params.get('id');

    try {
        const response = await fetch('https://nammachennaitracker.onrender.com/api/events/today');
        const events = await response.json();
        
        events.forEach(event => {
            const marker = L.circleMarker([event.latitude, event.longitude], {
                radius: 10,
                fillColor: event.party_color,
                color: "#fff",
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            });

            const popupContent = `
                <div class="popup-card">
                    <span style="font-size: 0.7rem; font-weight: bold; background: ${event.party_color}; color: white; padding: 2px 6px; border-radius: 4px; text-transform: uppercase;">
                        ${event.party_name}
                    </span>
                    <h4 style="margin-top: 5px;">${event.title}</h4>
                    <p>📍 ${event.location_name}</p>
                    <p>🕒 ${new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</p>
                    <p style="color: ${event.status === 'confirmed' ? 'green' : 'orange'}; font-weight: bold;">
                        ${event.status.toUpperCase()}
                    </span></p>
                    <button onclick="window.open('https://www.google.com/maps/dir/?api=1&destination=${event.latitude},${event.longitude}', '_blank')">
                        Get Directions
                    </button>
                    <a href="event-details.html?id=${event.id}" style="display: block; text-align: center; margin-top: 5px; font-size: 0.8rem; color: #2563eb; text-decoration: none;">Full Details →</a>
                </div>
            `;
            
            marker.bindPopup(popupContent);
            markerClusterGroup.addLayer(marker);

            // If this is the targeted event, focus on it
            if (targetId && event.id == targetId) {
                map.setView([event.latitude, event.longitude], 16);
                marker.openPopup();
            }
        });

        map.addLayer(markerClusterGroup);
    } catch (err) {
        console.error("Map fetch error:", err);
    }
}

loadMarkers();
