const LEVEL_LABELS = {
  accessible: "Accessible",
  partiellement: "Partiellement accessible",
  "non-accessible": "Non accessible",
  inconnu: "Inconnu",
};

// Pastille du niveau d'accessibilité, posée sur le coin des marqueurs de commerce.
const LEVEL_COLORS = {
  accessible: "#2563eb",
  partiellement: "#f59e0b",
  "non-accessible": "#e11d48",
  inconnu: "#64748b",
};

// Pictogrammes blancs (trait) affichés dans les marqueurs et les pastilles des couches.
function svgIcon(paths) {
  return `<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths}</svg>`;
}

const ICONS = {
  commerce: svgIcon('<path d="M5 8h14l-1.2 12H6.2L5 8Z"/><path d="M9 10V6a3 3 0 0 1 6 0v4"/>'),
  logement: svgIcon('<path d="M3.5 11 12 4l8.5 7"/><path d="M6 9.5V20h12V9.5"/><path d="M10 20v-5h4v5"/>'),
  stationnement: svgIcon('<path d="M8 20V4h5.5a4.5 4.5 0 0 1 0 9H8"/>'),
  equipement: svgIcon('<path d="M3 9.5 12 4l9 5.5"/><path d="M5 20h14"/><path d="M6.5 11v6M10 11v6M14 11v6M17.5 11v6"/>'),
  feu: svgIcon('<path d="M4 9.5h3l5-4v13l-5-4H4z" fill="#fff"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11"/>'),
};

const CATEGORY_LABELS = {
  cafe: "Café",
  bar: "Bar",
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

function reviewBlock(text, reviewer, url) {
  if (!text) return "";
  const link = url ? ` <a href="${url}" target="_blank" rel="noopener">Voir l'avis sur Google Maps</a>` : "";
  return `<div class="review">"${text}"${reviewer ? ` — ${reviewer}` : ""}${link}</div>`;
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
      ${field("Porte automatique", boolLabel(a.porteAutomatique))}
      ${field("Animaux d'assistance", boolLabel(a.animauxAssistance))}
      ${field("Mains courantes", boolLabel(a.mainsCourantes))}
      ${field("Étages", a.etages)}
      ${field("Ascenseur / monte-charge", boolLabel(a.ascenseur))}
      ${field("Salle d'essayage accessible", boolLabel(a.salleEssayage))}
      ${field("Mobilier amovible", boolLabel(a.mobilierAmovible))}
      ${field("Terrasse accessible", boolLabel(a.terrasseAccessible))}
      ${field("Terminal de paiement", a.terminalPaiement)}
      ${field("Menu numérique", boolLabel(a.menuNumerique))}
      ${field("Assistance auditive", boolLabel(a.assistanceAuditive))}
      ${field("Toilettes accessibles", boolLabel(a.toilettes))}
      ${field("Stationnement", boolLabel(a.stationnement))}
      ${field("Notes", a.notes)}
      ${reviewBlock(c.source?.reviewText, c.source?.reviewer, c.source?.reviewUrl)}
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
      ${reviewBlock(l.source?.reviewText, l.source?.reviewer, l.source?.reviewUrl)}
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
      ${reviewBlock(s.source?.reviewText, s.source?.reviewer, s.source?.reviewUrl)}
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
      ${reviewBlock(e.source?.reviewText, e.source?.reviewer, e.source?.reviewUrl)}
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
    color: ["#7dd3fc", "#0284c7"],
    icon: ICONS.commerce,
    getItems: (data) => data.commerces || [],
    getBadge: (item) => LEVEL_COLORS[levelClass(item.accessibility?.level)],
    getPopup: commercePopup,
  },
  {
    key: "logements",
    label: "Logements accessibles",
    file: "data/logements.json",
    defaultVisible: true,
    color: ["#4ade80", "#15803d"],
    icon: ICONS.logement,
    getItems: (data) => data.logements || [],
    getPopup: logementPopup,
  },
  {
    key: "stationnements",
    label: "Stationnements accessibles",
    file: "data/stationnements.json",
    defaultVisible: true,
    color: ["#3b82f6", "#1e3a8a"],
    icon: ICONS.stationnement,
    getItems: (data) => data.stationnements || [],
    getPopup: stationnementPopup,
  },
  {
    key: "equipements",
    label: "Équipements accessibles",
    file: "data/equipements.json",
    defaultVisible: true,
    color: ["#c084fc", "#7016b0"],
    icon: ICONS.equipement,
    getItems: (data) => data.equipements || [],
    getPopup: equipementPopup,
  },
  {
    key: "feux-sonores",
    label: "Feux sonores",
    file: "data/feux-sonores.json",
    defaultVisible: true,
    color: ["#f87171", "#b91c1c"],
    icon: ICONS.feu,
    getItems: (data) => data.feuxSonores || [],
    getPopup: feuSonorePopup,
    compact: true,
  },
];

