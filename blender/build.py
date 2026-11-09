#!/usr/bin/env python3
"""
Génère le thème Blender « Sphere Dark » à partir du thème par défaut de Blender 5.2
(exporté en XML), recoloré avec la palette du thème système Sphere-Dark.

Usage : python3 build_blender_theme.py default_5_2.xml sphere_dark.xml

Règles :
  - les gris neutres de Blender suivent une rampe vers les gris bleu-ardoise du système
    (l'ordre des valeurs est conservé, donc la hiérarchie de Blender reste intacte) ;
  - le bleu de sélection de l'interface devient l'accent du système (#5a6a9a) ;
  - les couleurs qui portent un sens (axes X/Y/Z, sélection orange, os, collections,
    nœuds, clés d'animation, icônes) ne sont pas touchées.
"""
import colorsys
import re
import sys
import xml.etree.ElementTree as ET

# Rampe : valeur de gris de Blender (0-255) -> couleur Sphere-Dark
STOPS = [
    (0,   "#06070c"),
    (22,  "#0f1017"),  # séparations entre éditeurs = barres de titre / panel du système
    (29,  "#13151d"),  # champs de saisie
    (40,  "#191b24"),  # fond des fenêtres du système
    (48,  "#1c1e29"),  # fonds d'éditeurs, en-têtes
    (61,  "#22242f"),  # panneaux, viewport
    (84,  "#383c4e"),  # boutons
    (112, "#4a4f63"),
    (153, "#8b92a8"),  # texte atténué
    (230, "#dfe5f5"),  # texte principal
    (238, "#e7ebf7"),
    (255, "#ffffff"),
]

ACCENT = "#5a6a9a"
ACCENT_ATTRS = {
    "inner_sel", "panel_active", "link", "widget_text_cursor", "playhead", "channels",
    "channels_sub", "selected_file", "match", "cursor", "text_strip_cursor",
    "selected_highlight", "active", "info_selected", "info", "line_output",
}
ACCENT_ITEM_WIDGETS = {"wcol_num", "wcol_numslider", "wcol_progress"}
SEMANTIC_PARENTS = {"ThemeBoneColorSet", "ThemeCollectionColor", "ThemeStripColor"}

# Retouches ponctuelles (chemin de balises se terminant par..., attribut) -> valeur
OVERRIDES = {
    # Viewport : halo de studio comme le fond d'écran (centre éclairé, bords sombres)
    (("view_3d",), "background_type"): "RADIAL",
    (("view_3d",), "high_gradient"): "#2a2d3a",
    (("view_3d",), "gradient"): "#12141b",
    (("view_3d",), "grid"): "#50566c80",
    (("view_3d",), "grid_major"): "#50566cff",
    # Lien et curseur de texte : bleu clair de la sphère
    (("user_interface",), "link"): "#a9b4d0ff",
    (("user_interface",), "widget_text_cursor"): "#a9b4d0",
    # Barre d'état au niveau du panel système
    (("statusbar",), "back"): "#0f1017",
    # Champs de saisie : un filet comme les champs GTK, car le fond sombre laisse peu d'écart
    (("wcol_text",), "outline"): "#2f313eff",
    (("wcol_num",), "outline"): "#2f313eff",
    (("wcol_numslider",), "outline"): "#2f313eff",
}


def hex2rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


S_STOPS = [(v, hex2rgb(c)) for v, c in STOPS]
A_H, A_L, A_S = colorsys.rgb_to_hls(*[v / 255 for v in hex2rgb(ACCENT)])
B_H, B_L, B_S = colorsys.rgb_to_hls(*[v / 255 for v in hex2rgb("#4772b3")])  # bleu Blender


def ramp(v):
    for (v0, c0), (v1, c1) in zip(S_STOPS, S_STOPS[1:]):
        if v <= v1:
            t = (v - v0) / (v1 - v0)
            return tuple(a + (b - a) * t for a, b in zip(c0, c1))
    return S_STOPS[-1][1]


def to_accent(rgb):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
    s2 = min(1.0, s * A_S / B_S)
    return tuple(v * 255 for v in colorsys.hls_to_rgb(A_H, l, s2))


def is_blender_blue(rgb):
    h, l, s = colorsys.rgb_to_hls(*[v / 255 for v in rgb])
    return 195 / 360 <= h <= 230 / 360 and s > 0.25


COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}([0-9a-fA-F]{2})?$")


def transform(value, attr, tags):
    rgb, alpha = hex2rgb(value), value[7:]
    widget = next((t for t in reversed(tags) if t.startswith("wcol_")), None)
    if is_blender_blue(rgb) and not (set(tags) & SEMANTIC_PARENTS) and (
        attr in ACCENT_ATTRS or (attr == "item" and widget in ACCENT_ITEM_WIDGETS)
    ):
        return rgb2hex(to_accent(rgb)) + alpha
    if max(rgb) - min(rgb) <= 12:
        return rgb2hex(ramp(sum(rgb) / 3)) + alpha
    return value


def walk(el, tags, stats):
    tags = tags + [el.tag]
    for attr, val in list(el.attrib.items()):
        for (suffix, a), new in OVERRIDES.items():
            if a == attr and any(s in tags for s in suffix):
                if COLOR_RE.match(val) and COLOR_RE.match(new) and len(val) != len(new):
                    new = new[:7] + val[7:]
                el.set(attr, new)
                stats["override"] += 1
                break
        else:
            if COLOR_RE.match(val):
                nv = transform(val, attr, tags)
                if nv.lower() != val.lower():
                    el.set(attr, nv)
                    stats["changed"] += 1
    for c in el:
        walk(c, tags, stats)


def main():
    src, dst = sys.argv[1], sys.argv[2]
    tree = ET.parse(src)
    stats = {"changed": 0, "override": 0}
    walk(tree.getroot(), [], stats)
    ET.indent(tree, space="  ")
    tree.write(dst, encoding="unicode")
    print("Couleurs modifiées :", stats["changed"], "| retouches :", stats["override"])


if __name__ == "__main__":
    main()
