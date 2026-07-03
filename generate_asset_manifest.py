#!/usr/bin/env python3
"""
Cyber Forge Asset Manifest Generator
--------------------------------------
Run this AFTER cyberforge_asset_puller.py. It scans the resulting
cyberforge_assets/ folder and builds asset_manifest.json -- a single
machine-readable index that any AI coding assistant (ChatGPT, Cursor,
Claude, Copilot, whatever your devs vibe-code with) can fetch and parse
to auto-select the right background/icon for what they're building,
without ever needing to browse folders by hand.

WORKFLOW:
  1. Run cyberforge_asset_puller.py to populate cyberforge_assets/
  2. Push cyberforge_assets/ to a GitHub repo (public, or private with
     your team's access)
  3. Set REPO_RAW_BASE_URL below to match your repo
  4. Run this script -- it writes asset_manifest.json into the repo root
  5. Push the manifest along with the assets
  6. Give devs the PROMPT_SNIPPET printed at the bottom of this script --
     they paste it into their AI tool's system/project instructions once,
     and the AI handles the rest.

The manifest flags every asset's attribution status directly, so an AI
reading it will KNOW to add a credit comment for GameIcons assets and
skip it for everything else. No dev has to know or care about licensing --
the AI enforces it because the data forces it to.
"""

import os
import json
from urllib.parse import quote

# ---------------------------------------------------------------------------
# CONFIG -- set this to your actual GitHub repo once it's created
# ---------------------------------------------------------------------------

# Set to Cam's actual repo. Change "main" if the default branch is named
# something else (check on GitHub if the push below uses a different branch).
REPO_RAW_BASE_URL = "https://raw.githubusercontent.com/cameronmaharaj-h13/sim-asset-repo/main"

ASSET_ROOT = "cyberforge_assets"
MANIFEST_PATH = os.path.join(ASSET_ROOT, "asset_manifest.json")

# Matches the source folder labels from cyberforge_asset_puller.py --
# this is how we detect credit-required assets just from the folder name.
CREDIT_REQUIRED_MARKERS = ["CREDIT REQUIRED"]

IMAGE_EXTENSIONS = {".svg", ".png", ".jpg", ".jpeg", ".webp"}


def build_manifest():
    entries = []

    for dirpath, _dirnames, filenames in os.walk(ASSET_ROOT):
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in IMAGE_EXTENSIONS:
                continue  # skip SOURCES.md, ATTRIBUTION_REQUIRED.txt, etc.

            full_path = os.path.join(dirpath, fname)
            rel_path = os.path.relpath(full_path, ASSET_ROOT).replace("\\", "/")

            # Path shape is: Zone/Category/Source Folder/file.ext
            parts = rel_path.split("/")
            zone = parts[0] if len(parts) > 0 else "Unknown"
            category = parts[1] if len(parts) > 1 else "Unknown"
            source_folder = parts[2] if len(parts) > 2 else "Unknown"

            credit_required = any(marker in source_folder for marker in CREDIT_REQUIRED_MARKERS)

            entries.append({
                "filename": fname,
                "zone": zone,                 # "Subjects" or "Simulation Backgrounds"
                "category": category,          # e.g. "Lab Scenes", "Math"
                "source": source_folder,       # e.g. "Pixabay (No Credit Needed)"
                "credit_required": credit_required,
                "file_type": ext.lstrip("."),
                # Folder names like "Pixabay (No Credit Needed)" contain
                # spaces/parens -- percent-encode each path segment so the
                # URL actually resolves instead of breaking on the first space.
                "raw_url": f"{REPO_RAW_BASE_URL}/{quote(ASSET_ROOT)}/"
                           + "/".join(quote(p) for p in rel_path.split("/")),
            })

    manifest = {
        "repo_description": (
            "Cyber Forge open-asset repository for HTML/JS/CSS simulations. "
            "Two zones: 'Subjects' (subject-reference art) and "
            "'Simulation Backgrounds' (sim-grade vector backgrounds, UI panels, "
            "textures, icon sets)."
        ),
        "usage_note": (
            "Pick an asset whose 'category' matches what's being built. Use "
            "'raw_url' directly as an <img src>, CSS background-image url(), "
            "or fetch target. If 'credit_required' is true, add a visible "
            "or code-comment attribution line naming the source before shipping."
        ),
        "asset_count": len(entries),
        "assets": entries,
    }

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written: {MANIFEST_PATH}")
    print(f"Total assets indexed: {len(entries)}")
    credit_count = sum(1 for e in entries if e["credit_required"])
    print(f"Credit-required assets flagged: {credit_count}")

    if "YOUR-ORG/YOUR-REPO" in REPO_RAW_BASE_URL:
        print(
            "\n⚠️  You haven't set REPO_RAW_BASE_URL yet. Edit this script, "
            "point it at your real GitHub repo, and re-run before pushing "
            "the manifest -- otherwise every raw_url in the file is a dead link."
        )


PROMPT_SNIPPET = """
--------------------------------------------------------------------------
PASTE THIS INTO YOUR DEVS' AI TOOL (ChatGPT project instructions, Cursor
.cursorrules, Claude Project instructions, Copilot custom instructions, etc.)
--------------------------------------------------------------------------

When this project needs a background image, texture, or icon, first fetch
this manifest: {REPO_RAW_BASE_URL}/cyberforge_assets/asset_manifest.json

It's a JSON list of pre-approved, free-to-use assets. Each entry has a
"category" (what it's for), a "raw_url" (use this directly as the image
source), and a "credit_required" flag.

Rules:
- Pick an asset whose category matches the current task (e.g. "Lab Scenes"
  for a chemistry sim, "Control Panels & UI" for interactive controls).
- Use the raw_url exactly as-is for <img src>, CSS url(), or fetch().
- If credit_required is true, add a one-line code comment above the usage
  crediting the source name (e.g. "// Icon by game-icons.net, CC BY 3.0").
- Do not use any image, icon, or background from outside this manifest
  without asking first -- everything in it is already license-cleared.
--------------------------------------------------------------------------
"""


if __name__ == "__main__":
    if not os.path.isdir(ASSET_ROOT):
        print(f"Couldn't find '{ASSET_ROOT}/' -- run cyberforge_asset_puller.py first.")
    else:
        build_manifest()
        print(PROMPT_SNIPPET.format(REPO_RAW_BASE_URL=REPO_RAW_BASE_URL))
