#!/usr/bin/env python3
"""
Cyber Forge Asset Puller v3
--------------------------------
Same two zones as before:

  1. cyberforge_assets/Subjects/<Subject>/
  2. cyberforge_assets/Simulation Backgrounds/<Category>/

NEW IN V3: every category folder now splits into SOURCE-LABELED SUBFOLDERS,
so credit-required assets can never end up mixed in with no-attribution ones.
Example:

  Subjects/ELA/
    Openclipart (CC0 - No Credit Needed)/
    Pexels (No Credit Needed)/
    Unsplash (No Credit Needed)/

  Simulation Backgrounds/Icon Sets/
    GameIcons (CC BY 3.0 - CREDIT REQUIRED)/     <-- the ONLY folder in the
                                                       whole repo that needs
                                                       an attribution line

License summary (confirmed):
  - Openclipart .... CC0 / Public Domain ......... No credit needed
  - Pixabay ........ Pixabay Content License ..... No credit needed
  - Pexels ......... Pexels License .............. No credit needed
  - Unsplash ....... Unsplash License ............ No credit needed
  - game-icons.net . CC BY 3.0 .................... CREDIT REQUIRED

SETUP: unchanged from v2.
  1. pip install requests
  2. (optional) Free Pixabay key:  https://pixabay.com/api/docs/
  3. (optional) Free Pexels key:   https://www.pexels.com/api/
  4. (optional) Free Unsplash key: https://unsplash.com/developers
  5. Paste keys below or set as environment variables of the same name.
  6. Run:  python cyberforge_asset_puller.py
  7. Output lands in ./cyberforge_assets/ -- drag straight into Drive.

Manual, curated sources still worth a one-time browse (no API):
  - Kenney.nl        -- https://kenney.nl/assets       -- CC0, no credit needed
  - OpenGameArt.org  -- https://opengameart.org         -- mixed CC0/CC-BY, CHECK
                          each individual asset page before use
"""

import os
import time
import shutil
import subprocess
import requests

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

IMAGES_PER_QUERY = 10
OUTPUT_ROOT = "cyberforge_assets"
SUBJECTS_DIR = os.path.join(OUTPUT_ROOT, "Subjects")
SIM_DIR = os.path.join(OUTPUT_ROOT, "Simulation Backgrounds")

# Every source gets a labeled subfolder name. The label IS the license status
# -- no separate doc to lose track of, no ambiguity when Cam is knee-deep in
# a build at midnight grabbing an asset.
SOURCE_FOLDER_NAMES = {
    "openclipart": "Openclipart (CC0 - No Credit Needed)",
    "pexels": "Pexels (No Credit Needed)",
    "unsplash": "Unsplash (No Credit Needed)",
    "pixabay": "Pixabay (No Credit Needed)",
    "game_icons": "GameIcons (CC BY 3.0 - CREDIT REQUIRED)",
}

# --- Zone 1: Subject reference art (matches your Drive folders) -----------
SUBJECT_QUERIES = {
    "ELA": ["books background", "writing notebook", "library shelf", "reading illustration"],
    "Geography": ["world map", "mountains landscape", "globe illustration", "compass terrain"],
    "Icons": ["flat icon set", "line icons", "ui icon pack"],
    "Integrated Science": ["laboratory background", "microscope science", "beaker chemistry", "science classroom"],
    "IT": ["computer circuit board", "coding background", "server technology", "keyboard closeup"],
    "Math": ["math equations background", "geometry shapes", "chalkboard numbers", "graph paper"],
    "Social Studies": ["classroom history", "government building", "historic landmark", "community illustration"],
    "Spanish": ["spain landmark", "latin culture illustration", "flamenco background", "spanish flag"],
}

# --- Zone 2: Sim-grade backgrounds (vector-first, built for HTML/JS/CSS) --
SIM_BACKGROUND_QUERIES = {
    "Lab Scenes": ["laboratory flat illustration", "science lab vector background", "chemistry bench illustration"],
    "Classroom Scenes": ["classroom flat illustration", "school room vector", "empty classroom illustration"],
    "Outdoor Scenes": ["nature flat illustration background", "sky gradient vector", "landscape flat background", "playground vector illustration"],
    "Control Panels & UI": ["control panel flat vector", "dashboard ui illustration", "machine panel vector"],
    "Textures": ["wood texture seamless", "metal texture seamless", "paper texture background", "grid texture background"],
}

GAME_ICONS_REPO = "https://github.com/game-icons/icons.git"
GAME_ICONS_FOLDERS = ["delapouite", "lorc", "skoll"]
GAME_ICONS_LIMIT_PER_FOLDER = 25


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _source_subfolder(category_dir, source_key):
    """Every download goes into category_dir/<Source Label>/ -- guarantees
    credit-required assets are physically walled off from the rest."""
    path = os.path.join(category_dir, SOURCE_FOLDER_NAMES[source_key])
    os.makedirs(path, exist_ok=True)
    return path


