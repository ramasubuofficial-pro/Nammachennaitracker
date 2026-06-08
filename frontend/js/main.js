const API_BASE = "https://nammachennaitracker.onrender.com/api";

const state = {
    allEvents: [],
    filteredEvents: [],
    parties: [],
    language: 'en'
};

const dom = {
    eventsContainer: document.getElementById('events-container'),
    statTotalEvents: document.getElementById('stat-total-events'),
    statPartiesActive: document.getElementById('stat-parties-active'),
    statAreasAffected: document.getElementById('stat-areas-affected'),
    currentDate: document.getElementById('current-date'),
    lastUpdated: document.getElementById('last-updated-timestamp'),
    langToggle: document.getElementById('lang-toggle'),
    filterParty: document.getElementById('filter-party'),
    filterArea: document.getElementById('filter-area'),
    searchPlace: document.getElementById('search-place'),
    filterDate: document.getElementById('filter-date')
};

function formatDate(date) {
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    return new Date().toLocaleDateString('en-IN', options);
}

async function fetchData() {
    try {
        const [eventsRes, partiesRes] = await Promise.all([
            fetch(`${API_BASE}/events/upcoming`),
            fetch(`${API_BASE}/parties`)
        ]);

        state.allEvents = await eventsRes.json();
        state.parties = await partiesRes.json();
        
        // Populate party select dropdown
        dom.filterParty.innerHTML = `<option value="all" id="opt-all-parties">${state.language === 'en' ? 'All Parties' : 'அனைத்து கட்சிகள்'}</option>` +
            state.parties.map(p => `<option value="${p.name}">${state.language === 'en' ? p.name : p.name_tamil || p.name}</option>`).join('');

        // Populate area select dropdown
        populateAreas();
        
        // Default filter date to today's date in local time
        const tzoffset = (new Date()).getTimezoneOffset() * 60000; // offset in milliseconds
        const localISODate = (new Date(Date.now() - tzoffset)).toISOString().split('T')[0];
        dom.filterDate.value = localISODate;

        updateUI();
    } catch (err) {
        console.error("Fetch error:", err);
        showError("Unable to fetch data. Make sure the server is running.");
    }
}

function populateAreas() {
    const uniqueAreas = [...new Set(state.allEvents.map(e => e.location_name))].sort();
    dom.filterArea.innerHTML = `<option value="all" id="opt-all-areas">${state.language === 'en' ? 'All Areas' : 'அனைத்து பகுதிகள்'}</option>` +
        uniqueAreas.map(a => `<option value="${a}">${a}</option>`).join('');
}

function updateUI() {
    dom.currentDate.textContent = formatDate(new Date());
    dom.lastUpdated.textContent = new Date().toLocaleTimeString();
    
    updateLanguage();
    filterAndRenderEvents();
}

function filterAndRenderEvents() {
    const selectedParty = dom.filterParty.value;
    const selectedArea = dom.filterArea.value;
    const searchVal = dom.searchPlace.value.trim().toLowerCase();
    const selectedDateVal = dom.filterDate.value; // YYYY-MM-DD
    
    let filtered = state.allEvents;
    
    // 1. Party Filter
    if (selectedParty !== 'all') {
        filtered = filtered.filter(e => e.party_name === selectedParty);
    }
    
    // 2. Area Filter
    if (selectedArea !== 'all') {
        filtered = filtered.filter(e => e.location_name === selectedArea);
    }
    
    // 3. Location/Text Search
    if (searchVal) {
        filtered = filtered.filter(e => 
            e.location_name.toLowerCase().includes(searchVal) || 
            (e.location_tamil && e.location_tamil.toLowerCase().includes(searchVal)) ||
            e.title.toLowerCase().includes(searchVal) ||
            (e.title_tamil && e.title_tamil.toLowerCase().includes(searchVal))
        );
    }
    
    // 4. Date Filter
    if (selectedDateVal) {
        filtered = filtered.filter(e => {
            const eventStartStr = e.start_time.split('T')[0];
            const eventEndStr = e.end_time.split('T')[0];
            return eventStartStr === selectedDateVal || eventEndStr === selectedDateVal;
        });
    }
    
    state.filteredEvents = filtered;
    renderEvents();
    renderStats();
}

