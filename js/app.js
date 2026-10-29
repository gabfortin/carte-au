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
  stationnementPayant: svgIcon('<path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>'),
  debarcadere: svgIcon('<circle cx="11" cy="4" r="1.8" fill="#fff" stroke="none"/><path d="M11 7.5v6h5l2.5 5"/><path d="M11 10h4.5"/><path d="M8 11a5.5 5.5 0 1 0 7.5 6.5"/>'),
  batiment: svgIcon('<path d="M3 9.5 12 4l9 5.5"/><path d="M5 20h14"/><path d="M6.5 11v6M10 11v6M14 11v6M17.5 11v6"/>'),
  feu: svgIcon('<path d="M4 9.5h3l5-4v13l-5-4H4z" fill="#fff"/><path d="M16 9a4 4 0 0 1 0 6M18.5 6.5a7.5 7.5 0 0 1 0 11"/>'),
  toilette: svgIcon('<path d="M8 3h8v4H8z"/><path d="M6 9a6 6 0 0 1 12 0c0 4-1.5 11-1.5 11h-9S6 13 6 9Z"/>'),
  gainCcu: svgIcon('<path d="M5 12.5l4.5 5L19 6"/>'),
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
  hlm: "HLM (OMHM)",
};

const STATIONNEMENT_TYPE_LABELS = {
  "sur-rue": "Sur rue",
  "hors-rue": "Hors rue",
};

const BATIMENT_CATEGORY_LABELS = {
  piscine: "Piscine",
  bibliotheque: "Bibliothèque",
  parc: "Parc",
  arena: "Aréna",
  "centre-sportif": "Centre sportif",
  autre: "Autre",
};

const TOILETTE_CATEGORY_LABELS = {
  parc: "Parc",
  bibliotheque: "Bibliothèque",
  "centre-communautaire": "Centre communautaire",
  commerce: "Commerce",
  "edifice-municipal": "Édifice municipal",
  piscine: "Piscine",
  arena: "Aréna",
  "centre-sportif": "Centre sportif",
  autre: "Autre",
};