def _download(url, path):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return True
    except Exception as e:
        print(f"    failed: {url} ({e})")
        return False


# ---------------------------------------------------------------------------
# SOURCE FETCHERS -- each one drops files into its own labeled subfolder
# ---------------------------------------------------------------------------

def fetch_openclipart(query, limit, category_dir):
    dest = _source_subfolder(category_dir, "openclipart")
    url = "https://openclipart.org/search/json/"
    params = {"query": query, "amount": limit}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [openclipart] skip ({e})")
        return 0

    count = 0
    for item in data.get("payload", [])[:limit]:
        img_url = item.get("svg", {}).get("url") or item.get("png_256", {}).get("url")
        title = item.get("title", "asset").replace(" ", "_").replace("/", "-")
        if not img_url:
            continue
        ext = ".svg" if img_url.endswith(".svg") else ".png"
        fname = f"openclipart_{title}{ext}"
        if _download(img_url, os.path.join(dest, fname)):
            count += 1
    return count


def fetch_pexels(query, limit, category_dir):
    if not PEXELS_API_KEY:
        return 0
    dest = _source_subfolder(category_dir, "pexels")
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": limit}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [pexels] skip ({e})")
        return 0

    count = 0
    for photo in data.get("photos", [])[:limit]:
        img_url = photo["src"]["large"]
        fname = f"pexels_{photo['id']}.jpg"
        if _download(img_url, os.path.join(dest, fname)):
            count += 1
    return count


def fetch_unsplash(query, limit, category_dir):
    if not UNSPLASH_ACCESS_KEY:
        return 0
    dest = _source_subfolder(category_dir, "unsplash")
    url = "https://api.unsplash.com/search/photos"
    headers = {"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"}
    params = {"query": query, "per_page": limit}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [unsplash] skip ({e})")
        return 0

    count = 0
    for photo in data.get("results", [])[:limit]:
        img_url = photo["urls"]["regular"]
        fname = f"unsplash_{photo['id']}.jpg"
        if _download(img_url, os.path.join(dest, fname)):
            count += 1
    return count


def fetch_pixabay(query, limit, category_dir, vectors_only=True):
    if not PIXABAY_API_KEY:
        return 0
    dest = _source_subfolder(category_dir, "pixabay")
    url = "https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "image_type": "vector" if vectors_only else "illustration",
        "per_page": max(limit, 3),
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  [pixabay] skip ({e})")
        return 0

    count = 0
    for hit in data.get("hits", [])[:limit]:
        img_url = hit.get("largeImageURL")
        fname = f"pixabay_{hit['id']}.jpg"
        if img_url and _download(img_url, os.path.join(dest, fname)):
            count += 1
    return count


