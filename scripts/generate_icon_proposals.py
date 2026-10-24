import os
import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg
import cairo

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

DESIGNS = {}

# 1. Layered Deck (Átlapolt Füllapok)
DESIGNS["design-1"] = {
    "name": "1. Layered Deck (Átlapolt Füllapok)",
    "subtitle": "Klasszikus több-füles böngészőkártyák modern rétegződéssel",
    "description": "Három egymást átfedő, lebegő lapka mélységi árnyékokkal és azonosító színpontokkal. Közvetlen, letisztult szimbóluma a párhuzamosan futó webes munkameneteknek.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0b1329"/>
      <stop offset="100%" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="card-back" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e3a8a"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
    <linearGradient id="card-mid" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <linearGradient id="card-front" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="70%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <filter id="shadow-1" x="-10%" y="-10%" width="130%" height="130%">
      <feDropShadow dx="0" dy="12" stdDeviation="16" flood-color="#000000" flood-opacity="0.5"/>
    </filter>
  </defs>
  <!-- Háttér Squircle -->
  <rect width="512" height="512" rx="112" fill="url(#bg-1)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#334155" stroke-width="4" opacity="0.6"/>

  <!-- Hátsó fül kártya -->
  <g filter="url(#shadow-1)">
    <rect x="170" y="80" width="230" height="270" rx="28" fill="url(#card-back)" stroke="#3b82f6" stroke-width="2" opacity="0.7" transform="rotate(8 285 215)"/>
  </g>

  <!-- Középső fül kártya -->
  <g filter="url(#shadow-1)">
    <rect x="130" y="110" width="240" height="280" rx="30" fill="url(#card-mid)" stroke="#60a5fa" stroke-width="3" opacity="0.9" transform="rotate(-4 250 250)"/>
  </g>

  <!-- Elülső aktív fül ablak -->
  <g filter="url(#shadow-1)">
    <rect x="100" y="140" width="270" height="280" rx="32" fill="url(#card-front)"/>
    <rect x="100" y="140" width="270" height="280" rx="32" fill="none" stroke="#bae6fd" stroke-width="3" opacity="0.8"/>
    <!-- Ablak fejléc -->
    <rect x="100" y="140" width="270" height="64" rx="32" fill="#0f172a" opacity="0.35"/>
    <!-- Fejléc gombok / fülek -->
    <circle cx="134" cy="172" r="10" fill="#f43f5e"/>
    <circle cx="164" cy="172" r="10" fill="#f59e0b"/>
    <circle cx="194" cy="172" r="10" fill="#10b981"/>
    <!-- Vertikális oldalsáv jelzés a kártyán belül -->
    <rect x="124" y="226" width="36" height="150" rx="12" fill="#ffffff" opacity="0.2"/>
    <circle cx="142" cy="254" r="8" fill="#38bdf8"/>
    <circle cx="142" cy="286" r="8" fill="#34d399"/>
    <circle cx="142" cy="318" r="8" fill="#f43f5e"/>
    <!-- Tartalom kártya -->
    <rect x="174" y="226" width="168" height="150" rx="16" fill="#ffffff" opacity="0.15"/>
    <line x1="194" y1="260" x2="310" y2="260" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.6"/>
    <line x1="194" y1="284" x2="280" y2="284" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.4"/>
    <line x1="194" y1="308" x2="250" y2="308" stroke="#ffffff" stroke-width="6" stroke-linecap="round" opacity="0.3"/>
  </g>
</svg>'''
}

# 2. Isolated Hexa-Vault (Partíció Hexagon)
DESIGNS["design-2"] = {
    "name": "2. Isolated Hexa-Vault (Biztonságos Partíció Hexagon)",
    "subtitle": "Három izolált munkamenet-konténer védett páncélban",
    "description": "Erőteljes, szimmetrikus hexagon struktúra 3 önálló partíció-szegmenssel (Munkahelyi, Magán, Alapértelmezett). A szigorú sütielkülönítést és adatvédelmet hangsúlyozza.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080c14"/>
      <stop offset="100%" stop-color="#111827"/>
    </linearGradient>
    <linearGradient id="hex-blue" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <linearGradient id="hex-green" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34d399"/>
      <stop offset="100%" stop-color="#047857"/>
    </linearGradient>
    <linearGradient id="hex-purple" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#a78bfa"/>
      <stop offset="100%" stop-color="#6d28d9"/>
    </linearGradient>
    <filter id="glow-2" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="12" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-2)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#1f2937" stroke-width="4"/>

  <!-- Külső védelmi gyűrű pontozva -->
  <circle cx="256" cy="256" r="185" fill="none" stroke="#334155" stroke-width="2" stroke-dasharray="8 8" opacity="0.6"/>

  <!-- Felső bal szegmens (Munkahelyi partíció - Kék) -->
  <path d="M 256 90 L 120 168 L 120 300 L 244 256 L 244 112 Z" fill="url(#hex-blue)" opacity="0.95"/>
  <circle cx="180" cy="210" r="12" fill="#ffffff" opacity="0.8"/>

  <!-- Felső jobb szegmens (Magán partíció - Zöld) -->
  <path d="M 256 90 L 392 168 L 392 300 L 268 256 L 268 112 Z" fill="url(#hex-green)" opacity="0.95"/>
  <circle cx="332" cy="210" r="12" fill="#ffffff" opacity="0.8"/>

  <!-- Alsó szegmens (Rendszer / Alapértelmezett partíció - Lila) -->
  <path d="M 132 322 L 256 394 L 380 322 L 268 274 L 244 274 Z" fill="url(#hex-purple)" opacity="0.95"/>
  <circle cx="256" cy="336" r="12" fill="#ffffff" opacity="0.8"/>

  <!-- Központi szigetelő pajzs / lakat mag -->
  <circle cx="256" cy="256" r="44" fill="#0b0f19" stroke="#60a5fa" stroke-width="5" filter="url(#glow-2)"/>
  <!-- Kulcslyuk / biztonsági ikon a magban -->
  <circle cx="256" cy="248" r="10" fill="#38bdf8"/>
  <polygon points="252,248 260,248 264,268 248,268" fill="#38bdf8"/>
</svg>'''
}

