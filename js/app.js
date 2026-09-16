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
  friperie: "Friperie",
  sante: "Santé",
  culture: "Culture",
  autre: "Autre",
};

const ENTREE_LABELS = {
  "plain-pied": "Plain-pied",
  rampe: "Rampe",
  marche: "Marche(s)",
  inconnu: "Inconnu",
};

const LOGEMENT_TYPE_LABELS = {
  locatif: "Locatif",
  condo: "Condo",
  residence: "Résidence",
};

const STATIONNEMENT_TYPE_LABELS = {
  "sur-rue": "Sur rue",
  "hors-rue": "Hors rue",
};

const EQUIPEMENT_CATEGORY_LABELS = {
  piscine: "Piscine",
  bibliotheque: "Bibliothèque",
  parc: "Parc",
  arena: "Aréna",
  autre: "Autre",
};

function levelClass(level) {
  return LEVEL_LABELS[level] ? level : "inconnu";
}

const BOOL_STRING_LABELS = {
  "non-verifie": "Non vérifié lors de la visite",
};

function boolLabel(value) {
  if (value === true) return "Oui";
  if (value === false) return "Non";
  if (typeof value === "string" && value) return BOOL_STRING_LABELS[value] || value;
  return null;
}

function field(label, value) {
  if (value === undefined || value === null || value === "") return "";
  return `<div class="popup-field"><span class="popup-field-label">${label}</span>${value}</div>`;
}

function reviewBlock(text, reviewer) {
  if (!text) return "";
  return `<div class="review">"${text}"${reviewer ? ` — ${reviewer}` : ""}</div>`;
}

function commercePopup(c) {
  const level = levelClass(c.accessibility?.level);
  const a = c.accessibility || {};
  return `
    <div class="popup-content">
      <h3>${c.name}</h3>
      <div class="popup-address">${c.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${field("Catégorie", CATEGORY_LABELS[c.category] || c.category)}
      ${field("Entrée", ENTREE_LABELS[a.entree] || a.entree)}
      ${field("Animaux d'assistance", boolLabel(a.animauxAssistance))}
      ${field("Mains courantes", boolLabel(a.mainsCourantes))}
      ${field("Étages", a.etages)}
      ${field("Ascenseur / monte-charge", boolLabel(a.ascenseur))}
      ${field("Salle d'essayage accessible", boolLabel(a.salleEssayage))}
      ${field("Terminal de paiement", a.terminalPaiement)}
      ${field("Assistance auditive", boolLabel(a.assistanceAuditive))}
      ${field("Toilettes accessibles", boolLabel(a.toilettes))}
      ${field("Stationnement", boolLabel(a.stationnement))}
      ${field("Notes", a.notes)}
      ${reviewBlock(c.source?.reviewText, c.source?.reviewer)}
    </div>
  `;
}

function logementPopup(l) {
  const level = levelClass(l.accessibility?.level);
  const a = l.accessibility || {};
  return `
    <div class="popup-content">
      <h3>${l.name}</h3>
      <div class="popup-address">${l.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${field("Type", LOGEMENT_TYPE_LABELS[l.type] || l.type)}
      ${field("Entrée", ENTREE_LABELS[a.entree] || a.entree)}
      ${field("Ascenseur", boolLabel(a.ascenseur))}
      ${field("Notes", a.notes)}
      ${reviewBlock(l.source?.reviewText, l.source?.reviewer)}
    </div>
  `;
}

function stationnementPopup(s) {
  return `
    <div class="popup-content">
      <h3>${s.description}</h3>
      ${s.address ? `<div class="popup-address">${s.address}</div>` : ""}
      ${field("Type", STATIONNEMENT_TYPE_LABELS[s.type] || s.type)}
      ${field("Notes", s.notes)}
      ${reviewBlock(s.source?.reviewText, s.source?.reviewer)}
    </div>
  `;
}

function equipementPopup(e) {
  const level = levelClass(e.accessibility?.level);
  const a = e.accessibility || {};
  return `
    <div class="popup-content">
      <h3>${e.name}</h3>
      <div class="popup-address">${e.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${field("Catégorie", EQUIPEMENT_CATEGORY_LABELS[e.category] || e.category)}
      ${field("Notes", a.notes)}
      ${reviewBlock(e.source?.reviewText, e.source?.reviewer)}
    </div>
  `;
}

function feuSonorePopup(f) {
  return `
    <div class="popup-content">
      <h3>${f.intersection}</h3>
      ${field("Arrondissement", f.arrondissement)}
      ${field("Type", f.statut)}
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
    defaultVisible: true,
    color: "#1565c0",
    getItems: (data) => data.logements || [],
    getColor: () => "#1565c0",
    getPopup: logementPopup,
  },
  {
    key: "stationnements",
    label: "Stationnements accessibles",
    file: "data/stationnements.json",
    defaultVisible: true,
    color: "#6a1b9a",
    getItems: (data) => data.stationnements || [],
    getColor: () => "#6a1b9a",
    getPopup: stationnementPopup,
  },
  {
    key: "equipements",
    label: "Équipements accessibles",
    file: "data/equipements.json",
    defaultVisible: true,
    color: "#00838f",
    getItems: (data) => data.equipements || [],
    getColor: () => "#00838f",
    getPopup: equipementPopup,
  },
  {
    key: "feux-sonores",
    label: "Feux sonores (malvoyants)",
    file: "data/feux-sonores.json",
    defaultVisible: true,
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