const map = L.map("map", { zoomControl: false, attributionControl: false }).setView([45.5247742, -73.5855742], 14);

L.control.zoom({ position: "bottomright" }).addTo(map);
L.control.attribution({ position: "bottomright" }).addTo(map);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  className: "map-tiles-muted",
}).addTo(map);

function markerIcon(config, badgeColor) {
  const [light, dark] = config.color;
  const style = `--pin-light:${light};--pin-dark:${dark}`;
  const badge = badgeColor ? `<span class="pin-badge" style="background:${badgeColor}"></span>` : "";
  if (config.compact) {
    return L.divIcon({
      className: "",
      html: `<div class="pin-marker dot-marker" style="width:18px;height:18px"><div class="pin" style="${style}">${config.icon}</div></div>`,
      iconSize: [18, 18],
      iconAnchor: [9, 9],
      popupAnchor: [0, -9],
    });
  }
  // Goutte de 34px (comme Avant / Après) pivotée de -45° : la pointe se retrouve ~41px sous le coin haut.
  return L.divIcon({
    className: "",
    html: `<div class="pin-marker" style="width:34px;height:34px"><div class="pin" style="${style}">${config.icon}</div>${badge}</div>`,
    iconSize: [34, 34],
    iconAnchor: [17, 41],
    popupAnchor: [0, -39],
  });
}

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
    const badgeColor = config.getBadge?.(item);
    const marker = L.marker([item.lat, item.lng], { icon: markerIcon(config, badgeColor) }).bindPopup(config.getPopup(item), { maxWidth: 420, minWidth: 340 });
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
      if (isMobile()) closeSidebar();
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
    const [light, dark] = config.color;
    li.innerHTML = `
      <label>
        <input type="checkbox" ${config.defaultVisible ? "checked" : ""} />
        <span class="swatch" style="background:linear-gradient(140deg, ${light}, ${dark})">${config.icon}</span>
        <span class="layer-label">${config.label}</span>
        <span class="layer-count" id="layer-count-${config.key}">–</span>
      </label>
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

const sidebarEl = document.getElementById("sidebar");
const sidebarScrim = document.getElementById("sidebar-scrim");
const sidebarToggle = document.getElementById("sidebar-toggle");

function isMobile() {
  return window.matchMedia("(max-width: 760px)").matches;
}

function isSidebarOpen() {
  return isMobile() ? sidebarEl.classList.contains("open") : !document.body.classList.contains("sidebar-collapsed");
}

function openSidebar() {
  if (isMobile()) {
    sidebarEl.classList.add("open");
    sidebarScrim.classList.add("open");
  } else {
    document.body.classList.remove("sidebar-collapsed");
  }
  sidebarToggle.setAttribute("aria-expanded", "true");
}

function closeSidebar() {
  if (isMobile()) {
    sidebarEl.classList.remove("open");
    sidebarScrim.classList.remove("open");
  } else {
    document.body.classList.add("sidebar-collapsed");
  }
  sidebarToggle.setAttribute("aria-expanded", "false");
}

sidebarToggle.addEventListener("click", () => (isSidebarOpen() ? closeSidebar() : openSidebar()));
document.getElementById("sidebar-close").addEventListener("click", closeSidebar);
sidebarScrim.addEventListener("click", closeSidebar);
sidebarToggle.setAttribute("aria-expanded", String(isSidebarOpen()));

const aboutOverlay = document.getElementById("about-overlay");

function openAbout() {
  aboutOverlay.classList.add("open");
}

function closeAbout() {
  aboutOverlay.classList.remove("open");
}

document.getElementById("about-btn").addEventListener("click", openAbout);
document.getElementById("about-modal-close").addEventListener("click", closeAbout);
aboutOverlay.addEventListener("click", (e) => {
  if (e.target === aboutOverlay) closeAbout();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && aboutOverlay.classList.contains("open")) closeAbout();
});

const STAT_ELEMENTS = {
  commerces: document.getElementById("stat-commerces"),
  "feux-sonores": document.getElementById("stat-feux"),
};

LAYER_CONFIG.forEach((config) => {
  fetch(config.file)
    .then((res) => res.json())
    .then((data) => {
      const items = config.getItems(data);
      document.getElementById(`layer-count-${config.key}`).textContent = items.length;
      if (STAT_ELEMENTS[config.key]) STAT_ELEMENTS[config.key].textContent = items.length;
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