# 3. Vertical Dock Monogram 'T' (Vertikális Dokkoló T-Monogram)
DESIGNS["design-3"] = {
    "name": "3. Vertical Dock 'T' (Vertikális Dokkoló Monogram)",
    "subtitle": "A TabbedClient névadó T-betűje füllistával egybeépítve",
    "description": "Geometrikus, modern 'T' forma. A vízszintes szár a felső ablakfejlécet, a függőleges vastag szár a vertikális oldalsávot formázza 3 fénylő aktív fül-kapszulával.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d16"/>
      <stop offset="100%" stop-color="#161f30"/>
    </linearGradient>
    <linearGradient id="t-bar" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#3b82f6"/>
      <stop offset="100%" stop-color="#6366f1"/>
    </linearGradient>
    <linearGradient id="t-stem" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#0f172a"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-3)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#2a374a" stroke-width="4"/>

  <!-- T felső vízszintes sáv (Ablak címsor) -->
  <rect x="86" y="96" width="340" height="74" rx="24" fill="url(#t-bar)"/>
  <!-- Címsor ablak-pontok -->
  <circle cx="126" cy="133" r="9" fill="#ffffff" opacity="0.75"/>
  <circle cx="154" cy="133" r="9" fill="#ffffff" opacity="0.4"/>
  <circle cx="182" cy="133" r="9" fill="#ffffff" opacity="0.4"/>

  <!-- T függőleges szár (Oldalsáv füllista) -->
  <rect x="196" y="160" width="120" height="256" rx="26" fill="url(#t-stem)" stroke="#334155" stroke-width="3"/>

  <!-- Fülek a szárban (3 vertikális pill) -->
  <!-- 1. Fül (Aktív, kék) -->
  <rect x="214" y="196" width="84" height="48" rx="14" fill="#2563eb"/>
  <circle cx="236" cy="220" r="8" fill="#ffffff"/>
  <line x1="254" y1="220" x2="284" y2="220" stroke="#ffffff" stroke-width="4" stroke-linecap="round"/>

  <!-- 2. Fül (Zöld) -->
  <rect x="214" y="260" width="84" height="48" rx="14" fill="#132337"/>
  <circle cx="236" cy="284" r="8" fill="#10b981"/>
  <line x1="254" y1="284" x2="278" y2="284" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>

  <!-- 3. Fül (Lila) -->
  <rect x="214" y="324" width="84" height="48" rx="14" fill="#132337"/>
  <circle cx="236" cy="348" r="8" fill="#a855f7"/>
  <line x1="254" y1="348" x2="278" y2="348" stroke="#94a3b8" stroke-width="4" stroke-linecap="round"/>

  <!-- Jobb oldali dinamikus böngészőtér keret -->
  <path d="M 336 210 L 400 210 C 414 210, 424 220, 424 234 L 424 370 C 424 384, 414 394, 400 394 L 336 394" fill="none" stroke="#38bdf8" stroke-width="4" stroke-linecap="round" opacity="0.7"/>
</svg>'''
}

# 4. Prism Workspace (Optikai Prizma és Munkamenet-fénysugarak)
DESIGNS["design-4"] = {
    "name": "4. Prism Workspace (Optikai Prizma)",
    "subtitle": "Egyetlen ablak fókuszált szétbontása párhuzamos adatfolyamokká",
    "description": "Üveghatású prizma, melybe egyetlen tiszta bejövő fénysugár érkezik, s a belsejéből 3 precíz, színes spektrális fül-sugár távozik. A hatékony multitask és rendszerezés jelképe.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-4" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0c13"/>
      <stop offset="100%" stop-color="#141824"/>
    </linearGradient>
    <linearGradient id="prism-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/>
      <stop offset="50%" stop-color="#818cf8" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#1e293b" stop-opacity="0.4"/>
    </linearGradient>
    <filter id="beam-glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-4)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#263143" stroke-width="4"/>

  <!-- Bejövő fénysugár balról -->
  <line x1="60" y1="256" x2="220" y2="256" stroke="#ffffff" stroke-width="8" stroke-linecap="round" opacity="0.9" filter="url(#beam-glow)"/>

  <!-- 3 kilépő színes spektrális fül-sugár jobbra -->
  <!-- Kék sugár (Felső) -->
  <line x1="260" y1="240" x2="430" y2="170" stroke="#38bdf8" stroke-width="8" stroke-linecap="round" filter="url(#beam-glow)"/>
  <circle cx="430" cy="170" r="12" fill="#38bdf8"/>

  <!-- Zöld sugár (Középső) -->
  <line x1="260" y1="256" x2="445" y2="256" stroke="#10b981" stroke-width="8" stroke-linecap="round" filter="url(#beam-glow)"/>
  <circle cx="445" cy="256" r="12" fill="#10b981"/>

  <!-- Korall / Magenta sugár (Alsó) -->
  <line x1="260" y1="272" x2="430" y2="342" stroke="#f43f5e" stroke-width="8" stroke-linecap="round" filter="url(#beam-glow)"/>
  <circle cx="430" cy="342" r="12" fill="#f43f5e"/>

  <!-- Prizma háromszög -->
  <polygon points="240,110 330,370 150,370" fill="url(#prism-grad)" stroke="#60a5fa" stroke-width="5" stroke-linejoin="round"/>
  <!-- Prizma belső fénytörés vonal -->
  <line x1="220" y1="256" x2="260" y2="256" stroke="#ffffff" stroke-width="7" opacity="0.9"/>
</svg>'''
}

