const LEVEL_LABELS = {
  accessible: "Accessible",
  partiellement: "Partiellement accessible",
  "non-accessible": "Non accessible",
  inconnu: "Inconnu",
};

const LEVEL_COLORS = {
  accessible: "#2e7d32",
  partiellement: "#f9a825",
  "non-accessible": "#c62828",
  inconnu: "#757575",
};

const CATEGORY_LABELS = {
  cafe: "Café",
  restaurant: "Restaurant",
  commerce: "Commerce",
  sante: "Santé",
  culture: "Culture",
  autre: "Autre",
};

function levelClass(level) {
  return LEVEL_LABELS[level] ? level : "inconnu";
}

function commercePopup(c) {
  const level = levelClass(c.accessibility?.level);
  const review = c.source?.reviewText;
  return `
    <div class="popup-content">
      <h3>${c.name}</h3>
      <div>${c.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${review ? `<div class="review">"${review}" — ${c.source.reviewer}</div>` : ""}
    </div>
  `;
}

function logementPopup(l) {
  return `
    <div class="popup-content">
      <h3>${l.name}</h3>
      <div>${l.address}</div>
      ${l.accessibility?.notes ? `<div class="review">${l.accessibility.notes}</div>` : ""}
    </div>
  `;
}

function stationnementPopup(s) {
  return `
    <div class="popup-content">
      <h3>${s.description}</h3>
      ${s.address ? `<div>${s.address}</div>` : ""}
      ${s.notes ? `<div class="review">${s.notes}</div>` : ""}
    </div>
  `;
}

function equipementPopup(e) {
  return `
    <div class="popup-content">
      <h3>${e.name}</h3>
      <div>${e.address}</div>
      ${e.accessibility?.notes ? `<div class="review">${e.accessibility.notes}</div>` : ""}
    </div>
  `;
}

function feuSonorePopup(f) {
  return `
    <div class="popup-content">
      <h3>${f.intersection}</h3>
      ${f.arrondissement ? `<div>${f.arrondissement}</div>` : ""}
      ${f.statut ? `<div class="review">Statut : ${f.statut}</div>` : ""}
    </div>
  `;
}

const LAYER_CONFIG = [
  {
    key: "commerces",
    label: "Commerces accessibles",
    file: "data/commerces.json",
    defaultVisible: true,
    color: "#2e7d32",
    getItems: (data) => data.commerces || [],
    getColor: (item) => LEVEL_COLORS[levelClass(item.accessibility?.level)],
    getPopup: commercePopup,
  },
  {
    key: "logements",
    label: "Logements accessibles",
    file: "data/logements.json",
    defaultVisible: false,
    color: "#1565c0",
    getItems: (data) => data.logements || [],
    getColor: () => "#1565c0",
    getPopup: logementPopup,
  },
  {
    key: "stationnements",
    label: "Stationnements accessibles",
    file: "data/stationnements.json",
    defaultVisible: false,
    color: "#6a1b9a",
    getItems: (data) => data.stationnements || [],
    getColor: () => "#6a1b9a",
    getPopup: stationnementPopup,
  },
  {
    key: "equipements",
    label: "Équipements accessibles",
    file: "data/equipements.json",
    defaultVisible: false,
    color: "#00838f",
    getItems: (data) => data.equipements || [],
    getColor: () => "#00838f",
    getPopup: equipementPopup,
  },
  {
    key: "feux-sonores",
    label: "Feux sonores (malvoyants)",
    file: "data/feux-sonores.json",
    defaultVisible: false,
    color: "#e65100",
    getItems: (data) => data.feuxSonores || [],
    getColor: () => "#e65100",
    getPopup: feuSonorePopup,
  },
];

const map = L.map("map").setView([45.5247742, -73.5855742], 14);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

const layerGroups = new Map(LAYER_CONFIG.map((c) => [c.key, L.layerGroup()]));
const markersById = new Map(); // commerces only, pour le lien liste <-> carte
let allCommerces = [];

const listEl = document.getElementById("commerce-list");
const levelFilter = document.getElementById("filter-level");
const categoryFilter = document.getElementById("filter-category");
const searchInput = document.getElementById("search");
const layerTogglesEl = document.getElementById("layer-toggles");

function renderLayerMarkers(config, items) {
  const group = layerGroups.get(config.key);
  group.clearLayers();
  if (config.key === "commerces") markersById.clear();

  items.forEach((item) => {
    if (typeof item.lat !== "number" || typeof item.lng !== "number") return;
    const marker = L.circleMarker([item.lat, item.lng], {
      radius: 7,
      color: "#fff",
      weight: 2,
      fillColor: config.getColor(item),
      fillOpacity: 0.9,
    }).bindPopup(config.getPopup(item));
    marker.addTo(group);
    if (config.key === "commerces") markersById.set(item.id, marker);
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

  renderLayerMarkers(LAYER_CONFIG[0], filtered);
  renderList(filtered);
}

levelFilter.addEventListener("change", applyFilters);
categoryFilter.addEventListener("change", applyFilters);
searchInput.addEventListener("input", applyFilters);

function buildLayerToggles() {
  LAYER_CONFIG.forEach((config) => {
    const group = layerGroups.get(config.key);
    if (config.defaultVisible) group.addTo(map);

    const li = document.createElement("li");
    const id = `layer-toggle-${config.key}`;
    li.innerHTML = `
      <input type="checkbox" id="${id}" ${config.defaultVisible ? "checked" : ""} />
      <span class="swatch" style="background:${config.color}"></span>
      <label for="${id}">${config.label}</label>
    `;
    li.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) {
        group.addTo(map);
      } else {
        map.removeLayer(group);
      }
    });
    layerTogglesEl.appendChild(li);
  });
}

buildLayerToggles();

LAYER_CONFIG.forEach((config) => {
  fetch(config.file)
    .then((res) => res.json())
    .then((data) => {
      const items = config.getItems(data);
      if (config.key === "commerces") {
        allCommerces = items;
        populateCategoryFilter(allCommerces);
        renderLayerMarkers(config, allCommerces);
        renderList(allCommerces);
      } else {
        renderLayerMarkers(config, items);
      }
    })
    .catch((err) => {
      console.error(`Erreur de chargement (${config.file}):`, err);
      if (config.key === "commerces") {
        listEl.innerHTML = "<li>Erreur de chargement des données.</li>";
      }
    });
});
