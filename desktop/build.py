#!/usr/bin/env python3
"""
Génère le thème « Sphere-Dark » (GTK2/3/4 + xfwm4 + libadwaita) à partir
des sources de Mint-Y (dépôt linuxmint/mint-themes, dossier src/Mint-Y),
recoloré avec la palette tirée du fond d'écran.

Usage : python3 -I build_sphere_theme.py <chemin/mint-themes/src/Mint-Y> <dossier-sortie>
Prérequis : Pillow, et pysassc (pip install libsass) ou sassc (apt install sassc).
Pour changer les couleurs, modifier uniquement la section PALETTE.
"""
import colorsys
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

# ----------------------------------------------------------------- PALETTE
NAME = "Sphere-Dark"
PAL = {
    "deep":    "#0f1017",  # panel, barres de titre, en-têtes
    "bg":      "#191b24",  # fond des fenêtres
    "surface": "#22242f",  # champs de saisie, vues, menus
    "raised":  "#2f313e",  # survol, bordures
    "line":    "#3b3f4e",
    "muted":   "#62687b",
    "dim":     "#8b92a8",  # texte atténué
    "text":    "#dfe5f5",  # texte principal
    "accent":  "#5a6a9a",  # sélection, cases cochées, boutons actifs (texte blanc lisible dessus)
    "light":   "#a9b4d0",  # liens, soulignés, contours de focus (intérieur de la sphère)
    "rim":     "#444a60",  # liseré lumineux en haut des barres de titre actives
    "rust":    "#b4694f",  # accent secondaire rare : survol du bouton fermer, actions destructives
}

# Barres de titre xfwm4 : dégradé « lumière venue du haut » et bordures
XFWM = {
    "active":   {"top": "#1a1d29", "bottom": "#12141c", "rim": PAL["rim"],   "border": "#33374a",
                 "text": "#eef1fa"},
    "inactive": {"top": PAL["deep"], "bottom": PAL["deep"], "rim": PAL["surface"], "border": "#252733",
                 "text": "#6b7186"},
}

# Couleurs de Mint-Y-Dark à remplacer
OLD_ACCENT = "#35a854"
# Rampe de gris : luminance 0-255 de l'ancien thème -> nouvelle couleur de la palette
STOPS = [
    (0, "#06070c"), (34, PAL["deep"]), (46, PAL["bg"]), (51, PAL["surface"]),
    (76, PAL["raised"]), (97, PAL["line"]), (144, PAL["muted"]),
    (167, PAL["dim"]), (218, PAL["text"]), (255, "#ffffff"),
]


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in c)


STOPS_RGB = [(v, hex2rgb(c)) for v, c in STOPS]
OLD_H, OLD_L, OLD_S = colorsys.rgb_to_hls(*[v / 255 for v in hex2rgb(OLD_ACCENT)])
NEW_H, NEW_L, NEW_S = colorsys.rgb_to_hls(*[v / 255 for v in hex2rgb(PAL["accent"])])


def ramp(v):
    for (v0, c0), (v1, c1) in zip(STOPS_RGB, STOPS_RGB[1:]):
        if v <= v1:
            t = (v - v0) / (v1 - v0) if v1 > v0 else 0
            return tuple(a + (b - a) * t for a, b in zip(c0, c1))
    return STOPS_RGB[-1][1]