# 5. Bento Multi-Grid (Rendezett Bento Rendszer)
DESIGNS["design-5"] = {
    "name": "5. Bento Multi-Grid (Bento Munkaállomás)",
    "subtitle": "Korszerű, moduláris oldalsáv- és ablakstruktúra",
    "description": "A modern operációs rendszerek Bento-kártyás formanyelve: dedikált magas vertikális oldalsáv balra, valamint rendezett aktív szolgáltatás- és értesítési panelek jobbra.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-5" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0f1117"/>
      <stop offset="100%" stop-color="#181c26"/>
    </linearGradient>
    <linearGradient id="bento-active" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
    <linearGradient id="bento-card" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#1e2433"/>
      <stop offset="100%" stop-color="#151922"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-5)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#2d3748" stroke-width="4"/>

  <!-- Bal oldalsáv blokk (Bento 1: Sidebar) -->
  <rect x="90" y="90" width="100" height="332" rx="26" fill="url(#bento-card)" stroke="#3b82f6" stroke-width="3"/>
  <circle cx="140" cy="136" r="16" fill="#38bdf8"/>
  <circle cx="140" cy="192" r="14" fill="#34d399" opacity="0.8"/>
  <circle cx="140" cy="244" r="14" fill="#f59e0b" opacity="0.8"/>
  <circle cx="140" cy="296" r="14" fill="#a78bfa" opacity="0.8"/>
  <rect x="116" y="356" width="48" height="36" rx="10" fill="#334155" opacity="0.6"/>

  <!-- Jobb felső nagy fül-ablak blokk (Bento 2: Fő munkaterület) -->
  <rect x="210" y="90" width="212" height="206" rx="26" fill="url(#bento-active)" stroke="#60a5fa" stroke-width="3"/>
  <circle cx="244" cy="126" r="8" fill="#ffffff" opacity="0.9"/>
  <circle cx="266" cy="126" r="8" fill="#ffffff" opacity="0.5"/>
  <circle cx="288" cy="126" r="8" fill="#ffffff" opacity="0.5"/>
  <rect x="236" y="156" width="160" height="18" rx="8" fill="#ffffff" opacity="0.35"/>
  <rect x="236" y="186" width="120" height="14" rx="6" fill="#ffffff" opacity="0.25"/>
  <rect x="236" y="210" width="140" height="14" rx="6" fill="#ffffff" opacity="0.25"/>

  <!-- Jobb alsó blokk (Bento 3: Adatvédelem és badge panel) -->
  <rect x="210" y="316" width="212" height="106" rx="24" fill="url(#bento-card)" stroke="#334155" stroke-width="2"/>
  <circle cx="250" cy="369" r="18" fill="#10b981"/>
  <path d="M 243 369 L 248 374 L 258 364" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="282" y="354" width="94" height="14" rx="6" fill="#94a3b8" opacity="0.7"/>
  <rect x="282" y="376" width="60" height="12" rx="5" fill="#64748b" opacity="0.5"/>
