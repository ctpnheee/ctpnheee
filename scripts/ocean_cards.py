"""Build a light ocean theme for the profile summary cards by recoloring the radical theme."""
import pathlib

SRC = pathlib.Path("profile-summary-card-output/radical")
DST = pathlib.Path("profile-summary-card-output/ocean")

PALETTE = {
    "#141321": "#eef8ff",  # background: sea foam
    "#fe428e": "#0b5394",  # title: deep ocean
    "#a9fef7": "#1e3a5f",  # text and axes: abyss blue
    "#f8d847": "#0891b2",  # icons: lagoon cyan
    "#ae81ff": "#38bdf8",  # charts: sky wave
}

DST.mkdir(parents=True, exist_ok=True)
for svg in SRC.glob("*.svg"):
    s = svg.read_text(encoding="utf-8")
    for old, new in PALETTE.items():
        s = s.replace(old, new).replace(old.upper(), new)
    # radical cards have no border; add a soft one so the light card stands out
    s = s.replace('stroke-opacity="0"', 'stroke-opacity="1"').replace(
        'stroke="#eef8ff"', 'stroke="#bae6fd"')
    (DST / svg.name).write_text(s, encoding="utf-8")
    print("wrote", DST / svg.name)
