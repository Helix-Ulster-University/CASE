# tools/make_manifest.py
# Usage: python tools/make_manifest.py
import os
import json
import sys
import urllib.parse
from pathlib import Path

# ---- Config ----
AUDIO_DIR = Path("audio")
ROOTS = ["Crime", "Non-Crime", "Crime OOD", "Non-Crime OOD"]
LANGS = ["en", "zh", "es", "fr", "ja"]
EXTS = (".mp3", ".wav", ".m4a", ".ogg")  # add more if needed

OUT_JSON = AUDIO_DIR / "manifest.json"
OUT_JS   = AUDIO_DIR / "manifest.js"

LANG_LABEL = {
    "en": "EN",
    "zh": "ZH",
    "es": "ES",
    "fr": "FR",
    "ja": "JA",
}

def is_audio(name: str) -> bool:
    return name.lower().endswith(EXTS)

def url_for(category: str, lang: str, fname: str) -> str:
    # Encode each path segment safely for URLs
    return "audio/{}/{}/{}".format(
        urllib.parse.quote(category, safe=""),
        urllib.parse.quote(lang, safe=""),
        urllib.parse.quote(fname, safe=""),
    )

def class_from_category(category: str) -> str:
    return "Non-Crime" if "Non-Crime" in category else "Crime"

def build_manifest() -> list[dict]:
    out = []
    for category in ROOTS:
        for lang in LANGS:
            dir_path = AUDIO_DIR / category / lang
            if not dir_path.is_dir():
                continue
            for entry in os.scandir(dir_path):
                if not entry.is_file():
                    continue
                fname = entry.name
                if not is_audio(fname):
                    continue

                rel_url = url_for(category, lang, fname)
                cls = class_from_category(category)
                lang_tag = LANG_LABEL.get(lang, lang.upper())

                out.append({
                    "category": category,
                    "lang": lang,
                    "cls": cls,
                    "url": rel_url,
                    "title": f"{lang_tag} — {category} — {fname}",
                })
    # Stable, human-friendly sort
    cat_order = {c: i for i, c in enumerate(ROOTS)}
    lang_order = {l: i for i, l in enumerate(LANGS)}
    out.sort(key=lambda x: (
        cat_order.get(x["category"], 999),
        lang_order.get(x["lang"], 999),
        x["title"].lower()
    ))
    return out

def write_json(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(entries):,} entries to {path.as_posix()}")

def write_js(entries: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Emit as a global for the no-backend HTML
    js = "window.MANIFEST_RAW = " + json.dumps(entries, indent=2, ensure_ascii=False) + ";\n"
    with path.open("w", encoding="utf-8") as f:
        f.write(js)
    print(f"Wrote {len(entries):,} entries to {path.as_posix()}")

def main():
    if not AUDIO_DIR.exists():
        print(f"Error: {AUDIO_DIR.as_posix()} not found.", file=sys.stderr)
        sys.exit(1)

    entries = build_manifest()
    write_json(entries, OUT_JSON)
    write_js(entries, OUT_JS)

if __name__ == "__main__":
    main()
