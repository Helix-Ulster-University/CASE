# save as tools/make_manifest.py  then: python tools/make_manifest.py
import os, json, urllib.parse

ROOTS = ["Crime","Non-Crime","Crime OOD","Non-Crime OOD"]
LANGS = ["en","zh","es","fr","ja"]
AUDIO_DIR = "audio"

def is_audio(name):
    return name.lower().endswith((".mp3",".wav",".m4a",".ogg"))

out = []
for category in ROOTS:
    for lang in LANGS:
        dir_path = os.path.join(AUDIO_DIR, category, lang)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if not is_audio(fname): 
                continue
            rel = "audio/{}/{}/{}".format(
                urllib.parse.quote(category), lang, urllib.parse.quote(fname))
            cls = "Non-Crime" if "Non-Crime" in category else "Crime"
            out.append({
                "category": category,
                "lang": lang,
                "cls": cls,
                "url": rel,
                "title": f"{lang.upper()} — {category} — {fname}"
            })

with open(os.path.join(AUDIO_DIR,"manifest.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)

print(f"Wrote {len(out)} entries to audio/manifest.json")
