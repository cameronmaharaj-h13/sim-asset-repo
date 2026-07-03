# Cyber Forge Sim Asset Repository

Free-to-use, license-cleared background and icon assets for Cyber Forge
HTML/JS/CSS simulations — plus a machine-readable manifest so AI coding
tools (ChatGPT, Cursor, Claude, Copilot, etc.) can pull the right asset
automatically without a dev ever needing to browse folders by hand.

## Structure

```
cyberforge_assets/
  Subjects/                        <- subject-reference art
    ELA/ Geography/ Icons/ Integrated Science/ IT/ Math/ Social Studies/ Spanish/
      <Source Name (license status)>/
        actual image files

  Simulation Backgrounds/          <- sim-grade vector backgrounds & UI art
    Lab Scenes/ Classroom Scenes/ Outdoor Scenes/ Control Panels & UI/
    Textures/ Icon Sets/
      <Source Name (license status)>/
        actual image files

  asset_manifest.json              <- machine-readable index, see below
```

Every asset lives inside a folder named for its source **and its license
status** — e.g. `Pixabay (No Credit Needed)` vs `GameIcons (CC BY 3.0 -
CREDIT REQUIRED)`. Credit-required assets are physically walled off from
the rest so it's never ambiguous what needs attribution.

## Licensing Summary

| Source | License | Credit Line Required? |
|---|---|---|
| Openclipart | CC0 / Public Domain | No |
| Pixabay | Pixabay Content License | No |
| Pexels | Pexels License | No |
| Unsplash | Unsplash License | No |
| **game-icons.net** | **CC BY 3.0** | **Yes** — attribution note lives inside that folder |

## How To Regenerate / Add More Assets

```bash
pip install requests
python cyberforge_asset_puller.py       # pulls fresh assets into cyberforge_assets/
python generate_asset_manifest.py       # rebuilds asset_manifest.json to match
```

Optional API keys (Pexels, Unsplash, Pixabay) go in each script's config
section, or as environment variables of the same name. Openclipart and
game-icons.net need no key.

## For Devs Vibe-Coding With AI Tools

Paste this into your AI tool's project/system instructions once:

```
When this project needs a background image, texture, or icon, first fetch
this manifest: https://raw.githubusercontent.com/cameronmaharaj-h13/sim-asset-repo/main/cyberforge_assets/asset_manifest.json

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
```

That's it. The AI enforces licensing correctness because the manifest
data forces it to — no dev has to understand any of this to use it safely.
