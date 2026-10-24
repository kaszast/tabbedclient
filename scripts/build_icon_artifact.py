import os
import json

BASE_DIR = "/home/maci/antigravity/tabbetclient"
ICONS_DIR = os.path.join(BASE_DIR, "resources", "icons")
ARTIFACT_DIR = "/home/maci/.gemini/antigravity/brain/1cf1bfdb-9291-4483-be6d-701a84fd25cc"
HTML_PATH = os.path.join(ARTIFACT_DIR, "icon_proposals.html")

DESIGNS_DATA = [
    {
        "id": "design-1",
        "number": 1,
        "name": "Layered Deck",
        "hu_name": "Átlapolt Füllapok",
        "tag": "Klasszikus & Letisztult",
        "color": "from-blue-600 to-indigo-800",
        "desc": "Három egymást átfedő, lebegő böngészőkártya mélységi árnyékkal, állapotjelző pontokkal és vertikális oldalsáv-jelzéssel. A párhuzamos munkamenetek közvetlen, könnyen felismerhető szimbóluma.",
        "metaphor": "Több füles kártyapakli és párhuzamos webes appok"
    },
    {
        "id": "design-2",
        "number": 2,
        "name": "Isolated Hexa-Vault",
        "hu_name": "Biztonságos Partíció Hexagon",
        "tag": "Adatvédelem & Konténerek",
        "color": "from-emerald-600 to-blue-700",
        "desc": "Erőteljes, szimmetrikus hexagon védelmi pajzs 3 izolált szegmenssel (Munkahelyi kék, Magán zöld, Rendszer lila) és központi biztonsági zárral. A multi-account süti- és munkamenet-izolációt testesíti meg.",
        "metaphor": "Kriptográfiailag védett, elszeparált partíciók"
    },
    {
        "id": "design-3",
        "number": 3,
        "name": "Vertical Dock Monogram 'T'",
        "hu_name": "Vertikális Dokkoló T-Monogram",
        "tag": "Márkanév & Navigáció",
        "color": "from-blue-500 to-indigo-600",
        "desc": "A TabbedClient névadó 'T' betűje, melynek felső szára az ablakcímsort, függőleges vastag szára pedig a bal oldali vertikális dokkolósávot formázza 3 fénylő aktív fül-kapszulával.",
        "metaphor": "TabbedClient 'T' betű + vertikális füllista"
    },
    {
        "id": "design-4",
        "number": 4,
        "name": "Prism Workspace",
        "hu_name": "Optikai Prizma és Fénysugarak",
        "tag": "Fókusz & Szétválasztás",
        "color": "from-cyan-500 to-rose-500",
        "desc": "Üveghatású prizma, melybe egyetlen tiszta fehér fénysugár érkezik balról (az alkalmazás), és 3 precíz, színes spektrális fül-sugár távozik jobbra. A fókuszált szétválasztás metaforája.",
        "metaphor": "Optikai prizma, fókuszált munkamenetek"
    },
    {
        "id": "design-5",
        "number": 5,
        "name": "Bento Multi-Grid",
        "hu_name": "Bento Rendszer & Munkaállomás",
        "tag": "Moduláris & Modern",
        "color": "from-blue-600 to-slate-800",
        "desc": "Modern Bento-grid elrendezés: dedikált magas vertikális oldalsáv balra 4 szolgáltatás-ikonnal, jobb felül aktív fülmunkaterület, alul pedig állapot- és adatvédelmi panel.",
        "metaphor": "Rendezett Bento munkaállomás"
    },
    {
        "id": "design-6",
        "number": 6,
        "name": "Orbit Gateway",
        "hu_name": "Keringő Partíció Portál",
        "tag": "Dinamikus & Kozmikus",
        "color": "from-sky-400 to-purple-600",
        "desc": "Központi WebKit motor-mag körül három külön pályán keringő, fénylő fiók-égitest. A független, soha nem ütköző munkamenetek és háttérben futó szolgáltatások kifejező szimbóluma.",
        "metaphor": "Központi motor és önálló pályájú fiókok"
    },
    {
        "id": "design-7",
        "number": 7,
        "name": "Split-View Minimalist",
        "hu_name": "Svájci Minimalista Ablak",
        "tag": "Elegáns & Flat Design",
        "color": "from-blue-700 to-slate-900",
        "desc": "Letisztult, svájci stílusú magas kontrasztú geometria: vékony ablakkeret markáns bal oldali indigókék oldalsávval, aktív fül-jelzővel és minimalista munkatérrel. Diszkrét és prémium.",
        "metaphor": "Letisztult skandináv/svájci dokk-ikon"
    },
    {
        "id": "design-8",
        "number": 8,
        "name": "Cyber-Stack Cube",
        "hu_name": "Izometrikus Rétegtorony",
        "tag": "Hardveres & 3D Stabilitás",
        "color": "from-sky-400 to-emerald-500",
        "desc": "3D izometrikus lapkatorony: három lebegő szint (Adattárolás, Hálózati sandbox, Felhasználói felület) függőleges fénynyalábbal összekötve. A magas technológiai stabilitást tükrözi.",
        "metaphor": "Többrétegű hardveres és szoftveres izoláció"
    }
]