def remap_rgb(r, g, b):
    """Remappe un pixel : vert d'accent -> nouvel accent, gris -> rampe, reste inchangé."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    chroma = max(r, g, b) - min(r, g, b)
    if chroma > 30 and s > 0.2 and 80 / 360 <= h <= 170 / 360:
        l2 = max(0.0, min(1.0, NEW_L + (l - OLD_L)))
        rr, gg, bb = colorsys.hls_to_rgb(NEW_H, l2, NEW_S)
        return (rr * 255, gg * 255, bb * 255)
    if chroma <= 48:
        return ramp(0.299 * r + 0.587 * g + 0.114 * b)
    return (r, g, b)


def remap_hex(m):
    h = m.group(0)
    if h.lower() == OLD_ACCENT:
        return PAL["accent"]
    r, g, b = hex2rgb(h)
    return rgb2hex(remap_rgb(r, g, b))


HEX_RE = re.compile(r"#[0-9a-fA-F]{6}\b")


def remap_text_file(path):
    with open(path, encoding="utf-8", errors="surrogateescape") as f:
        s = f.read()
    s2 = HEX_RE.sub(remap_hex, s)
    if s2 != s:
        with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
            f.write(s2)


_cache = {}


def recolor_png(path):
    im = Image.open(path).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            key = (r, g, b)
            if key not in _cache:
                _cache[key] = tuple(round(v) for v in remap_rgb(r, g, b))
            nr, ng, nb = _cache[key]
            px[x, y] = (max(0, min(255, nr)), max(0, min(255, ng)), max(0, min(255, nb)), a)
    im.save(path)


# ------------------------------------------------------------------- SASS
SPHERE_SCSS = r'''// =====================================================================
// Sphere-Dark : couche de finition (GTK3), ajoutée après Mint-Y-Dark.
// Les règles ici l'emportent sur Mint-Y parce qu'elles viennent en dernier.
// =====================================================================

$sphere_line:  #2f313e;   // séparateurs entre niveaux de surface
$sphere_rim:   #444a60;   // liseré lumineux (arête éclairée de la sphère)
$sphere_light: #a9b4d0;   // accent clair (intérieur de la sphère)
$sphere_rust:  #b4694f;   // accent secondaire rare (liseré rouille)
$sphere_title_top:    #1a1d29;
$sphere_title_bottom: #12141c;

// ---------------------------------------------------------------------
// 1. Trois niveaux : chrome (#0f1017) > base (#191b24) > contenu (#22242f)
// ---------------------------------------------------------------------

// En-têtes de colonnes : au niveau du contenu, séparés par une ligne
treeview.view header button {
  background-color: $base_color;
  color: $dim_label_fg_color;
  font-weight: normal;
  border-color: $sphere_line;
  border-style: none solid solid none;

  &:hover, &:active { background-color: lighten($base_color, 3%); color: $fg_color; }
}

// Séparateur visible entre barre latérale et contenu
paned > separator { background-color: $sphere_line; }

// Barre d'état au niveau de base, filet en haut
statusbar { background-color: $bg_color; border-top: 1px solid $sphere_line; }

// ---------------------------------------------------------------------
// 2. Focus : plus de pointillés, contour plein et discret
// ---------------------------------------------------------------------
treeview.view, iconview, .view, list, listbox {
  outline-style: solid;
  outline-color: transparentize($sphere_light, 0.7);
}

// ---------------------------------------------------------------------
// 3. Barres de titre côté client (applications avec headerbar)
//    Même logique que xfwm4 : dégradé venu du haut + liseré lumineux.
// ---------------------------------------------------------------------
headerbar,
.titlebar:not(headerbar) {
  background-color: $sphere_title_bottom;
  background-image: linear-gradient(to bottom, $sphere_title_top, $sphere_title_bottom);
  box-shadow: inset 0 1px $sphere_rim, inset 0 -1px $header_border;

  &:backdrop {
    background-image: none;
    background-color: $header_bg;
    box-shadow: inset 0 1px $base_color, inset 0 -1px $header_border;
  }
}

// ---------------------------------------------------------------------
// 4. Panel XFCE : bouton actif souligné au lieu d'un bloc plein
//    (le trait est en bas : prévu pour un panel en bas d'écran)
// ---------------------------------------------------------------------
.xfce4-panel.panel button {
  &:hover {
    background-color: transparentize(white, 0.94);
  }
  &:checked, &:active {
    color: $panel_fg;
    background-color: transparentize($sphere_light, 0.9);
    box-shadow: inset 0 -2px $sphere_light;
  }
  &:checked:hover { background-color: transparentize($sphere_light, 0.84); }
}

// ---------------------------------------------------------------------
// 5. Menu Whisker : survol et catégorie active dans la palette
// ---------------------------------------------------------------------
#whiskermenu-window {
  background-color: $bg_color;

  button {
    &:hover { background-color: $sphere_line; }
    &:checked, &:active {
      color: $text_color;
      background-color: transparentize($sphere_light, 0.88);
      box-shadow: inset 2px 0 $sphere_light;
    }
  }

  treeview.view:hover, iconview:hover { background-color: $sphere_line; }
  entry { background-color: $base_color; border-color: $sphere_line; }
}

// ---------------------------------------------------------------------
// 6. Accent rouille : réservé aux actions destructives
// ---------------------------------------------------------------------
button.destructive-action {
  background-color: $sphere_rust;
  border-color: darken($sphere_rust, 12%);
  color: white;
  &:hover { background-color: lighten($sphere_rust, 6%); }
  &:active { background-color: darken($sphere_rust, 8%); }
}

// ---------------------------------------------------------------------
// 8. Indicateur de défilement : un léger dégradé d'ombre au lieu des tirets
//    (même logique que la lumière qui vient du haut)
// ---------------------------------------------------------------------
scrolledwindow undershoot {
  padding: 0;
  background-color: transparent;
  background-repeat: no-repeat;
  background-origin: border-box;

  &.top    { background-image: linear-gradient(to bottom, rgba(6, 7, 12, 0.45), transparent); background-size: 100% 10px; background-position: top; }
  &.bottom { background-image: linear-gradient(to top,    rgba(6, 7, 12, 0.45), transparent); background-size: 100% 10px; background-position: bottom; }
  &.left   { background-image: linear-gradient(to right,  rgba(6, 7, 12, 0.45), transparent); background-size: 10px 100%; background-position: left; }
  &.right  { background-image: linear-gradient(to left,   rgba(6, 7, 12, 0.45), transparent); background-size: 10px 100%; background-position: right; }
}

// ---------------------------------------------------------------------
// 9. Thunar : la barre d'emplacement devient un champ, comme la barre d'adresse
//    de Firefox. Elle contient un bouton vide de remplissage, qui créait une bande
//    plus claire que le contenu ; tous ses boutons deviennent transparents.
// ---------------------------------------------------------------------
.thunar .path-bar {
  background-color: $base_color;
  border: 1px solid $sphere_line;
  border-radius: 4px;

  button {
    background-color: transparent;
    background-image: none;
    border-color: transparent;
    box-shadow: none;
    color: $dim_label_fg_color;

    &:hover { background-color: transparentize($sphere_light, 0.9); color: $fg_color; }
    &:checked, &:active { background-color: $sphere_line; color: $text_color; }
  }
}

// ---------------------------------------------------------------------
// 7. Écran de connexion (slick-greeter / LightDM)
//    La boîte et la barre du haut sont dessinées par le greeter lui-même
//    (fond flouté assombri) ; on règle ici les champs, boutons et textes.
// ---------------------------------------------------------------------
window.background.lightdm {
  color: $text_color;

  entry {
    background-color: transparentize($header_bg, 0.45);
    border-color: transparentize($sphere_light, 0.65);
    border-radius: 6px;
    color: $text_color;
    caret-color: $sphere_light;

    &:focus {
      border-color: $sphere_light;
      box-shadow: 0 0 0 1px transparentize($sphere_light, 0.7);
      color: white;
    }
    &:selected { background-color: $accent_color; }
    image { color: $sphere_light; }
  }

  button,
  button.toggle-button,
  button.flat.option-button {
    color: $text_color;
    border-color: transparent;
    background-color: transparent;

    &:hover {
      border-color: transparent;
      background-color: transparentize($sphere_light, 0.86);
    }
    &:active,
    &:checked,
    &.selected {
      border-color: transparent;
      background-color: $accent_color;
      color: white;
    }
  }

  menubar,
  menubar > menuitem,
  menubar label { color: $text_color; }
  menu { background-color: $bg_color; color: $text_color; }
  menu menuitem:hover { background-color: $accent_color; color: white; }
}
'''

DARK_OVERRIDES = {
    "base_color": PAL["surface"],
    "text_color": PAL["text"],
    "header_bg": PAL["deep"],
    "bg_color": PAL["bg"],
    "borders_color": PAL["raised"],
    "separator_color": PAL["surface"],
    "header_highlight": PAL["raised"],
    "osd_bg_color": PAL["bg"],
    "wm_title_unfocused": PAL["dim"],
    "wm_button_hover_bg": PAL["raised"],
    "wm_button_active_bg": PAL["muted"],
    "wm_icon_bg": PAL["dim"],
    "wm_icon_unfocused_bg": PAL["line"],
    "wm_icon_hover_bg": PAL["text"],
}
GLOBAL_OVERRIDES = {
    "accent_color": PAL["accent"],
    "link_color": PAL["light"],
    "link_visited_color": PAL["light"],
    "xfce_panel_bg": PAL["deep"],
    "panel_bg": PAL["deep"],
    "panel_fg": PAL["text"],
    "terminal_bg": PAL["deep"],
    "osd_fg_color": PAL["text"],
    "dark_sidebar_bg": PAL["bg"],
    "destructive_color": PAL["rust"],
    "suggested_color": PAL["accent"],
    "success_color": "#6fa58a",
    "question_color": PAL["light"],
}


def patch_colors_scss(path):
    with open(path) as f:
        lines = f.read().split("\n")
    # Bloc « dark » : de "} @else {" jusqu'au "}" en début de ligne qui suit
    start = next(i for i, l in enumerate(lines) if l.startswith("} @else {"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("}"))
    for i in range(start, end):
        for name, val in DARK_OVERRIDES.items():
            m = re.match(r"^(\s+\$%s:\s*)[^;]+;(.*)$" % name, lines[i])
            if m:
                lines[i] = "%s%s;%s" % (m.group(1), val, m.group(2))
    for i, l in enumerate(lines):
        for name, val in GLOBAL_OVERRIDES.items():
            m = re.match(r"^(\$%s:\s*)[^;]+;(.*)$" % name, l)
            if m:
                lines[i] = "%s%s;%s" % (m.group(1), val, m.group(2))
    with open(path, "w") as f:
        f.write("\n".join(lines))


def sass_compile(cwd, src, dst):
    exe = shutil.which("pysassc") or shutil.which("sassc")
    if not exe:
        sys.exit("pysassc/sassc introuvable (pip install libsass  ou  apt install sassc)")
    subprocess.run([exe, src, dst], cwd=cwd, check=True)


def build_gtk(build_dir, gtk):
    d = os.path.join(build_dir, gtk)
    sass = os.path.join(d, "sass")
    patch_colors_scss(os.path.join(sass, "_colors.scss"))
    for fn in os.listdir(sass):
        if fn.endswith(".scss") and fn != "_colors.scss" and not fn.startswith("gtk"):
            remap_text_file(os.path.join(sass, fn))
    # Focus : contour plein et discret au lieu des pointillés
    for fn in os.listdir(sass):
        if fn.endswith(".scss"):
            fp = os.path.join(sass, fn)
            with open(fp) as f:
                c = f.read()
            if "outline-style: dashed;" in c:
                with open(fp, "w") as f:
                    f.write(c.replace("outline-style: dashed;", "outline-style: solid;"))
    common = os.path.join(sass, "_common.scss")
    with open(common) as f:
        c = f.read()
    c = c.replace("outline-style: dashed;", "outline-style: solid;")
    c = c.replace("outline-color: transparentize($fg_color, 0.7);\n  outline-style: solid;",
                  "outline-color: transparentize(%s, 0.7);\n  outline-style: solid;" % PAL["light"], 1)
    with open(common, "w") as f:
        f.write(c)
    # Couche de finition (GTK3 : panel, Thunar, Whisker...), ajoutée en dernier
    if gtk == "gtk-3.0":
        with open(os.path.join(sass, "_sphere.scss"), "w") as f:
            f.write(SPHERE_SCSS)
        with open(os.path.join(sass, "gtk-dark.scss"), "a") as f:
            f.write("\n@import 'sphere';\n")
    sass_compile(d, "sass/gtk-dark.scss", "gtk-dark.css")


# ------------------------------------------------------------------ XFWM4
def _lerp(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


def refinish_xfwm(xd):
    """Barre de titre active/inactive distincte, liseré lumineux, bordure visible, fermer en rouille."""
    old_bg = hex2rgb(PAL["deep"])
    old_edge = hex2rgb(PAL["bg"])
    white = (255, 255, 255)
    for fn in sorted(os.listdir(xd)):
        if not fn.endswith(".png"):
            continue
        name = fn[:-4]
        st = XFWM["inactive" if name.endswith("-inactive") else "active"]
        frame_piece = name.split("-")[0] in ("left", "right", "bottom")
        im = Image.open(os.path.join(xd, fn)).convert("RGBA")
        px = im.load()
        w, h = im.size
        # couleur principale du bouton (disque), hors fond et hors liseré
        counts = {}
        for y in range(1, h):
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 255 and (r, g, b) not in (old_bg, old_edge) and min(r, g, b) < 230:
                    counts[(r, g, b)] = counts.get((r, g, b), 0) + 1
        disc = max(counts, key=counts.get) if counts and max(counts.values()) > 40 else None
        new_disc = disc
        if name.startswith("close-") and disc is not None:
            if name.endswith("-prelight"):
                new_disc = hex2rgb(PAL["rust"])
            elif name.endswith("-pressed"):
                new_disc = tuple(v * 0.8 for v in hex2rgb(PAL["rust"]))
        top, bot = hex2rgb(st["top"]), hex2rgb(st["bottom"])
        for y in range(h):
            nbg = old_bg if frame_piece else _lerp(top, bot, max(0, y - 1) / max(1, h - 2))
            for x in range(w):
                r, g, b, a = px[x, y]
                if a == 0:
                    continue
                p = (r, g, b)
                if p == old_edge:
                    c = hex2rgb(st["rim"]) if (y == 0 and not frame_piece) else hex2rgb(st["border"])
                elif frame_piece:
                    continue
                else:
                    # p = bg + u*(disc-bg) + v*(white-bg)  -> même mélange sur le nouveau fond
                    vecs = [tuple(c1 - c0 for c1, c0 in zip(white, old_bg))]
                    if disc is not None:
                        vecs.insert(0, tuple(c1 - c0 for c1, c0 in zip(disc, old_bg)))
                    d = tuple(c1 - c0 for c1, c0 in zip(p, old_bg))
                    coef = _lstsq(vecs, d)
                    targets = ([new_disc] if disc is not None else []) + [white]
                    c = list(nbg)
                    for k, t in zip(coef, targets):
                        k = max(0.0, min(1.0, k))
                        c = [ci + k * (ti - ni) for ci, ti, ni in zip(c, t, nbg)]
                px[x, y] = tuple(max(0, min(255, round(v))) for v in c) + (a,)
        im.save(os.path.join(xd, fn))

    themerc = os.path.join(xd, "themerc")
    with open(themerc) as f:
        t = f.read()
    for key, val in (("active_text_color", XFWM["active"]["text"]),
                     ("active_text_shadow_color", XFWM["active"]["text"]),
                     ("inactive_text_color", XFWM["inactive"]["text"]),
                     ("inactive_text_shadow_color", XFWM["inactive"]["text"])):
        t = re.sub(r"^%s=.*$" % key, "%s=%s" % (key, val), t, flags=re.M)
    with open(themerc, "w") as f:
        f.write(t)


def _lstsq(vecs, d):
    """Moindres carrés pour 1 ou 2 vecteurs RGB."""
    if len(vecs) == 1:
        a = vecs[0]
        n = sum(x * x for x in a) or 1
        return [sum(x * y for x, y in zip(a, d)) / n]
    a, b = vecs
    aa = sum(x * x for x in a); bb = sum(x * x for x in b); ab = sum(x * y for x, y in zip(a, b))
    ad = sum(x * y for x, y in zip(a, d)); bd = sum(x * y for x, y in zip(b, d))
    det = aa * bb - ab * ab or 1
    return [(ad * bb - bd * ab) / det, (bd * aa - ad * ab) / det]


# ------------------------------------------------------------------ BUILD
def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    theme = os.path.join(out, NAME)
    if os.path.exists(theme):
        shutil.rmtree(theme)
    os.makedirs(theme)

    with tempfile.TemporaryDirectory() as tmp:
        build = os.path.join(tmp, "Mint-Y")
        shutil.copytree(src, build)

        build_gtk(build, "gtk-3.0")
        build_gtk(build, "gtk-4.0")

        # GTK 2
        g2 = os.path.join(theme, "gtk-2.0")
        os.makedirs(g2)
        shutil.copytree(os.path.join(build, "gtk-2.0/assets-dark"), os.path.join(g2, "assets"))
        for fn in os.listdir(os.path.join(build, "gtk-2.0")):
            if fn.endswith(".rc") and "-dark" not in fn:
                shutil.copy(os.path.join(build, "gtk-2.0", fn), g2)
        shutil.copy(os.path.join(build, "gtk-2.0/gtkrc-dark"), os.path.join(g2, "gtkrc"))
        shutil.copy(os.path.join(build, "gtk-2.0/menubar-toolbar-dark.rc"), os.path.join(g2, "menubar-toolbar.rc"))

        # GTK 3 et 4
        for gtk in ("gtk-3.0", "gtk-4.0"):
            d = os.path.join(theme, gtk)
            os.makedirs(d)
            shutil.copytree(os.path.join(build, gtk, "assets"), os.path.join(d, "assets"))
            shutil.copy(os.path.join(build, gtk, "gtk-dark.css"), os.path.join(d, "gtk.css"))
            shutil.copy(os.path.join(build, gtk, "gtk-dark.css"), os.path.join(d, "gtk-dark.css"))

        # xfwm4 (bordures de fenêtres)
        xd = os.path.join(theme, "xfwm4")
        os.makedirs(xd)
        for fn in os.listdir(os.path.join(build, "xfwm4-dark")):
            if fn.endswith(".png") or fn == "themerc":
                shutil.copy(os.path.join(build, "xfwm4-dark", fn), xd)

        # libadwaita / libadapta
        for fn in os.listdir(build):
            if fn.startswith(("libadwaita-", "libadapta-")):
                shutil.copytree(os.path.join(build, fn), os.path.join(theme, fn))

    # Recoloration des fichiers texte et des images
    for root, _, files in os.walk(theme):
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, theme)
            if fn.endswith(".png"):
                recolor_png(p)
            elif rel.startswith("gtk-2.0") and (fn.endswith(".rc") or fn == "gtkrc"):
                remap_text_file(p)
            elif rel.startswith(("libadwaita-", "libadapta-")) and fn.endswith(".css"):
                remap_text_file(p)
            elif rel == os.path.join("xfwm4", "themerc"):
                remap_text_file(p)

    refinish_xfwm(os.path.join(theme, "xfwm4"))

    with open(os.path.join(theme, "index.theme"), "w") as f:
        f.write(
            "[Desktop Entry]\nType=X-GNOME-Metatheme\nName=%s\n"
            "Comment=Thème sombre bleu-ardoise tiré d'un fond d'écran (base Mint-Y)\n"
            "Encoding=UTF-8\n\n[X-GNOME-Metatheme]\nGtkTheme=%s\nMetacityTheme=%s\n"
            "IconTheme=Papirus-Dark\nButtonLayout=:minimize,maximize,close\n" % (NAME, NAME, NAME)
        )
    print("Thème généré :", theme)


if __name__ == "__main__":
    main()
