#!/usr/bin/env python3
"""
Génère « sphere_dark-ardour.colors » (Ardour 9) à partir de dark-ardour.colors,
le thème sombre fourni avec Ardour. Seule la palette (<Colors>) change : les 429 alias
d'Ardour pointent vers elle, donc toute l'interface suit.

Usage : python3 build_ardour_theme.py dark-ardour.colors sphere_dark-ardour.colors

Les couleurs fonctionnelles restent intactes : VU-mètres, alertes (enregistrement,
solo, mute), mètres MIDI, lignes du piano roll.
"""
import re
import sys

# Gris d'Ardour -> gris bleu-ardoise (même rampe que le thème Blender)
STOPS = [
    (0, "#06070c"), (22, "#0f1017"), (29, "#13151d"), (40, "#191b24"), (48, "#1c1e29"),
    (61, "#22242f"), (84, "#383c4e"), (112, "#4a4f63"), (153, "#8b92a8"),
    (230, "#dfe5f5"), (238, "#e7ebf7"), (255, "#ffffff"),
]

# Retouches de palette (nom Ardour -> couleur Sphere-Dark)
OVERRIDES = {
    "theme:contrasting selection": "#5a6a9a",  # sélection GTK = accent du système
    "widget:blue":                 "#5a6a9a",  # remplissage des faders de processeurs
    "widget:blue lighter":         "#7d8ab3",
    "widget:blue darker":          "#1c1f2b",  # base des bus audio
    "theme:contrasting clock":     "#a9b4d0",  # texte des horloges : bleu clair de la sphère
    "theme:contrasting alt":       "#ddc084",  # horloge en édition, delta
    "theme:contrasting less":      "#7eb488",
    "theme:contrasting":           "#e8604c",  # tête de lecture : rouge chaud, reste très visible
    "widget:orange":               "#b4694f",  # marqueurs de tempo : accent rouille
    "neutral:foregroundest":       "#eef1fa",  # lignes de grille majeures, pas blanc pur
}

# Familles fonctionnelles laissées telles quelles
KEEP_PREFIXES = ("alert:", "meter color", "midi meter", "pianoroll:")
KEEP_NAMES = {"widget:green", "widget:green darker", "widget:ruddy", "widget:yellow"}


def ramp(v):
    pts = [(a, tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))) for a, c in STOPS]
    for (v0, c0), (v1, c1) in zip(pts, pts[1:]):
        if v <= v1:
            t = (v - v0) / (v1 - v0)
            return "%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(c0, c1))
    return "ffffff"


COLOR_RE = re.compile(r'(<Color name="([^"]+)" value=")(?:0x)?([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})("/>)')


def recolor(m):
    head, name, rgb, alpha, tail = m.groups()
    if name in OVERRIDES:
        new = OVERRIDES[name].lstrip("#")
    elif name.startswith(KEEP_PREFIXES) or name in KEEP_NAMES:
        new = rgb
    else:
        r, g, b = (int(rgb[i:i + 2], 16) for i in (0, 2, 4))
        new = ramp((r + g + b) / 3) if max(r, g, b) - min(r, g, b) <= 16 else rgb
    return head + new.lower() + alpha.lower() + tail


def main():
    src, dst = sys.argv[1], sys.argv[2]
    s = open(src, encoding="utf-8").read()
    s = s.replace('<Ardour theme-name="dark">', '<Ardour theme-name="Sphere Dark">', 1)
    head, sep, rest = s.partition("</Colors>")
    head, n = COLOR_RE.subn(recolor, head)
    open(dst, "w", encoding="utf-8").write(head + sep + rest)
    print("Écrit :", dst, "-", n, "couleurs de palette traitées")


if __name__ == "__main__":
    main()
