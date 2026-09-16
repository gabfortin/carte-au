const LEVEL_LABELS = {
  accessible: "Accessible",
  partiellement: "Partiellement accessible",
  "non-accessible": "Non accessible",
  inconnu: "Inconnu",
};

const CATEGORY_LABELS = {
  cafe: "Café",
  restaurant: "Restaurant",
  commerce: "Commerce",
  sante: "Santé",
  culture: "Culture",
  autre: "Autre",
};

const map = L.map("map").setView([45.5247742, -73.5855742], 14);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const markersById = new Map();
const markerLayer = L.layerGroup().addTo(map);
let allCommerces = [];

const listEl = document.getElementById("commerce-list");
const levelFilter = document.getElementById("filter-level");
const categoryFilter = document.getElementById("filter-category");
const searchInput = document.getElementById("search");

const LEVEL_COLORS = {
  accessible: "#2e7d32",
  partiellement: "#f9a825",
  "non-accessible": "#c62828",
  inconnu: "#757575",
};

function levelClass(level) {
  return LEVEL_LABELS[level] ? level : "inconnu";
}

function popupHtml(commerce) {
  const level = levelClass(commerce.accessibility?.level);
  const review = commerce.source?.reviewText;
  return `
    <div class="popup-content">
      <h3>${commerce.name}</h3>
      <div>${commerce.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${review ? `<div class="review">"${review}" — ${commerce.source.reviewer}</div>` : ""}
    </div>
  `;
}

function renderMarkers(commerces) {
  markerLayer.clearLayers();
  markersById.clear();
  commerces.forEach((c) => {
    if (typeof c.lat !== "number" || typeof c.lng !== "number") return;
    const level = levelClass(c.accessibility?.level);
    const marker = L.circleMarker([c.lat, c.lng], {
      radius: 8,
      color: "#fff",
      weight: 2,
      fillColor: LEVEL_COLORS[level],
      fillOpacity: 0.9,
    }).bindPopup(popupHtml(c));
    marker.addTo(markerLayer);
    markersById.set(c.id, marker);
  });
}

function renderList(commerces) {
  listEl.innerHTML = "";
  commerces.forEach((c) => {
    const level = levelClass(c.accessibility?.level);
    const li = document.createElement("li");
    li.innerHTML = `
      <span class="name">${c.name}</span>
      <span class="address">${c.address}</span>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
    `;
    li.addEventListener("click", () => {
      map.setView([c.lat, c.lng], 17);
      markersById.get(c.id)?.openPopup();
    });
    listEl.appendChild(li);
  });
}

function populateCategoryFilter(commerces) {
  const categories = [...new Set(commerces.map((c) => c.category).filter(Boolean))];
  categories.forEach((cat) => {
    const opt = document.createElement("option");
    opt.value = cat;
    opt.textContent = CATEGORY_LABELS[cat] || cat;
    categoryFilter.appendChild(opt);
  });
}

function applyFilters() {
  const level = levelFilter.value;
  const category = categoryFilter.value;
  const query = searchInput.value.trim().toLowerCase();

  const filtered = allCommerces.filter((c) => {
    const matchesLevel = level === "all" || c.accessibility?.level === level;
    const matchesCategory = category === "all" || c.category === category;
    const matchesQuery = !query || c.name.toLowerCase().includes(query) || c.address.toLowerCase().includes(query);
    return matchesLevel && matchesCategory && matchesQuery;
  });

  renderMarkers(filtered);
  renderList(filtered);
}

levelFilter.addEventListener("change", applyFilters);
categoryFilter.addEventListener("change", applyFilters);
searchInput.addEventListener("input", applyFilters);

fetch("data/commerces.json")
  .then((res) => res.json())
  .then((data) => {
    allCommerces = data.commerces || [];
    populateCategoryFilter(allCommerces);
    renderMarkers(allCommerces);
    renderList(allCommerces);
  })
  .catch((err) => {
    console.error("Erreur de chargement des données:", err);
    listEl.innerHTML = "<li>Erreur de chargement des données.</li>";
  });