def fetch_game_icons(category_dir):
    """CC BY 3.0 -- the only source in this script that legally needs a
    credit line. Lands in its own clearly-flagged subfolder for exactly
    that reason."""
    dest = _source_subfolder(category_dir, "game_icons")
    tmp_clone = "_gameicons_tmp"
    if os.path.exists(tmp_clone):
        shutil.rmtree(tmp_clone)

    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", GAME_ICONS_REPO, tmp_clone],
            check=True, capture_output=True, timeout=120,
        )
    except Exception as e:
        print(f"  [game-icons] skip ({e})")
        return 0

    count = 0
    for author in GAME_ICONS_FOLDERS:
        src_dir = os.path.join(tmp_clone, "icons", author)
        if not os.path.isdir(src_dir):
            continue
        svgs = [f for f in os.listdir(src_dir) if f.endswith(".svg")][:GAME_ICONS_LIMIT_PER_FOLDER]
        for svg in svgs:
            shutil.copy(os.path.join(src_dir, svg), os.path.join(dest, f"{author}_{svg}"))
            count += 1

    shutil.rmtree(tmp_clone, ignore_errors=True)

    # Drop a plain-text attribution reminder INSIDE the folder itself --
    # travels with the files no matter how they get moved around later.
    with open(os.path.join(dest, "ATTRIBUTION_REQUIRED.txt"), "w") as f:
        f.write(
            "These icons are from game-icons.net, licensed CC BY 3.0.\n"
            "You MUST credit the original artist when used publicly.\n"
            "Format: 'Icons by [author name] from game-icons.net, "
            "licensed under CC BY 3.0'\n"
            "Author names match the filename prefix (delapouite, lorc, skoll).\n"
            "Full license: https://creativecommons.org/licenses/by/3.0/\n"
        )
    return count


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    os.makedirs(SUBJECTS_DIR, exist_ok=True)
    os.makedirs(SIM_DIR, exist_ok=True)
    license_log = []

    # --- Zone 1: Subjects -------------------------------------------------
    for subject, queries in SUBJECT_QUERIES.items():
        category_dir = os.path.join(SUBJECTS_DIR, subject)
        os.makedirs(category_dir, exist_ok=True)
        print(f"\n=== Subjects / {subject} ===")

        for q in queries:
            print(f" query: '{q}'")
            n1 = fetch_openclipart(q, IMAGES_PER_QUERY, category_dir)
            n2 = fetch_pexels(q, IMAGES_PER_QUERY, category_dir)
            n3 = fetch_unsplash(q, IMAGES_PER_QUERY, category_dir)
            print(f"  -> openclipart:{n1}  pexels:{n2}  unsplash:{n3}")
            license_log.append({
                "zone": "Subjects", "category": subject, "query": q,
                "openclipart": n1, "pexels": n2, "unsplash": n3, "pixabay": 0, "game_icons": 0,
            })
            time.sleep(0.3)

    # --- Zone 2: Simulation Backgrounds ------------------------------------
    for category, queries in SIM_BACKGROUND_QUERIES.items():
        category_dir = os.path.join(SIM_DIR, category)
        os.makedirs(category_dir, exist_ok=True)
        print(f"\n=== Simulation Backgrounds / {category} ===")

        for q in queries:
            print(f" query: '{q}'")
            n1 = fetch_openclipart(q, IMAGES_PER_QUERY, category_dir)
            n4 = fetch_pixabay(q, IMAGES_PER_QUERY, category_dir, vectors_only=True)
            print(f"  -> openclipart:{n1}  pixabay(vector):{n4}")
            license_log.append({
                "zone": "Simulation Backgrounds", "category": category, "query": q,
                "openclipart": n1, "pexels": 0, "unsplash": 0, "pixabay": n4, "game_icons": 0,
            })
            time.sleep(0.3)

    # --- Zone 2 bonus: game-icons.net icon dump ----------------------------
    icons_category_dir = os.path.join(SIM_DIR, "Icon Sets")
    os.makedirs(icons_category_dir, exist_ok=True)
    print(f"\n=== Simulation Backgrounds / Icon Sets (game-icons.net) ===")
    n5 = fetch_game_icons(icons_category_dir)
    print(f"  -> game-icons SVGs pulled: {n5}  [CREDIT REQUIRED -- see subfolder]")
    license_log.append({
        "zone": "Simulation Backgrounds", "category": "Icon Sets", "query": "game-icons.net bulk pull",
        "openclipart": 0, "pexels": 0, "unsplash": 0, "pixabay": 0, "game_icons": n5,
    })

    # --- Manifest ------------------------------------------------------------
    manifest_path = os.path.join(OUTPUT_ROOT, "SOURCES.md")
    with open(manifest_path, "w") as f:
        f.write("# Asset Source Manifest\n\n")
        f.write("Auto-generated by cyberforge_asset_puller.py\n\n")
        f.write("## Credit Requirements -- read this first\n\n")
        f.write("| Source | License | Credit Line Needed? |\n")
        f.write("|---|---|---|\n")
        f.write("| Openclipart | CC0 / Public Domain | No |\n")
        f.write("| Pixabay | Pixabay Content License | No |\n")
        f.write("| Pexels | Pexels License | No |\n")
        f.write("| Unsplash | Unsplash License | No |\n")
        f.write("| **game-icons.net** | **CC BY 3.0** | **YES -- see the "
                 "'GameIcons (CC BY 3.0 - CREDIT REQUIRED)' subfolder in every "
                 "category, it has its own attribution note inside** |\n\n")
        f.write("Every download is sorted into a source-labeled subfolder "
                 "inside its category, so credit-required assets are never "
                 "mixed in with no-attribution ones. Check the folder name "
                 "before you use anything, and you're covered.\n\n")
        f.write("## Pull Log\n\n")
        f.write("| Zone | Category | Query | Openclipart | Pexels | Unsplash | Pixabay | game-icons (CREDIT REQ.) |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        for row in license_log:
            f.write(f"| {row['zone']} | {row['category']} | {row['query']} | {row['openclipart']} | "
                     f"{row['pexels']} | {row['unsplash']} | {row['pixabay']} | {row['game_icons']} |\n")
        f.write("\n## Manual sources worth a one-time browse (not scriptable)\n\n")
        f.write("- Kenney.nl -- https://kenney.nl/assets -- CC0, no credit needed\n")
        f.write("- OpenGameArt.org -- https://opengameart.org -- MIXED licenses, "
                 "check each asset page individually before use\n")

    print(f"\nDone. Files sorted into ./{OUTPUT_ROOT}/")
    print(f"Source manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