</svg>'''
}

# 6. Orbit Gateway (Keringő Partíciók és Portál)
DESIGNS["design-6"] = {
    "name": "6. Orbit Gateway (Keringő Partíció Portál)",
    "subtitle": "Központi webmotor független keringési pályán lévő fiókokkal",
    "description": "Kozmikus hatású, körkörös szimbólum: egy nagy központi WebKit motor-mag körül három külön pályán keringő fül-égitest, melyek soha nem keverednek egymással.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-6" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#080a14"/>
      <stop offset="100%" stop-color="#12182c"/>
    </linearGradient>
    <linearGradient id="core-glow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <filter id="glow-6" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="14" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-6)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#25324d" stroke-width="4"/>

  <!-- Pálya 1 (Külső elnyújtott ellipszis) -->
  <ellipse cx="256" cy="256" rx="175" ry="90" fill="none" stroke="#3b82f6" stroke-width="3" stroke-dasharray="6 8" opacity="0.5" transform="rotate(-30 256 256)"/>

  <!-- Pálya 2 (Keresztező ellipszis) -->
  <ellipse cx="256" cy="256" rx="175" ry="90" fill="none" stroke="#10b981" stroke-width="3" stroke-dasharray="6 8" opacity="0.5" transform="rotate(30 256 256)"/>

  <!-- Pálya 3 (Függőleges körgyűrű) -->
  <circle cx="256" cy="256" r="140" fill="none" stroke="#a855f7" stroke-width="2" opacity="0.4"/>

  <!-- Központi fénylő mag (Webmag / Kliens) -->
  <circle cx="256" cy="256" r="54" fill="url(#core-glow)" filter="url(#glow-6)"/>
  <circle cx="256" cy="256" r="50" fill="none" stroke="#ffffff" stroke-width="3" opacity="0.8"/>
  <!-- Fehér belső fül-ikon a magban -->
  <rect x="236" y="238" width="40" height="36" rx="8" fill="#ffffff" opacity="0.9"/>
  <rect x="242" y="244" width="10" height="24" rx="3" fill="#2563eb"/>

  <!-- Keringő csomópontok (Fiókok) -->
  <!-- Kék csomópont -->
  <circle cx="115" cy="180" r="20" fill="#38bdf8" filter="url(#glow-6)"/>
  <circle cx="115" cy="180" r="10" fill="#ffffff"/>

  <!-- Zöld csomópont -->
  <circle cx="390" cy="190" r="18" fill="#34d399" filter="url(#glow-6)"/>
  <circle cx="390" cy="190" r="9" fill="#ffffff"/>

  <!-- Narancs csomópont -->
  <circle cx="256" cy="396" r="18" fill="#f59e0b" filter="url(#glow-6)"/>
  <circle cx="256" cy="396" r="9" fill="#ffffff"/>
</svg>'''
}

