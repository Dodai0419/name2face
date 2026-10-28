---
name: name2face
description: Generate deterministic, cute SVG blob avatars from names, usernames, emails or IDs (same input, same face). Use when the user needs default profile pictures, placeholder avatars, user icons for a mock-up, or avatars in a Python backend without Node or an image API.
---

# name2face

Stdlib-only Python 3 (tested on 3.11). Output is byte-identical to `@blobz/avatar-core`, so a Python backend and a React frontend can draw the same face.

## Commands (run from the repo root)
- Print one SVG: `python name2face.py "ada lovelace" > ada.svg`
- Many files: `python name2face.py alice bob carol -o avatars/` (writes `avatars/<name>.svg`)
- A gallery page to preview: `python name2face.py alice bob carol --html faces.html`
- Brand colours and frame: add `--bg "#0b1830" --body "#18a6d3" --frame circle` (`rounded` default, `square`)
- README images: `python demo.py`

## From Python
```python
from name2face import avatar
svg = avatar("user@example.com", palette=("#f2f1f4", "#7c6cf2"), frame="rounded")
```
Pass `overrides={"eyeI": 3, "mouthI": 0}` to pin single features (indexes into `CHOICES`).

## Notes for the agent
- Names are trimmed and lower-cased first, so "Ada " and "ada" get the same face.
- The avatar is not a secret and not unique: about 4.9 billion combinations, so two names can share a face.
- Colours must be `#rrggbb`. A dark body colour switches the face to light ink automatically.