function renderStats() {
    const uniqueParties = new Set(state.filteredEvents.map(e => e.party_name)).size;
    const uniqueAreas = new Set(state.filteredEvents.map(e => e.location_name)).size;

    dom.statTotalEvents.textContent = state.filteredEvents.length;
    dom.statPartiesActive.textContent = uniqueParties;
    dom.statAreasAffected.textContent = uniqueAreas;
}

function renderEvents() {
    if (state.filteredEvents.length === 0) {
        dom.eventsContainer.innerHTML = `
            <div class="event-card glass" style="text-align: center; padding: 3rem; grid-column: 1/-1;">
                <p>No upcoming events matching your search filters.</p>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">வடிகட்டலுக்குப் பொருத்தமான நிகழ்வுகள் ஏதுமில்லை.</p>
            </div>
        `;
        return;
    }

    dom.eventsContainer.innerHTML = state.filteredEvents.map(event => {
        const partyObj = state.parties.find(p => p.name === event.party_name);
        const partyTamil = partyObj ? partyObj.name_tamil : event.party_name;
        
        return `
            <div class="event-card glass" onclick="window.location.href='event-details.html?id=${event.id}'">
                <span class="party-badge" style="background: ${event.party_color};">
                    ${state.language === 'en' ? event.party_name : partyTamil}
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
        `;
    }).join('');
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
    filterAndRenderEvents();
});

function updateLanguage() {
    const translations = {
        en: {
            title: "Namma Chennai Tracker",
            subtitle: "Helping you plan your travel during elections",
            hero: "Know Before You Go",
            home: "Home / இல்லம்",
            parties: "Parties / கட்சிகள்",
            map: "Map / வரைபடம்",
            filterBy: "Filter by:",
            allParties: "All Parties",
            allAreas: "All Areas",
            searchPlace: "Search by place...",
            totalEventsLabel: "Total Events Found",
            partiesActiveLabel: "Parties Active",
            areasAffectedLabel: "Areas Affected"
        },
        ta: {
            title: "நம்ம சென்னை ட்ராக்கர்",
            subtitle: "தேர்தல் கால பயணங்களை திட்டமிட உதவுதல்",
            hero: "போவதற்கு முன் தெரிந்துக்கொள்",
            home: "இல்லம் / Home",
            parties: "கட்சிகள் / Parties",
            map: "வரைபடம் / Map",
            filterBy: "வடிகட்டு:",
            allParties: "அனைத்து கட்சிகள்",
            allAreas: "அனைத்து பகுதிகள்",
            searchPlace: "இடம் தேடுக...",
            totalEventsLabel: "கண்டறியப்பட்ட நிகழ்வுகள்",
            partiesActiveLabel: "செயலில் உள்ள கட்சிகள்",
            areasAffectedLabel: "பாதிக்கப்பட்ட பகுதிகள்"
        }
    };
    
    const t = translations[state.language];
    document.getElementById('site-title').textContent = t.title;
    document.getElementById('site-subtitle').textContent = t.subtitle;
    document.getElementById('hero-headline').textContent = t.hero;
    
    document.getElementById('label-filter-by').textContent = t.filterBy;
    
    const optParties = document.getElementById('opt-all-parties');
    if (optParties) optParties.textContent = t.allParties;
    
    const optAreas = document.getElementById('opt-all-areas');
    if (optAreas) optAreas.textContent = t.allAreas;
    
    dom.searchPlace.placeholder = t.searchPlace;
    
    const labels = document.querySelectorAll('.stat-card .stat-label');
    if (labels.length === 3) {
        labels[0].textContent = t.totalEventsLabel;
        labels[1].textContent = t.partiesActiveLabel;
        labels[2].textContent = t.areasAffectedLabel;
    }
}

// Wire up event listeners
dom.filterParty.addEventListener('change', filterAndRenderEvents);
dom.filterArea.addEventListener('change', filterAndRenderEvents);
dom.searchPlace.addEventListener('input', filterAndRenderEvents);
dom.filterDate.addEventListener('change', filterAndRenderEvents);

// Initial Load
fetchData();