# 7. Split-View Minimalist (Osztott Ablak Minimalizmus)
DESIGNS["design-7"] = {
    "name": "7. Split-View Minimalist (Svájci Minimalista)",
    "subtitle": "Kifejezetten letisztult, sötét tónusú prémium geometriai ikon",
    "description": "Minimalista, high-contrast svájci dizájn. Precízen megrajzolt böngészőablak markáns bal oldali fülsávval és fénylő aktív fül-jelzővel. Kifejezetten elegáns dock-ikon.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-7" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0a0f"/>
      <stop offset="100%" stop-color="#14141e"/>
    </linearGradient>
    <linearGradient id="sidebar-grad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1d4ed8"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-7)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#222230" stroke-width="4"/>

  <!-- Külső ablak keret -->
  <rect x="90" y="90" width="332" height="332" rx="36" fill="#12131a" stroke="#333846" stroke-width="4"/>

  <!-- Bal oldali vertikális fülsáv -->
  <path d="M 126 90 L 190 90 L 190 422 L 126 422 C 106 422, 90 406, 90 386 L 90 126 C 90 106, 106 90, 126 90 Z" fill="url(#sidebar-grad)"/>

  <!-- Oldalsáv ikonjai (Vertikális füllista) -->
  <rect x="110" y="130" width="60" height="46" rx="12" fill="#ffffff" opacity="0.95"/>
  <circle cx="140" cy="153" r="10" fill="#2563eb"/>

  <rect x="110" y="196" width="60" height="46" rx="12" fill="#ffffff" opacity="0.2"/>
  <circle cx="140" cy="219" r="8" fill="#ffffff" opacity="0.7"/>

  <rect x="110" y="260" width="60" height="46" rx="12" fill="#ffffff" opacity="0.2"/>
  <circle cx="140" cy="283" r="8" fill="#ffffff" opacity="0.7"/>

  <circle cx="140" cy="370" r="14" fill="#ffffff" opacity="0.15"/>
  <line x1="140" y1="362" x2="140" y2="378" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>
  <line x1="132" y1="370" x2="148" y2="370" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>

  <!-- Jobb oldali tartalomablak -->
  <circle cx="230" cy="130" r="8" fill="#f43f5e" opacity="0.7"/>
  <circle cx="254" cy="130" r="8" fill="#f59e0b" opacity="0.7"/>
  <circle cx="278" cy="130" r="8" fill="#10b981" opacity="0.7"/>

  <rect x="220" y="166" width="170" height="110" rx="18" fill="#1a1c26" stroke="#2b2e3d" stroke-width="2"/>
  <line x1="246" y1="205" x2="340" y2="205" stroke="#38bdf8" stroke-width="6" stroke-linecap="round"/>
  <line x1="246" y1="235" x2="310" y2="235" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>

  <rect x="220" y="296" width="170" height="96" rx="18" fill="#1a1c26" stroke="#2b2e3d" stroke-width="2"/>
  <line x1="246" y1="334" x2="320" y2="334" stroke="#10b981" stroke-width="5" stroke-linecap="round"/>
  <line x1="246" y1="358" x2="280" y2="358" stroke="#64748b" stroke-width="5" stroke-linecap="round"/>
