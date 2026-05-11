const API_BASE = "http://localhost:8000/api";

const state = {
    events: [],
    parties: [],
    stats: {
        totalEvents: 0,
        partiesActive: 0,
        areasAffected: 0
    },
    language: 'en'
};

const dom = {
    eventsContainer: document.getElementById('events-container'),
    statTotalEvents: document.getElementById('stat-total-events'),
    statPartiesActive: document.getElementById('stat-parties-active'),
    statAreasAffected: document.getElementById('stat-areas-affected'),
    currentDate: document.getElementById('current-date'),
    lastUpdated: document.getElementById('last-updated-timestamp'),
    langToggle: document.getElementById('lang-toggle')
};

function formatDate(date) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date().toLocaleDateString('en-IN', options);
}

async function fetchData() {
    try {
        const [eventsRes, partiesRes] = await Promise.all([
            fetch(`${API_BASE}/events/today`),
            fetch(`${API_BASE}/parties`)
        ]);

        state.events = await eventsRes.json();
        state.parties = await partiesRes.json();
        
        updateUI();
    } catch (err) {
        console.error("Fetch error:", err);
        showError("Unable to fetch data. Make sure the server is running.");
    }
}

function updateUI() {
    dom.currentDate.textContent = formatDate(new Date());
    dom.lastUpdated.textContent = new Date().toLocaleTimeString();
    
    renderStats();
    renderEvents();
}

function renderStats() {
    const uniqueParties = new Set(state.events.map(e => e.party_name)).size;
    const uniqueAreas = new Set(state.events.map(e => e.location_name)).size;

    dom.statTotalEvents.textContent = state.events.length;
    dom.statPartiesActive.textContent = uniqueParties;
    dom.statAreasAffected.textContent = uniqueAreas;
}

function renderEvents() {
    if (state.events.length === 0) {
        dom.eventsContainer.innerHTML = `
            <div class="event-card glass" style="text-align: center; padding: 3rem; grid-column: 1/-1;">
                <p>No major events reported for today. Chennai is smooth!</p>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">இன்று முக்கிய நிகழ்வுகள் ஏதுமில்லை.</p>
            </div>
        `;
        return;
    }

    dom.eventsContainer.innerHTML = state.events.map(event => `
        <div class="event-card glass" onclick="window.location.href='event-details.html?id=${event.id}'">
            <span class="party-badge" style="background: ${event.party_color};">
                ${state.language === 'en' ? event.party_name : event.party_name_tamil || event.party_name}
            </span>
            <div class="event-location" style="display: flex; justify-content: space-between; align-items: flex-start;">
                <span>${state.language === 'en' ? event.location_name : event.location_tamil || event.location_name}</span>
            </div>
            <p style="margin: 0.5rem 0 1.5rem 0; font-weight: 500; font-size: 1.1rem; min-height: 3rem;">
                ${state.language === 'en' ? event.title : event.title_tamil || event.title}
            </p>
            <div class="event-time" style="padding-bottom: 1.5rem; border-bottom: 1px solid var(--glass-border); margin-bottom: 1.5rem;">
                <span>🕒 ${new Date(event.start_time).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
                <span>•</span>
                <span style="color: ${event.status === 'confirmed' ? 'var(--confirmed)' : 'var(--unverified)'}; font-weight: bold;">
                    ${event.status.toUpperCase()}
                </span>
            </div>
            <div style="display: flex; gap: 0.75rem;">
                <button class="glass" onclick="event.stopPropagation(); window.location.href='map.html?id=${event.id}'" style="padding: 0.6rem 1rem; font-size: 0.85rem; color: white; cursor: pointer; flex: 1;">
                    View on Map
                </button>
                <a href="${event.source_url}" target="_blank" onclick="event.stopPropagation()" class="glass" style="padding: 0.6rem 1rem; font-size: 0.85rem; text-decoration: none; color: white; flex: 1; text-align: center;">
                    Source
                </a>
            </div>
        </div>
    `).join('');
}

function showError(msg) {
    dom.eventsContainer.innerHTML = `
        <div class="event-card glass" style="text-align: center; padding: 3rem; border-color: var(--danger); grid-column: 1/-1;">
            <p style="color: var(--danger); font-weight: bold;">API Offline</p>
            <p style="font-size: 0.9rem; margin-top: 0.5rem;">${msg}</p>
        </div>
    `;
}

dom.langToggle.addEventListener('click', () => {
    state.language = state.language === 'en' ? 'ta' : 'en';
    dom.langToggle.textContent = state.language === 'en' ? 'EN / த' : 'த / EN';
    updateLanguage();
    renderEvents();
});

function updateLanguage() {
    const translations = {
        en: {
            title: "Namma Chennai Tracker",
            subtitle: "Helping you plan your travel during elections",
            hero: "Know Before You Go",
            home: "Home / இல்லம்",
            parties: "Parties / கட்சிகள்",
            map: "Map / வரைபடம்"
        },
        ta: {
            title: "நம்ம சென்னை ட்ராக்கர்",
            subtitle: "தேர்தல் கால பயணங்களை திட்டமிட உதவுதல்",
            hero: "போவதற்கு முன் தெரிந்துக்கொள்",
            home: "இல்லம் / Home",
            parties: "கட்சிகள் / Parties",
            map: "வரைபடம் / Map"
        }
    };
    
    const t = translations[state.language];
    document.getElementById('site-title').textContent = t.title;
    document.getElementById('site-subtitle').textContent = t.subtitle;
    document.getElementById('hero-headline').textContent = t.hero;
}

// Initial Load
fetchData();
updateLanguage();