html_cards = []
for d in DESIGNS_DATA:
    svg_file = os.path.join(ICONS_DIR, f"{d['id']}.svg")
    with open(svg_file, "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Eltávolítjuk a width/height attribútumot az inline SVG-ből a rugalmas méretezéshez
    svg_clean = svg_content.replace('width="512"', 'class="w-full h-full object-contain rounded-2xl shadow-md transition-transform duration-300 group-hover:scale-105"')
    svg_clean = svg_clean.replace('height="512"', '')

    card = f"""
    <div class="group relative bg-[var(--card)] hover:bg-[var(--sidebar)] border border-[var(--border)] hover:border-blue-500/50 rounded-2xl p-5 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            #{d['number']} Terv
          </span>
          <span class="text-xs text-[var(--muted-foreground)] font-mono">{d['tag']}</span>
        </div>

        <!-- Nagy Ikon Előnézet -->
        <div class="w-full aspect-square max-w-[180px] mx-auto my-3 p-2 bg-[var(--background)] rounded-3xl border border-[var(--border)] flex items-center justify-center">
          {svg_clean}
        </div>

        <h3 class="text-base font-bold text-[var(--foreground)] mt-2 group-hover:text-blue-400 transition-colors">
          {d['name']}
        </h3>
        <p class="text-xs font-medium text-blue-400/90 mb-2">{d['hu_name']}</p>
        <p class="text-xs text-[var(--muted-foreground)] leading-relaxed">
          {d['desc']}
        </p>
      </div>

      <div class="mt-4 pt-3 border-t border-[var(--border)] flex items-center justify-between text-xs text-[var(--muted-foreground)]">
        <span class="truncate">💡 {d['metaphor']}</span>
      </div>
    </div>
    """
    html_cards.append(card)

full_html = f"""<!DOCTYPE html>
<html lang="hu">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TabbedClient — 8 Ikon Terv Koncepció</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
</head>
<body class="bg-transparent text-[var(--foreground)] antialiased p-4 md:p-6 font-sans">

  <!-- Fejléc Szekció -->
  <div class="bg-[var(--card)] border border-[var(--border)] rounded-2xl p-6 mb-6 shadow-sm">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <div class="flex items-center gap-2 mb-1">
          <span class="w-3 h-3 rounded-full bg-blue-500 animate-pulse"></span>
          <span class="text-xs font-semibold uppercase tracking-wider text-blue-400">Design Rendszer</span>
        </div>
        <h1 class="text-2xl font-extrabold text-[var(--foreground)]">TabbedClient — 8 Hivatalos Ikon Terv</h1>
        <p class="text-sm text-[var(--muted-foreground)] mt-1">
          Válaszd ki az alábbi 8 egyedi tervezésű ikon közül a neked tetszőt. A kiválasztott dizájn beépítésre kerül az asztali indítóba (.desktop), a rendszertálcába, a címsor logóba és a telepítőcsomagokba.
        </p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-xs px-3 py-1.5 rounded-lg bg-[var(--background)] border border-[var(--border)] text-[var(--muted-foreground)] font-mono">
          512×512 Vektor SVG
        </span>
      </div>
    </div>
  </div>

  <!-- 8 Ikon Rács -->
  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
    {"".join(html_cards)}
  </div>

  <!-- Összegző lábléc -->
  <div class="mt-6 bg-[var(--card)] border border-[var(--border)] rounded-xl p-4 text-center text-xs text-[var(--muted-foreground)]">
    Mind a 8 ikon teljes vektoros formátumban elkészült és letárolva a <code class="text-blue-400">resources/icons/</code> mappában. A választás után azonnal legenerálódnak a 16×16, 32×32, 48×48, 128×128, 256×256 és 512×512 képpontos raszteres változatok.
  </div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"Successfully generated HTML artifact at: {HTML_PATH}")