</svg>'''
}

# 8. Cyber-Stack Cube (Izometrikus Multi-Layer Kocka)
DESIGNS["design-8"] = {
    "name": "8. Cyber-Stack Cube (Izometrikus Rétegtorony)",
    "subtitle": "Három lebegő izometrikus réteg hardveres stabilitással",
    "description": "Futurisztikus 3D hatás: három önállóan lebegő réteg (Adatpartíció, Hálózati sandbox, Felső aktív felület). A magas technológiai színvonal és a WebKit process-izoláció jelképe.",
    "svg": '''<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg-8" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0e17"/>
      <stop offset="100%" stop-color="#141c2c"/>
    </linearGradient>
    <linearGradient id="layer-top" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="100%" stop-color="#2563eb"/>
    </linearGradient>
    <linearGradient id="layer-mid" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#059669"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>
    <linearGradient id="layer-bot" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#4338ca"/>
    </linearGradient>
    <filter id="shadow-8" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="16" stdDeviation="14" flood-color="#000000" flood-opacity="0.6"/>
    </filter>
  </defs>
  <rect width="512" height="512" rx="112" fill="url(#bg-8)"/>
  <rect width="508" height="508" x="2" y="2" rx="110" fill="none" stroke="#233047" stroke-width="4"/>

  <!-- Függőleges fénynyalábok / összekötők a rétegek között -->
  <line x1="256" y1="130" x2="256" y2="410" stroke="#38bdf8" stroke-width="4" stroke-dasharray="8 8" opacity="0.6"/>

  <!-- Alsó réteg (Partíció & Adattárolás) -->
  <g filter="url(#shadow-8)">
    <!-- Izometrikus rombusz lapka -->
    <path d="M 256 310 L 390 375 L 256 440 L 122 375 Z" fill="url(#layer-bot)"/>
    <path d="M 256 310 L 390 375 L 256 440 L 122 375 Z" fill="none" stroke="#a5b4fc" stroke-width="3" opacity="0.7"/>
    <circle cx="256" cy="375" r="10" fill="#ffffff" opacity="0.8"/>
  </g>

  <!-- Középső réteg (Sandbox & Hálózat) -->
  <g filter="url(#shadow-8)">
    <path d="M 256 210 L 390 275 L 256 340 L 122 275 Z" fill="url(#layer-mid)"/>
    <path d="M 256 210 L 390 275 L 256 340 L 122 275 Z" fill="none" stroke="#6ee7b7" stroke-width="3" opacity="0.8"/>
    <circle cx="256" cy="275" r="10" fill="#ffffff" opacity="0.8"/>
  </g>

  <!-- Felső réteg (Aktív Fül & WebKit UI) -->
  <g filter="url(#shadow-8)">
    <path d="M 256 110 L 390 175 L 256 240 L 122 175 Z" fill="url(#layer-top)"/>
    <path d="M 256 110 L 390 175 L 256 240 L 122 175 Z" fill="none" stroke="#ffffff" stroke-width="4" opacity="0.9"/>
    <!-- Kis fül-elem a felső lapon -->
    <circle cx="220" cy="175" r="9" fill="#ffffff"/>
    <circle cx="256" cy="175" r="9" fill="#ffffff" opacity="0.8"/>
    <circle cx="292" cy="175" r="9" fill="#ffffff" opacity="0.8"/>
  </g>
</svg>'''
}

def main():
    print(f"Generating {len(DESIGNS)} SVG icon files...")
    for key, data in DESIGNS.items():
        svg_path = os.path.join(ICONS_DIR, f"{key}.svg")
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(data["svg"])
        print(f"✓ Saved {svg_path}")

        # PNG renderelés (512x512 és 128x128 thumbnail)
        png_512 = os.path.join(ICONS_DIR, f"{key}-512.png")
        png_128 = os.path.join(ICONS_DIR, f"{key}-128.png")

        handle = Rsvg.Handle.new_from_data(data["svg"].encode("utf-8"))

        # 512x512
        surf_512 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 512, 512)
        ctx_512 = cairo.Context(surf_512)
        handle.render_cairo(ctx_512)
        surf_512.write_to_png(png_512)

        # 128x128
        surf_128 = cairo.ImageSurface(cairo.FORMAT_ARGB32, 128, 128)
        ctx_128 = cairo.Context(surf_128)
        ctx_128.scale(128.0 / 512.0, 128.0 / 512.0)
        handle.render_cairo(ctx_128)
        surf_128.write_to_png(png_128)

    print("All 8 SVG and PNG icons successfully generated!")

if __name__ == "__main__":
    main()
