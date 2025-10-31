
# This script scans a folder of PNG map images that follow specific naming patterns,
# extracts species, period, and scenario metadata from the filenames,
# and generates a single static HTML page with dropdown filters to view the images.
#
# It writes the output to /mnt/data/map_gallery.html and uses relative paths.
import os, re, json
from urllib.parse import quote  # for GBIF URL encoding

INPUT_DIR = "C:/MyFiles/R-dev/OneSTOP_Outputs/OneSTOP_SDM_Map_Gallery/imgs"
OUTPUT_HTML = "C:/MyFiles/R-dev/OneSTOP_Outputs/OneSTOP_SDM_Map_Gallery/index.html"

pat = re.compile(
    r"^sdm_map_([a-z]+_[a-z]+)__((hist)_bin_|(\d{4}_\d{4})_(ssp(?:126|370|585))_bin_)\.png$"
)

def title_case_species(s):
    parts = s.split("_")
    return " ".join([parts[0].capitalize(), parts[1].lower()])

def pretty_period(period_token):
    if period_token == "hist":
        return "Historical (1971–2024)"
    if "_" in period_token:
        a, b = period_token.split("_")
        return f"{a}–{b}"
    return period_token

def scenario_label(ssp):
    mapping = {"ssp126":"SSP1 / RCP2.6", "ssp370":"SSP3 / RCP7.0", "ssp585":"SSP5 / RCP8.5"}
    return mapping.get(ssp, ssp.upper())

def period_sort_key(label):
    order = {"Historical (1971–2024)": 0, "Historical": 0, "2041–2070": 1, "2071–2100": 2}
    return order.get(label, 99), label

def scenario_sort_key(code):
    order = {"ssp126":0, "ssp370":1, "ssp585":2}
    return order.get(code, 99), code

entries = []
for fname in sorted(os.listdir(INPUT_DIR)):
    m = pat.match(fname)
    if not m:
        continue
    species_token = m.group(1)
    period_token = "hist" if m.group(3) else m.group(4)
    ssp_token = m.group(5) if m.group(5) else None

    species_display = title_case_species(species_token)
    gbif_url = f"https://www.gbif.org/species/search?q={quote(species_display)}"

    entry = {
        "id": fname,
        "file": fname,
        "path": f"imgs/{fname}", # fname,
        "species_token": species_token,
        "species": species_display,
        "gbif": gbif_url,
        "period_token": period_token,
        "period": pretty_period(period_token if period_token == "hist" else period_token),
        "scenario": ssp_token,
        "scenario_label": (scenario_label(ssp_token) if ssp_token else "—"),
    }
    entries.append(entry)

entries.sort(key=lambda e: (e["species"], period_sort_key(e["period"]), scenario_sort_key(e["scenario"] or "")))

data_json = json.dumps(entries)