const GAIN_TYPE_LABELS = {
  "logements-adaptables": "Logements adaptables",
  "acces-rampe": "Accès / rampe",
  stationnement: "Stationnement",
  toilettes: "Toilettes",
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

const NEW_TAB = `<span class="sr-only"> (s'ouvre dans un nouvel onglet)</span>`;

function field(label, value) {
  if (value === undefined || value === null || value === "") return "";
  return `<div class="popup-field"><span class="popup-field-label">${label}</span>${value}</div>`;
}

function sourceField(source) {
  if (!source?.url) return "";
  return field("Source", `<a href="${source.url}" target="_blank" rel="noopener">${source.name || "Voir la fiche"}${NEW_TAB}</a>`);
}

function reviewBlock(text, reviewer, url) {
  if (!text) return "";
  const link = url ? ` <a href="${url}" target="_blank" rel="noopener">Voir l'avis sur Google Maps${NEW_TAB}</a>` : "";
  const reviewerLabel = reviewer === "Promo-Accès"
    ? `<a class="review-source-link" href="https://promo-acces.com" target="_blank" rel="noopener">${reviewer}${NEW_TAB}</a>`
    : reviewer;
  return `<div class="review">"${text}"${reviewer ? ` — ${reviewerLabel}` : ""}${link}</div>`;
}

function imagesGallery(images) {
  if (!images?.length) return "";
  const figures = images.map(
    (img) => `
      <figure class="popup-image">
        <img src="${img.image}" alt="${img.description || ""}" loading="lazy">
        ${img.description ? `<figcaption>${img.description}</figcaption>` : ""}
      </figure>
    `
  ).join("");
  return `<div class="popup-images">${figures}</div>`;
}

function toiletteSection(toilette) {
  if (!toilette) return "";
  const level = levelClass(toilette.level);
  return `
    <div class="popup-subsection">
      <div class="popup-subsection-header">
        <span class="popup-subsection-title">Toilette</span>
        <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      </div>
      <p class="popup-subsection-notes">${toilette.notes}</p>
    </div>
  `;
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
      ${imagesGallery(c.images)}
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
      ${sourceField(l.source)}
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
      ${sourceField(s.source)}
      ${reviewBlock(s.source?.reviewText, s.source?.reviewer, s.source?.reviewUrl)}
      ${imagesGallery(s.images)}
    </div>
  `;
}

function debarcaderePopup(d) {
  return `
    <div class="popup-content">
      <h3>${d.description}</h3>
      ${d.address ? `<div class="popup-address">${d.address}</div>` : ""}
      ${field("Notes", d.notes)}
      ${streetViewField(d.lat, d.lng)}
      ${sourceField(d.source)}
      ${reviewBlock(d.source?.reviewText, d.source?.reviewer, d.source?.reviewUrl)}
      ${imagesGallery(d.images)}
    </div>
  `;
}

function streetViewField(lat, lng) {
  if (lat == null || lng == null) return "";
  const url = `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=${lat},${lng}`;
  return field("Street View", `<a href="${url}" target="_blank" rel="noopener">Voir sur Google Maps${NEW_TAB}</a>`);
}

function batimentPopup(e) {
  const level = levelClass(e.accessibility?.level);
  const a = e.accessibility || {};
  return `
    <div class="popup-content">
      <h3>${e.name}</h3>
      <div class="popup-address">${e.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${field("Catégorie", BATIMENT_CATEGORY_LABELS[e.category] || e.category)}
      ${field("Notes", a.notes)}
      ${sourceField(e.source)}
      ${reviewBlock(e.source?.reviewText, e.source?.reviewer, e.source?.reviewUrl)}
      ${toiletteSection(e.toilette)}
      ${imagesGallery(e.images)}
    </div>
  `;
}

function toilettePopup(t) {
  const level = levelClass(t.accessibility?.level);
  const a = t.accessibility || {};
  return `
    <div class="popup-content">
      <h3>${t.name}</h3>
      <div class="popup-address">${t.address}</div>
      <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      ${field("Catégorie", TOILETTE_CATEGORY_LABELS[t.category] || t.category)}
      ${field("Horaire", t.horaire)}
      ${field("Notes", a.notes)}
      ${sourceField(t.source)}
      ${reviewBlock(t.source?.reviewText, t.source?.reviewer, t.source?.reviewUrl)}
      ${imagesGallery(t.images)}
    </div>
  `;
}

function gainPopup(g) {
  return `
    <div class="popup-content">
      <h3>${g.description}</h3>
      ${g.address ? `<div class="popup-address">${g.address}</div>` : ""}
      ${field("Type de gain", GAIN_TYPE_LABELS[g.type] || g.type)}
      ${field("Date", g.date)}
      ${field("Notes", g.notes)}
      ${sourceField(g.source)}
      ${imagesGallery(g.images)}
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

function externalLink(url, text) {
  return `<a href="${url}" target="_blank" rel="noopener">${text}${NEW_TAB}</a>`;
}

const ISSUE_URL = "https://github.com/gabfortin/carte-au/issues/new?template=";

// Texte du panneau ⓘ de chaque catégorie : ce qu'elle montre, les données de
// chaque fiche et d'où elles viennent. Garder à jour avec le README.
const LAYER_INFO = {
  commerces: {
    about: "Commerces, cafés, restaurants, bars et lieux culturels dont l'accessibilité a été évaluée lors d'une visite sur place.",
    data: [
      "Niveau d'accessibilité, indiqué par la pastille de couleur du marqueur",
      "Entrée (plain-pied, rampe ou marches), porte automatique, ascenseur, mains courantes",
      "Toilettes, terrasse, salle d'essayage, terminal de paiement, menu numérique, assistance auditive",
      "Extrait de l'avis et photos, lorsque disponibles",
    ],
    process: `Chaque fiche reprend un avis d'accessibilité publié par ${externalLink("https://www.google.com/maps/contrib/100918280676331873494", "Promo-Accès sur Google Maps")}. L'avis est retranscrit à la main; un point qu'il ne mentionne pas est laissé vide.`,
    template: "ajouter-commerce.yml",
  },
  logements: {
    about: "Immeubles qui comptent des logements adaptés aux personnes à mobilité réduite.",
    data: [
      "Nombre d'unités adaptées et nombre total de logements",
      "Taille des logements, clientèle visée, ascenseur",
      "Conditions d'admissibilité, pour les HLM",
    ],
    process: `Les HLM proviennent du ${externalLink("https://www.omhm.qc.ca/fr/habitations?arrondissement_1=99", "répertoire des habitations de l'OMHM")}, qui indique les unités adaptées; leur position vient du jeu « ${externalLink("https://donnees.montreal.ca/dataset/logements-sociaux", "Logements hors marché")} » de la Ville. L'import est automatisé et d'autres logements peuvent être ajoutés à la main. Aucun registre des logements accessibles du marché privé n'existe : la liste n'est pas complète.`,
  },
  "batiments-municipaux": {
    about: "Piscines, arénas, bibliothèques, centres sportifs et autres bâtiments de la Ville et de l'arrondissement.",
    data: [
      "Niveau d'accessibilité, indiqué par la pastille de couleur du marqueur",
      "Aménagements : rampe, entrée accessible, stationnement, toilettes",
      "Section distincte sur la toilette, lorsque l'information vient d'une autre source",
      "Lien vers la fiche du lieu",
    ],
    process: `Saisie à la main à partir des fiches des lieux sur ${externalLink("https://montreal.ca/lieux", "montreal.ca")}.`,
    template: "ajouter-batiment-municipal.yml",
  },
  toilettes: {
    about: "Toilettes accessibles au public dans les parcs, bibliothèques, piscines, édifices municipaux et commerces.",
    data: [
      "Niveau d'accessibilité, indiqué par la pastille de couleur du marqueur",
      "Aménagements observés : entrée, seuils, barres d'appui, table à langer",
      "Horaire ou fermeture saisonnière",
    ],
    process: "Saisie à la main à partir d'observations faites sur place. Les notes décrivent l'état au moment de la visite (par exemple, un ascenseur en panne).",
    template: "ajouter-toilette.yml",
  },
  stationnements: {
    about: "Places de stationnement gratuites réservées aux détenteurs d'une vignette pour personnes handicapées, sur rue ou hors rue.",
    data: ["Emplacement et type (sur rue ou hors rue)", "Notes et photos, lorsque disponibles"],
    process: "Saisie à la main seulement. Les places réservées gratuites des rues résidentielles ne figurent dans aucun jeu de données ouvertes : la liste n'est pas complète.",
    template: "ajouter-stationnement.yml",
  },
  "stationnements-payants": {
    about: "Places tarifées réservées aux détenteurs d'une vignette pour personnes handicapées.",
    data: ["Emplacement", "Tarif horaire", "Panneau de signalisation associé, s'il y a lieu"],
    process: `Import automatisé des ${externalLink("https://www.agencemobilitedurable.ca/fr/informations/donnees-ouvertes/description-des-donnees-disponibles", "données ouvertes de l'Agence de mobilité durable")} (licence CC-BY 4.0), en gardant les places situées dans les limites du Plateau. Un panneau « réservé handicapés » de la Ville à moins de 15 m d'une place y est jumelé.`,
  },
  debarcaderes: {
    about: "Zones d'arrêt réservées pour faire monter ou descendre une personne handicapée.",
    data: ["Emplacement et description", "Lien Street View pour voir l'aménagement sur place"],
    process: `Saisie à la main, complétée par les panneaux « débarcadère réservé handicapés » du jeu ${externalLink("https://donnees.montreal.ca/dataset/stationnement-sur-rue-signalisation-courant", "Signalisation (stationnement sur rue)")} de la Ville, importés automatiquement.`,
    template: "ajouter-debarcadere.yml",
  },
  "feux-sonores": {
    about: "Intersections dont les feux pour piétons émettent un signal sonore, pour les personnes aveugles ou malvoyantes.",
    data: ["Intersection et arrondissement", "Type d'installation (permanente ou temporaire)"],
    process: `Import automatisé des ${externalLink("https://donnees.montreal.ca/dataset/feux-malvoyants", "données ouvertes de la Ville de Montréal")}. Le jeu couvre toute la ville : les feux des arrondissements voisins sont aussi affichés.`,
  },
  "gains-ccu": {
    about: "Améliorations de l'accessibilité obtenues lors de l'étude de projets immobiliers par le comité consultatif d'urbanisme (CCU) de l'arrondissement, par exemple une proportion de logements adaptables ou une rampe d'accès.",
    data: ["Description et type de gain", "Projet ou adresse concernés, date", "Lien vers la résolution du CCU, lorsque disponible"],
    process: "Saisie à la main au fil des séances du CCU. Le nom de cette catégorie est provisoire.",
    template: "ajouter-gain-ccu.yml",
  },
};

function layerInfoHtml(config) {
  const info = LAYER_INFO[config.key];
  const contribute = info.template
    ? `<p class="layer-info-contribute">Vous connaissez un lieu à ajouter? ${externalLink(ISSUE_URL + info.template, "Proposer un ajout sur GitHub")} (compte requis).</p>`
    : "";
  return `
    <h3 id="layer-info-title">${config.label}</h3>
    <p>${info.about}</p>
    <h4>Données affichées</h4>
    <ul>${info.data.map((d) => `<li>${d}</li>`).join("")}</ul>
    <h4>Provenance et traitement</h4>
    <p>${info.process}</p>
    ${contribute}
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
    // Saisie manuelle + immeubles de l'OMHM avec unités adaptées.
    files: ["data/logements.json", "data/logements-omhm.json"],
    defaultVisible: true,
    color: ["#4ade80", "#15803d"],
    icon: ICONS.logement,
    getItems: (data) => data.logements || [],
    getPopup: logementPopup,
  },
  {
    key: "batiments-municipaux",
    label: "Bâtiments municipaux accessibles",
    file: "data/batiments-municipaux.json",
    defaultVisible: true,
    color: ["#c084fc", "#7016b0"],
    icon: ICONS.batiment,
    getItems: (data) => data.batiments || [],
    getBadge: (item) => LEVEL_COLORS[levelClass(item.accessibility?.level)],
    getPopup: batimentPopup,
  },
  {
    key: "toilettes",
    label: "Toilettes accessibles",
    file: "data/toilettes.json",
    defaultVisible: true,
    color: ["#2dd4bf", "#0f766e"],
    icon: ICONS.toilette,
    getItems: (data) => data.toilettes || [],
    getBadge: (item) => LEVEL_COLORS[levelClass(item.accessibility?.level)],
    getPopup: toilettePopup,
  },
  {
    key: "stationnements",
    label: "Stationnement accessible",
    // Saisie manuelle uniquement.
    file: "data/stationnements.json",
    defaultVisible: true,
    color: ["#3b82f6", "#1e3a8a"],
    icon: ICONS.stationnement,
    size: 28,
    getItems: (data) => data.stationnements || [],
    getPopup: stationnementPopup,
  },
  {
    key: "stationnements-payants",
    label: "Stationnement accessible payant",
    // Places tarifées importées de l'Agence de mobilité durable.
    file: "data/places-handicapes.json",
    defaultVisible: true,
    color: ["#3b82f6", "#1e3a8a"],
    icon: ICONS.stationnementPayant,
    size: 28,
    getItems: (data) => data.stationnements || [],
    getPopup: stationnementPopup,
  },
  {
    key: "debarcaderes",
    label: "Débarcadères accessibles",
    files: ["data/debarcaderes.json", "data/places-handicapes.json"],
    defaultVisible: true,
    color: ["#3b82f6", "#1e3a8a"],
    icon: ICONS.debarcadere,
    size: 28,
    getItems: (data) => data.debarcaderes || [],
    getPopup: debarcaderePopup,
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
  {
    key: "gains-ccu",
    label: "Gains CCU",
    file: "data/gains-ccu.json",
    defaultVisible: true,
    color: ["#fbbf24", "#b45309"],
    icon: ICONS.gainCcu,
    getItems: (data) => data.gains || [],
    getPopup: gainPopup,
  },
];

const map = L.map("map", { zoomControl: false, attributionControl: false }).setView([45.5247742, -73.5855742], 14);

L.control.zoom({ position: "bottomright", zoomInTitle: "Zoom avant", zoomOutTitle: "Zoom arrière" }).addTo(map);
L.control.attribution({ position: "bottomright" }).addTo(map);

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  className: "map-tiles-muted",
}).addTo(map);

const SAFE_MARGIN = 12;

function headerBottom() {
  return document.querySelector(".site-header").getBoundingClientRect().bottom;
}

// Zone de la carte réellement visible : sous l'en-tête flottant et, sur ordinateur,
// à droite du panneau latéral quand il est ouvert.
function visibleMapArea() {
  const sidebarRight = !isMobile() && isSidebarOpen() ? document.getElementById("sidebar").getBoundingClientRect().right : 0;
  return {
    top: headerBottom() + SAFE_MARGIN,
    left: sidebarRight + SAFE_MARGIN,
    right: window.innerWidth - SAFE_MARGIN,
    bottom: window.innerHeight - SAFE_MARGIN,
  };
}

// Déplace la carte pour que la popup ouverte ne soit ni hors champ ni cachée sous
// l'en-tête ou le panneau. Si elle est trop grande, on garde son haut et sa gauche visibles.
function keepPopupInView(popup) {
  const rect = popup.getElement().getBoundingClientRect();
  const area = visibleMapArea();
  let dx = 0;
  let dy = 0;
  if (rect.right > area.right) dx = rect.right - area.right;
  if (rect.left - dx < area.left) dx = rect.left - area.left;
  if (rect.bottom > area.bottom) dy = rect.bottom - area.bottom;
  if (rect.top - dy < area.top) dy = rect.top - area.top;
  if (dx || dy) map.panBy([dx, dy]);
}

// Ouverte au clavier (ou depuis la recherche), la fiche reçoit le focus pour être lue par
// les lecteurs d'écran; à la fermeture, le focus revient sur le marqueur.
let focusPopupOnOpen = false;

map.on("popupopen", (e) => {
  const el = e.popup.getElement();
  const closeBtn = el.querySelector(".leaflet-popup-close-button");
  closeBtn?.setAttribute("aria-label", "Fermer la fiche");
  const content = el.querySelector(".popup-content");
  content?.setAttribute("tabindex", "-1");
  el.setAttribute("role", "dialog");
  const title = content?.querySelector("h3");
  if (title) {
    title.id ||= `popup-title-${L.stamp(e.popup)}`;
    el.setAttribute("aria-labelledby", title.id);
  }
  const markerEl = e.popup._source?.getElement?.();
  if (focusPopupOnOpen || (markerEl && markerEl === document.activeElement)) content?.focus({ preventScroll: true });
  focusPopupOnOpen = false;
  requestAnimationFrame(() => keepPopupInView(e.popup));
});

map.on("popupclose", (e) => {
  const markerEl = e.popup._source?.getElement?.();
  const active = document.activeElement;
  const focusWasInPopup = !active || active === document.body || e.popup.getElement()?.contains(active);
  if (markerEl && focusWasInPopup) markerEl.focus({ preventScroll: true });
});

function markerIcon(config, badgeColor, offset) {
  const [light, dark] = config.color;
  const style = `--pin-light:${light};--pin-dark:${dark}`;
  const badge = badgeColor ? `<span class="pin-badge" style="background:${badgeColor}"></span>` : "";
  const [dx, dy] = offset || [0, 0];
  if (config.compact) {
    return L.divIcon({
      className: "",
      html: `<div class="pin-marker dot-marker" style="width:18px;height:18px"><div class="pin" style="${style}">${config.icon}</div></div>`,
      iconSize: [18, 18],
      iconAnchor: [9 - dx, 9 - dy],
      popupAnchor: [dx, -9 + dy],
    });
  }
  // Goutte de 34px (comme Avant / Après) pivotée de -45° : la pointe se retrouve ~41px sous le coin haut.
  // Les proportions (ancre, pointe) sont conservées au prorata pour les tailles réduites.
  const size = config.size || 34;
  const sizeClass = size !== 34 ? " pin-marker-sm" : "";
  const anchorX = size / 2;
  const anchorY = Math.round((size * 41) / 34);
  const popupY = -Math.round((size * 39) / 34);
  // Décalage purement visuel (quelques px) quand un marqueur partage exactement les
  // coordonnées d'un autre : la position géographique réelle (lat/lng) n'est jamais
  // modifiée, seul le rendu de la goutte sur l'écran est déplacé. Voir computeMarkerOffsets().
  return L.divIcon({
    className: "",
    html: `<div class="pin-marker${sizeClass}" style="width:${size}px;height:${size}px"><div class="pin" style="${style}">${config.icon}</div>${badge}</div>`,
    iconSize: [size, size],
    iconAnchor: [anchorX - dx, anchorY - dy],
    popupAnchor: [dx, popupY + dy],
  });
}

// Quand deux lieux de couches différentes partagent exactement les mêmes coordonnées
// (ex : la toilette d'un bâtiment municipal, à la même adresse que le bâtiment), leurs
// gouttes se superposent pile l'une sur l'autre. On les éloigne visuellement de
// quelques pixels en éventail autour du point réel, sans jamais toucher au lat/lng
// stocké : calculé une fois que toutes les couches sont chargées (voir plus bas).
let markerOffsets = new Map();
const MARKER_OFFSET_RADIUS = 9;

function computeMarkerOffsets(layerResults) {
  const groups = new Map();
  layerResults.forEach(({ config, items }) => {
    items.forEach((item) => {
      if (typeof item.lat !== "number" || typeof item.lng !== "number") return;
      const coordKey = `${item.lat.toFixed(6)},${item.lng.toFixed(6)}`;
      const markerKey = `${config.key}:${item.id}`;
      const list = groups.get(coordKey) || [];
      list.push(markerKey);
      groups.set(coordKey, list);
    });
  });

  const offsets = new Map();
  groups.forEach((markerKeys) => {
    if (markerKeys.length < 2) return;
    markerKeys.sort();
    markerKeys.forEach((markerKey, i) => {
      const angle = (2 * Math.PI * i) / markerKeys.length;
      offsets.set(markerKey, [
        Math.round(Math.cos(angle) * MARKER_OFFSET_RADIUS),
        Math.round(Math.sin(angle) * MARKER_OFFSET_RADIUS),
      ]);
    });
  });
  return offsets;
}

const layerGroups = new Map(LAYER_CONFIG.map((c) => [c.key, L.layerGroup()]));
const markersById = new Map(); // commerces only, pour le lien résultats de recherche <-> carte
let allCommerces = [];

const searchInput = document.getElementById("search");
const searchResultsEl = document.getElementById("search-results");
const layerTogglesEl = document.getElementById("layer-toggles");

// Sur téléphone, la popup prend la largeur de l'écran moins les marges, et défile
// si elle est plus haute que l'espace sous l'en-tête.
function popupOptions() {
  const width = window.innerWidth - 2 * SAFE_MARGIN;
  return {
    maxWidth: Math.min(420, width),
    minWidth: Math.min(340, width),
    maxHeight: window.innerHeight - headerBottom() - 4 * SAFE_MARGIN,
    autoPan: false, // remplacé par keepPopupInView, qui tient compte de l'en-tête et du panneau
  };
}

function renderLayerMarkers(config, items) {
  const group = layerGroups.get(config.key);
  group.clearLayers();
  if (config.key === "commerces") markersById.clear();

  items.forEach((item) => {
    if (typeof item.lat !== "number" || typeof item.lng !== "number") return;
    const badgeColor = config.getBadge?.(item);
    const offset = markerOffsets.get(`${config.key}:${item.id}`);
    const marker = L.marker([item.lat, item.lng], { icon: markerIcon(config, badgeColor, offset) }).bindPopup(config.getPopup(item), popupOptions());
    // Le marqueur est un bouton (Leaflet) sans texte : on lui donne un nom qui inclut
    // la catégorie et le niveau d'accessibilité, sinon indiqué seulement par la couleur.
    const markerLabel = markerName(config, item);
    marker.on("add", () => marker.getElement()?.setAttribute("aria-label", markerLabel));
    marker.addTo(group);
    if (config.key === "commerces") markersById.set(item.id, marker);
  });
}

function markerName(config, item) {
  const name = item.name || item.description || item.intersection || "Lieu";
  const parts = [name, config.label];
  if (config.getBadge) parts.push(LEVEL_LABELS[levelClass(item.accessibility?.level)]);
  return parts.join(" — ");
}

const MAX_SEARCH_RESULTS = 20;

const searchStatusEl = document.getElementById("search-status");

function selectCommerce(c) {
  hideSearchResults();
  searchInput.value = c.name;
  map.setView([c.lat, c.lng], 17, { animate: false });
  const marker = markersById.get(c.id);
  if (marker) {
    focusPopupOnOpen = true;
    marker.openPopup();
  }
}

function renderSearchResults(commerces) {
  searchResultsEl.innerHTML = "";

  if (!commerces.length) {
    searchResultsEl.innerHTML = `<li class="search-empty">Aucun commerce trouvé.</li>`;
    searchStatusEl.textContent = "Aucun commerce trouvé.";
    return;
  }

  const shown = commerces.slice(0, MAX_SEARCH_RESULTS);
  searchStatusEl.textContent =
    commerces.length === 1
      ? "1 commerce trouvé. Utilisez la flèche du bas pour parcourir les résultats."
      : `${commerces.length} commerces trouvés${commerces.length > shown.length ? `, ${shown.length} affichés` : ""}. Utilisez la flèche du bas pour parcourir les résultats.`;

  shown.forEach((c) => {
    const level = levelClass(c.accessibility?.level);
    const li = document.createElement("li");
    li.innerHTML = `
      <button type="button">
        <span class="name">${c.name}</span>
        <span class="address">${c.address}</span>
        <span class="badge ${level}">${LEVEL_LABELS[level]}</span>
      </button>
    `;
    li.querySelector("button").addEventListener("click", () => selectCommerce(c));
    searchResultsEl.appendChild(li);
  });
}

// Flèches haut/bas pour passer du champ aux résultats et d'un résultat à l'autre.
function searchResultButtons() {
  return [...searchResultsEl.querySelectorAll("button")];
}

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "ArrowDown" && !searchResultsEl.hidden) {
    e.preventDefault();
    searchResultButtons()[0]?.focus();
  }
});

searchResultsEl.addEventListener("keydown", (e) => {
  const buttons = searchResultButtons();
  const index = buttons.indexOf(document.activeElement);
  if (index === -1) return;
  if (e.key === "ArrowDown") {
    e.preventDefault();
    buttons[Math.min(index + 1, buttons.length - 1)].focus();
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    (index === 0 ? searchInput : buttons[index - 1]).focus();
  } else if (e.key === "Escape") {
    hideSearchResults();
    searchInput.focus();
  }
});

// Les résultats se ferment quand on tabule hors de la zone de recherche (le clic
// ailleurs est géré plus bas; relatedTarget est vide lors d'un clic dans Safari).
document.querySelector(".header-search").addEventListener("focusout", (e) => {
  if (e.relatedTarget && !e.currentTarget.contains(e.relatedTarget)) hideSearchResults();
});

function showSearchResults() {
  searchResultsEl.hidden = false;
}

function hideSearchResults() {
  searchResultsEl.hidden = true;
}

function applySearch() {
  const query = searchInput.value.trim().toLowerCase();

  const filtered = allCommerces.filter((c) => {
    const categoryLabel = CATEGORY_LABELS[c.category] || c.category || "";
    return (
      !query ||
      c.name.toLowerCase().includes(query) ||
      c.address.toLowerCase().includes(query) ||
      categoryLabel.toLowerCase().includes(query)
    );
  });

  renderLayerMarkers(LAYER_CONFIG[0], filtered);

  if (query) {
    renderSearchResults(filtered);
    showSearchResults();
  } else {
    hideSearchResults();
    searchStatusEl.textContent = "";
  }
}

searchInput.addEventListener("input", applySearch);
searchInput.addEventListener("focus", () => {
  if (searchInput.value.trim()) showSearchResults();
});

document.addEventListener("click", (e) => {
  if (!e.target.closest(".header-search")) hideSearchResults();
});

searchInput.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !searchResultsEl.hidden) {
    e.preventDefault();
    hideSearchResults();
  }
});

// Au début d'une recherche, on désactive les autres couches pour ne garder que
// les commerces à l'écran, en notant celles qui étaient actives pour les
// resélectionner quand la recherche se termine (champ vidé).
let searchWasEmpty = true;
let layersBeforeSearch = [];
searchInput.addEventListener("input", () => {
  const isEmpty = !searchInput.value.trim();

  if (searchWasEmpty && !isEmpty) {
    layersBeforeSearch = [...layerTogglesEl.querySelectorAll("input")]
      .filter((input) => input.dataset.layer !== "commerces" && input.checked)
      .map((input) => input.dataset.layer);
    layerTogglesEl.querySelectorAll("input").forEach((input) => {
      if (input.dataset.layer === "commerces" || !input.checked) return;
      input.checked = false;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  } else if (!searchWasEmpty && isEmpty) {
    layerTogglesEl.querySelectorAll("input").forEach((input) => {
      if (input.dataset.layer === "commerces") return;
      const shouldBeChecked = layersBeforeSearch.includes(input.dataset.layer);
      if (input.checked === shouldBeChecked) return;
      input.checked = shouldBeChecked;
      input.dispatchEvent(new Event("change", { bubbles: true }));
    });
  }

  searchWasEmpty = isEmpty;
});

// La recherche ne concerne que les commerces : on la masque quand cette couche est désactivée.
function setCommercesUiVisible(visible) {
  document.documentElement.classList.toggle("commerces-hidden", !visible);
}

function buildLayerToggles() {
  LAYER_CONFIG.forEach((config) => {
    const group = layerGroups.get(config.key);
    if (config.defaultVisible) group.addTo(map);

    const li = document.createElement("li");
    const [light, dark] = config.color;
    li.innerHTML = `
      <label>
        <input type="checkbox" data-layer="${config.key}" ${config.defaultVisible ? "checked" : ""} />
        <span class="swatch" style="background:linear-gradient(140deg, ${light}, ${dark})">${config.icon}</span>
        <span class="layer-label">${config.label}</span>
        <span class="layer-count"><span id="layer-count-${config.key}">–</span><span class="sr-only"> lieux</span></span>
      </label>
      <button type="button" class="layer-info-btn" data-layer-info="${config.key}" aria-label="Information sur la catégorie ${config.label}" aria-haspopup="dialog" aria-expanded="false" aria-controls="layer-info">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true" focusable="false">
          <circle cx="12" cy="12" r="9.5" stroke="currentColor" stroke-width="1.6"/>
          <circle cx="12" cy="7.8" r="1.2" fill="currentColor"/>
          <path d="M12 11v5.8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>
    `;
    li.querySelector(".layer-info-btn").addEventListener("click", (e) => toggleLayerInfo(config, e.currentTarget));
    li.querySelector("input").addEventListener("change", (e) => {
      if (e.target.checked) {
        group.addTo(map);
      } else {
        map.removeLayer(group);
      }
      if (config.key === "commerces") setCommercesUiVisible(e.target.checked);
    });
    if (config.key === "commerces") setCommercesUiVisible(config.defaultVisible);
    layerTogglesEl.appendChild(li);
  });
}

// Panneau ⓘ : non modal, il reçoit le focus à l'ouverture et le rend au bouton à la
// fermeture (Échap, ✕, clic ailleurs). Tab au-delà du panneau reprend dans la liste.
const layerInfoEl = document.getElementById("layer-info");
const layerInfoBody = document.getElementById("layer-info-body");
const layerInfoClose = document.getElementById("layer-info-close");
let layerInfoTrigger = null;

function positionLayerInfo() {
  if (!layerInfoTrigger) return;
  const gap = 12;
  const btn = layerInfoTrigger.getBoundingClientRect();
  const sidebarRight = document.getElementById("sidebar").getBoundingClientRect().right;
  const { offsetWidth: w, offsetHeight: h } = layerInfoEl;
  let left;
  let top;
  if (sidebarRight + gap + w <= window.innerWidth - gap) {
    // À droite du panneau latéral, aligné sur la catégorie.
    left = sidebarRight + gap;
    top = btn.top - 14;
  } else {
    // Pas la place (téléphone) : sous la catégorie, ou au-dessus si l'écran est trop court.
    left = btn.right - w;
    top = btn.bottom + 6 + h <= window.innerHeight - gap ? btn.bottom + 6 : btn.top - 6 - h;
  }
  layerInfoEl.style.left = `${Math.max(gap, Math.min(left, window.innerWidth - w - gap))}px`;
  layerInfoEl.style.top = `${Math.max(gap, Math.min(top, window.innerHeight - h - gap))}px`;
}

function openLayerInfo(config, trigger) {
  if (layerInfoTrigger) layerInfoTrigger.setAttribute("aria-expanded", "false");
  layerInfoTrigger = trigger;
  layerInfoBody.innerHTML = layerInfoHtml(config);
  layerInfoClose.setAttribute("aria-label", `Fermer l'information sur ${config.label}`);
  layerInfoEl.hidden = false;
  trigger.setAttribute("aria-expanded", "true");
  positionLayerInfo();
  layerInfoEl.scrollTop = 0;
  layerInfoEl.focus();
}

function closeLayerInfo({ restoreFocus = true } = {}) {
  if (!layerInfoTrigger) return;
  const trigger = layerInfoTrigger;
  layerInfoTrigger = null;
  layerInfoEl.hidden = true;
  trigger.setAttribute("aria-expanded", "false");
  if (restoreFocus) trigger.focus();
}

function toggleLayerInfo(config, trigger) {
  if (layerInfoTrigger === trigger) closeLayerInfo();
  else openLayerInfo(config, trigger);
}

layerInfoClose.addEventListener("click", () => closeLayerInfo());

layerInfoEl.addEventListener("keydown", (e) => {
  if (e.key === "Escape") {
    e.stopPropagation(); // ne pas fermer aussi le panneau latéral sur téléphone
    closeLayerInfo();
    return;
  }
  if (e.key !== "Tab") return;
  const focusables = [...layerInfoEl.querySelectorAll("button, a[href]")];
  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  if (e.shiftKey && (document.activeElement === first || document.activeElement === layerInfoEl)) {
    e.preventDefault();
    closeLayerInfo();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    const controls = [...document.getElementById("sidebar").querySelectorAll("input, button:not(.sidebar-close)")];
    const next = controls[controls.indexOf(layerInfoTrigger) + 1];
    closeLayerInfo({ restoreFocus: !next });
    next?.focus();
  }
});

document.addEventListener("click", (e) => {
  if (layerInfoTrigger && !layerInfoEl.contains(e.target) && !e.target.closest(".layer-info-btn")) {
    closeLayerInfo({ restoreFocus: false });
  }
});

window.addEventListener("resize", positionLayerInfo);
document.getElementById("sidebar").addEventListener("scroll", positionLayerInfo);

buildLayerToggles();

// Bascule entre « Tout désélectionner » (au moins une couche active) et
// « Tout sélectionner » (aucune couche active).
const layersClearBtn = document.getElementById("layers-clear");

function anyLayerChecked() {
  return layerTogglesEl.querySelector("input:checked") !== null;
}

function updateLayersClearLabel() {
  layersClearBtn.textContent = anyLayerChecked() ? "Tout désélectionner" : "Tout sélectionner";
}

layersClearBtn.addEventListener("click", () => {
  const check = !anyLayerChecked();
  layerTogglesEl.querySelectorAll("input").forEach((input) => {
    if (input.checked === check) return;
    input.checked = check;
    input.dispatchEvent(new Event("change"));
  });
  updateLayersClearLabel();
});

layerTogglesEl.addEventListener("change", updateLayersClearLabel);
updateLayersClearLabel();

const sidebarEl = document.getElementById("sidebar");
const sidebarScrim = document.getElementById("sidebar-scrim");
const sidebarToggle = document.getElementById("sidebar-toggle");

function isMobile() {
  return window.matchMedia("(max-width: 760px)").matches;
}

function isSidebarOpen() {
  return isMobile() ? sidebarEl.classList.contains("open") : !document.body.classList.contains("sidebar-collapsed");
}

// Panneau fermé : retiré de l'ordre de tabulation et des lecteurs d'écran (inert).
function syncSidebarState() {
  const open = isSidebarOpen();
  sidebarEl.inert = !open;
  sidebarToggle.setAttribute("aria-expanded", String(open));
}

function openSidebar() {
  if (isMobile()) {
    sidebarEl.classList.add("open");
    sidebarScrim.classList.add("open");
  } else {
    document.body.classList.remove("sidebar-collapsed");
  }
  syncSidebarState();
  // Sur téléphone, le panneau recouvre la carte : on y place le focus.
  if (isMobile()) layerTogglesEl.querySelector("input")?.focus();
}

function closeSidebar() {
  const hadFocus = sidebarEl.contains(document.activeElement) || layerInfoEl.contains(document.activeElement);
  closeLayerInfo({ restoreFocus: false });
  if (isMobile()) {
    sidebarEl.classList.remove("open");
    sidebarScrim.classList.remove("open");
  } else {
    document.body.classList.add("sidebar-collapsed");
  }
  syncSidebarState();
  if (hadFocus) sidebarToggle.focus();
}

sidebarToggle.addEventListener("click", () => (isSidebarOpen() ? closeSidebar() : openSidebar()));
document.getElementById("sidebar-close").addEventListener("click", closeSidebar);
sidebarScrim.addEventListener("click", closeSidebar);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && isMobile() && isSidebarOpen()) closeSidebar();
});
window.matchMedia("(max-width: 760px)").addEventListener("change", syncSidebarState);
syncSidebarState();

