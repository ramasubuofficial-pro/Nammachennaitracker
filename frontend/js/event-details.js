const API_BASE = "http://localhost:8000/api";

async function fetchEventDetails() {
    const params = new URLSearchParams(window.location.search);
    const eventId = params.get('id');
    
    if (!eventId) {
        document.getElementById('event-content').innerHTML = `
            <div class="glass" style="padding: 4rem; text-align: center; border-color: var(--danger);">
                <h3>No Event ID provided.</h3>
                <a href="index.html" class="back-link">Return Home</a>
            </div>
        `;
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/events/${eventId}`);
        if (!response.ok) throw new Error("Event not found");
        const event = await response.json();
        
        renderEventDetails(event);
        initMiniMap(event);
    } catch (err) {
        console.error("Error fetching event details:", err);
        document.getElementById('event-content').innerHTML = `
            <div class="glass" style="padding: 4rem; text-align: center;">
                <h3>Event Not Found</h3>
                <p>The event you are looking for may have been removed or updated.</p>
                <a href="index.html" class="back-link">Return Home</a>
            </div>
        `;
    }
}

function renderEventDetails(event) {
    const content = document.getElementById('event-content');
    
    content.innerHTML = `
        <div class="detail-grid">
            <div class="glass" style="padding: 3rem; border-left: 10px solid ${event.party_color};">
                <span class="party-badge" style="background: ${event.party_color}; font-size: 1rem; padding: 0.5rem 1.5rem;">
                    ${event.party_name}
                </span>
                <h2 style="font-size: 2.5rem; margin: 1rem 0;">${event.title}</h2>
                <p style="font-size: 1.25rem; color: var(--text-muted); margin-bottom: 2rem;">${event.title_tamil || ''}</p>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                    <div class="glass" style="padding: 1.5rem; background: rgba(56, 189, 248, 0.05);">
                        <span style="font-size: 0.8rem; color: var(--text-muted); display: block; margin-bottom: 0.5rem;">START TIME</span>
                        <span style="font-size: 1.5rem; font-weight: bold;">🕒 ${new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                    </div>
                    <div class="glass" style="padding: 1.5rem; background: rgba(56, 189, 248, 0.05);">
                        <span style="font-size: 0.8rem; color: var(--text-muted); display: block; margin-bottom: 0.5rem;">STATUS</span>
                        <span style="font-size: 1.5rem; font-weight: bold; color: ${event.status === 'confirmed' ? 'var(--confirmed)' : 'var(--unverified)'};">
                            ${event.status.toUpperCase()}
                        </span>
                    </div>
                </div>

                <div class="glass" style="padding: 2rem; border-color: rgba(255,255,255,0.05);">
                    <h4 style="margin-bottom: 1rem;">Location Details</h4>
                    <p style="font-size: 1.2rem; margin-bottom: 0.5rem;">📍 ${event.location_name}</p>
                    <p style="color: var(--text-muted);">${event.location_tamil || ''}</p>
                </div>
            </div>

            <div class="sidebar">
                <div class="glass" style="padding: 2rem; margin-bottom: 2rem; text-align: center;">
                    <div style="width: 100px; height: 100px; background: rgba(255,255,255,0.1); border-radius: 50%; margin: 0 auto 1.5rem auto; display: flex; align-items: center; justify-content: center; font-size: 3rem;">
                        🏛️
                    </div>
                    <h4>Official Party Details</h4>
                    <a href="parties.html" style="color: var(--accent); font-size: 0.9rem; text-decoration: none;">View all events for ${event.party_name} →</a>
                </div>

                <div class="glass" style="padding: 2rem;">
                    <h4 style="margin-bottom: 1rem;">Source</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 1.5rem;">Data verified via ${event.source_name || 'Public News'}.</p>
                    <a href="${event.source_url}" target="_blank" class="glass" style="display: block; width: 100%; text-align: center; padding: 1rem; text-decoration: none; color: white; background: rgba(255,255,255,0.05);">
                        Open Original Clip/Source
                    </a>
                </div>
            </div>
        </div>

        <div id="mini-map"></div>
    `;
}

function initMiniMap(event) {
    const miniMap = L.map('mini-map').setView([event.latitude, event.longitude], 15);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(miniMap);
    
    L.circleMarker([event.latitude, event.longitude], {
        radius: 12,
        fillColor: event.party_color,
        color: "#fff",
        weight: 3,
        opacity: 1,
        fillOpacity: 0.9
    }).addTo(miniMap)
      .bindPopup(`<strong>${event.location_name}</strong><br>${event.title}`)
      .openPopup();
}

fetchEventDetails();