# Template with floating "Go to top" button
TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Map Gallery – SDM PNG Browser</title>
<style>
  :root {
    --bg: #0b1220;
    --card: #111827;
    --muted: #9aa4b2;
    --text: #e5e7eb;
    --chip: #1f2937;
    --border: #1d283a;
    --accent: #22c55e;
  }
  * { box-sizing: border-box; }
  html, body { height: 100%; scroll-behavior: smooth; }
  body {
    margin: 0;
    font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    background: radial-gradient(1000px 600px at 10% -20%, #1f2937 0%, #0b1220 30%), var(--bg);
    color: var(--text);
    min-height: 100%;
  }
  header { padding: 32px 24px 8px; max-width: 1200px; margin: 0 auto; }
  h1 { margin: 0; font-size: clamp(22px, 2.8vw, 36px); }
  p.sub { margin: 6px 0 0; color: var(--muted); }
  .controls {
    margin: 18px auto 12px;
    display: grid;
    grid-template-columns: repeat(12, 1fr);
    gap: 12px;
    max-width: 1200px;
    padding: 0 24px;
  }
  .control { grid-column: span 12; }
  @media (min-width: 720px) { .control { grid-column: span 4; } }
  label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 6px; }
  select {
    width: 100%; background: var(--card); border: 1px solid var(--border); color: var(--text);
    padding: 10px 12px; border-radius: 12px; outline: none;
  }
  .gallery {
    max-width: 1200px; padding: 16px 24px 80px; margin: 0 auto;
    display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px;
  }
  .card {
    background: linear-gradient(180deg, #0e1626, #0c1320);
    border: 1px solid var(--border); border-radius: 16px; overflow: hidden;
    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    transition: transform .2s ease, box-shadow .2s ease;
    cursor: zoom-in;
  }
  .card:hover { transform: translateY(-3px); box-shadow: 0 16px 28px rgba(0,0,0,0.28); }
  .card img { width: 100%; height: 220px; object-fit: cover; display: block; background: #0b1220; }
  .meta { padding: 12px 14px 14px; display: grid; gap: 6px; }

  .sp a {
  font-weight: 600;
  font-style: italic;   /* <-- NEW */
  color: var(--text);
  text-decoration: none;
  }
  .sp a:hover {
    text-decoration: underline;
    color: var(--accent);
  }

  .row { font-size: 13px; color: var(--muted); display:flex; gap:8px; flex-wrap:wrap; }
  .chip { background: var(--chip); border: 1px solid #293447; padding: 4px 8px; border-radius: 999px; font-size: 12px; }
  .empty { text-align:center; color: var(--muted); padding: 24px; grid-column: 1/-1; }

  /* Floating Go-to-top button */
  #toTop {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 50%;
    width: 44px;
    height: 44px;
    font-size: 22px;
    font-weight: bold;
    cursor: pointer;
    display: none;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    transition: background 0.2s, transform 0.2s;
    z-index: 10000;
  }
  #toTop:hover { background: #16a34a; transform: translateY(-2px); }

  /* Lightbox modal */
  .modal {
    position: fixed; inset: 0; background: rgba(0,0,0,0.75);
    display: none; align-items: center; justify-content: center; z-index: 9999;
    backdrop-filter: blur(2px);
  }
  .modal.open { display: flex; }
  .modal-content {
    position: relative; max-width: 90vw; max-height: 90vh;
    box-shadow: 0 25px 50px rgba(0,0,0,.35); border-radius: 12px; overflow: hidden;
    background: #0b1220; padding: 10px;
  }
  .modal img { display: block; max-width: 90vw; max-height: 85vh; object-fit: contain; }
  .modal .caption {
    font-size: 12px; color: #cbd5e1; margin-top: 8px; text-align: center;
  }
  .modal .close {
    position: absolute; top: 8px; right: 10px; background: rgba(17,24,39,.8);
    border: 1px solid #334155; color: #e5e7eb; border-radius: 999px; padding: 6px 10px; cursor: pointer;
  }
  .modal .nav {
    position: absolute; top: 50%; transform: translateY(-50%); background: rgba(17,24,39,.7);
    border: 1px solid #334155; color: #e5e7eb; border-radius: 999px; padding: 8px 12px; cursor: pointer;
    user-select: none;
  }
  .modal .prev { left: 8px; }
  .modal .next { right: 8px; }
</style>
</head>
<body>
<header>
  <h1>OneSTOP | IAS Distribution Model Map Gallery</h1>
   <p class="sub">Click any thumbnail to view a larger map. Use ESC or the × button to close; use ← → to navigate.</p>
   <p class="sub">Green areas represent potential distribution with suitable climate/land cover conditions</p>
</header>

<section class="controls">
  <div class="control">
    <label for="species">Species</label>
    <select id="species"></select>
  </div>
  <div class="control">
    <label for="period">Period</label>
    <select id="period" disabled></select>
  </div>
  <div class="control">
    <label for="scenario">Scenario</label>
    <select id="scenario" disabled></select>
  </div>
</section>

<section class="gallery" id="gallery"></section>

<!-- Lightbox modal -->
<div class="modal" id="lightbox" aria-hidden="true">
  <div class="modal-content">
    <button class="close" id="closeBtn" aria-label="Close">×</button>
    <button class="nav prev" id="prevBtn" aria-label="Previous">‹</button>
    <button class="nav next" id="nextBtn" aria-label="Next">›</button>
    <img id="lightboxImg" alt="Large map">
    <div class="caption" id="lightboxCap"></div>
  </div>
</div>

<!-- Go-to-top button -->
<button id="toTop" title="Go to top">↑</button>

<script>
// Data injected below to avoid f-string brace issues
const DATA = __DATA_JSON__;

const speciesSelect = document.getElementById('species');
const periodSelect = document.getElementById('period');
const scenarioSelect = document.getElementById('scenario');
const gallery = document.getElementById('gallery');
const toTopBtn = document.getElementById('toTop');
const ALL = '__ALL__';

// Scroll-to-top logic
window.addEventListener('scroll', () => {
  if (document.documentElement.scrollTop > 300 || document.body.scrollTop > 300) {
    toTopBtn.style.display = 'block';
  } else {
    toTopBtn.style.display = 'none';
  }
});
toTopBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

function uniqueSpecies() {
  return Array.from(new Set(DATA.map(d => d.species))).sort((a,b)=>a.localeCompare(b));
}
function periodsForSpecies(sp) {
  const set = new Set(DATA.filter(d => d.species===sp).map(d => d.period));
  const order = {"Historical (1971–2024)":0,"Historical":0,"2041–2070":1,"2071–2100":2};
  return Array.from(set).sort((a,b)=>(order[a]??99)-(order[b]??99)||a.localeCompare(b));
}
function scenariosFor(sp, period) {
  const set = new Set(DATA.filter(d => d.species===sp && d.period===period && d.scenario).map(d => d.scenario));
  const order = {ssp126:0, ssp370:1, ssp585:2};
  return Array.from(set).sort((a,b)=>(order[a]??99)-(order[b]??99));
}
function labelScenario(code) {
  const m = {ssp126:"SSP1 / RCP2.6", ssp370:"SSP3 / RCP7.0", ssp585:"SSP5 / RCP8.5"};
  return m[code] || "—";
}
function setOptions(sel, options, placeholder, disable = false) {
  sel.innerHTML = '';
  const ph = document.createElement('option');
  ph.value = ALL; ph.textContent = placeholder; sel.appendChild(ph);
  for (const opt of options) { const el=document.createElement('option'); el.value=opt; el.textContent=opt; sel.appendChild(el); }
  sel.disabled = disable;
}

// Initialize dropdowns
setOptions(speciesSelect, uniqueSpecies(), 'All species', false);
setOptions(periodSelect, [], 'Select a species first', true);
setOptions(scenarioSelect, [], 'Select a period', true);

// Dropdown change logic
speciesSelect.addEventListener('change', () => {
  const sp = speciesSelect.value;
  if (sp === ALL) {
    setOptions(periodSelect, [], 'Select a species first', true);
    setOptions(scenarioSelect, [], 'Select a period', true);
  } else {
    setOptions(periodSelect, periodsForSpecies(sp), 'All periods', false);
    setOptions(scenarioSelect, [], 'Select a period', true);
  }
  render();
});
periodSelect.addEventListener('change', () => {
  const sp = speciesSelect.value;
  const period = periodSelect.value;
  if (period === ALL) {
    setOptions(scenarioSelect, [], 'Select a period', true);
  } else if (period.toLowerCase().startsWith('historical')) {
    setOptions(scenarioSelect, [], 'Not applicable for historical', true);
  } else {
    const scs = scenariosFor(sp, period);
    scenarioSelect.innerHTML = '';
    const ph = document.createElement('option'); ph.value = ALL; ph.textContent = 'All scenarios'; scenarioSelect.appendChild(ph);
    for (const s of scs) { const o=document.createElement('option'); o.value=s; o.textContent=labelScenario(s); scenarioSelect.appendChild(o); }
    scenarioSelect.disabled = false;
  }
  render();
});
scenarioSelect.addEventListener('change', render);

function sortEntries(a,b) {
  const orderP = {"Historical (1971–2024)":0,"Historical":0,"2041–2070":1,"2071–2100":2};
  const orderS = {ssp126:0, ssp370:1, ssp585:2};
  return a.species.localeCompare(b.species) ||
         (orderP[a.period]??99)-(orderP[b.period]??99) ||
         (orderS[a.scenario]??99)-(orderS[b.scenario]??99);
}

// Lightbox state
let currentIndex = -1;
let currentItems = [];

function openLightbox(idx) {
  currentIndex = idx;
  const d = currentItems[currentIndex];
  const modal = document.getElementById('lightbox');
  const img = document.getElementById('lightboxImg');
  const cap = document.getElementById('lightboxCap');
  img.src = d.path;
  img.alt = d.species + ' – ' + d.period + (d.scenario?(' – '+labelScenario(d.scenario)):''); 
  cap.textContent = d.species + ' • ' + d.period + (d.scenario?(' • '+labelScenario(d.scenario)):''); 
  modal.classList.add('open');
  modal.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}
function closeLightbox() {
  const modal = document.getElementById('lightbox');
  modal.classList.remove('open');
  modal.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
  currentIndex = -1;
}
function navLightbox(delta) {
  if (currentIndex < 0) return;
  const next = currentIndex + delta;
  if (next < 0 || next >= currentItems.length) return;
  openLightbox(next);
}

document.getElementById('closeBtn').addEventListener('click', closeLightbox);
document.getElementById('prevBtn').addEventListener('click', () => navLightbox(-1));
document.getElementById('nextBtn').addEventListener('click', () => navLightbox(1));
document.getElementById('lightbox').addEventListener('click', (e) => { if (e.target.id === 'lightbox') closeLightbox(); });
window.addEventListener('keydown', (e) => {
  const modalOpen = document.getElementById('lightbox').classList.contains('open');
  if (!modalOpen) return;
  if (e.key === 'Escape') closeLightbox();
  if (e.key === 'ArrowLeft') navLightbox(-1);
  if (e.key === 'ArrowRight') navLightbox(1);
});

function render() {
  const sp = speciesSelect.value;
  const period = periodSelect.value;
  const scenario = scenarioSelect.value;
  let items = DATA.slice();
  if (sp !== ALL) items = items.filter(d => d.species===sp);
  if (period !== ALL && periodSelect.disabled === false) items = items.filter(d => d.period===period);
  if (!scenarioSelect.disabled && scenario !== ALL) items = items.filter(d => d.scenario===scenario);
  items.sort(sortEntries);
  currentItems = items;
  gallery.innerHTML = '';
  if (items.length === 0) {
    const div = document.createElement('div'); div.className='empty'; div.textContent='No images match the current filters.'; gallery.appendChild(div); return;
  }
  items.forEach((d, idx) => {
    const card = document.createElement('div'); card.className = 'card';
    const img = document.createElement('img');
    img.loading='lazy'; img.src=d.path; img.alt=d.species + ' – ' + d.period + (d.scenario?(' – '+labelScenario(d.scenario)):''); 
    const meta = document.createElement('div'); meta.className='meta';

    // Species name as GBIF link
    const spn = document.createElement('div'); spn.className='sp';
    const a = document.createElement('a');
    a.href = d.gbif;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    a.textContent = d.species;
    spn.appendChild(a);

    const row = document.createElement('div'); row.className='row';
    const c1=document.createElement('span'); c1.className='chip'; c1.textContent=d.period; row.appendChild(c1);
    if (d.scenario) { const c2=document.createElement('span'); c2.className='chip'; c2.textContent=labelScenario(d.scenario); row.appendChild(c2); }

    meta.appendChild(spn); 
    meta.appendChild(row);
    card.appendChild(img); 
    card.appendChild(meta);
    card.addEventListener('click', () => openLightbox(idx));
    gallery.appendChild(card);
  });
}

render();
</script>
</body>
</html>
"""

html_content = TEMPLATE.replace("__DATA_JSON__", data_json)

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Wrote:", OUTPUT_HTML)