// Le lien d'évitement « Passer aux catégories » ouvre le panneau s'il est fermé.
document.querySelector('.skip-link[href="#sidebar"]').addEventListener("click", (e) => {
  e.preventDefault();
  if (!isSidebarOpen()) openSidebar();
  layerTogglesEl.querySelector("input")?.focus();
});

const aboutOverlay = document.getElementById("about-overlay");

const aboutBtn = document.getElementById("about-btn");
// Pendant que la fenêtre est ouverte, le reste de la page est inerte : le focus y reste.
const backgroundEls = [".skip-link", ".site-header", "#sidebar", "#map"].flatMap((sel) => [...document.querySelectorAll(sel)]);

function openAbout() {
  closeLayerInfo({ restoreFocus: false });
  aboutOverlay.classList.add("open");
  aboutOverlay.inert = false;
  backgroundEls.forEach((el) => (el.inert = true));
  document.getElementById("about-modal-close").focus();
}

function closeAbout() {
  aboutOverlay.classList.remove("open");
  aboutOverlay.inert = true;
  backgroundEls.forEach((el) => (el.inert = false));
  syncSidebarState();
  aboutBtn.focus();
}

aboutBtn.addEventListener("click", openAbout);
document.getElementById("about-modal-close").addEventListener("click", closeAbout);
aboutOverlay.addEventListener("click", (e) => {
  if (e.target === aboutOverlay) closeAbout();
});
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && aboutOverlay.classList.contains("open")) closeAbout();
});

// On attend que toutes les couches soient chargées avant de poser les marqueurs, pour
// pouvoir détecter les lieux qui partagent exactement les mêmes coordonnées entre
// couches (ex : bâtiment municipal et sa toilette) et les décaler visuellement.
Promise.all(
  LAYER_CONFIG.map((config) => {
    const files = config.files || [config.file];
    return Promise.all(files.map((file) => fetch(file).then((res) => res.json())))
      .then((datasets) => ({ config, items: datasets.flatMap((data) => config.getItems(data)) }))
      .catch((err) => {
        console.error(`Erreur de chargement (${files.join(", ")}):`, err);
        return { config, items: [] };
      });
  })
).then((layerResults) => {
  markerOffsets = computeMarkerOffsets(layerResults);
  layerResults.forEach(({ config, items }) => {
    document.getElementById(`layer-count-${config.key}`).textContent = items.length;
    if (config.key === "commerces") allCommerces = items;
    renderLayerMarkers(config, items);
  });
});
