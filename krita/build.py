#!/usr/bin/env python3
"""
Génère « Sphere Dark.colors » pour Krita à partir de KritaDarker.colors (fourni avec Krita),
en appliquant les rôles de couleur du thème système Sphere-Dark.

Usage : python3 build_krita_theme.py KritaDarker.colors "Sphere Dark.colors"
"""
import configparser
import sys

PAL = {
    "deep": "#0f1017", "bg": "#191b24", "bg_alt": "#1c1e29",
    "surface": "#22242f", "surface_alt": "#262835",
    "raised": "#2f313e", "line": "#3b3f4e",
    "dim": "#8b92a8", "text": "#dfe5f5", "text_hi": "#eef1fa",
    "accent": "#5a6a9a", "accent_dark": "#3d4a6e", "accent_hover": "#7d8ab3",
    "light": "#a9b4d0",
    # couleurs d'état : mêmes teintes que la palette du terminal
    "neg": "#d59087", "neu": "#bfa060", "pos": "#7eb488", "visited": "#bb94c7",
    "neg_hi": "#f1b2a9", "neu_hi": "#ddc084", "pos_hi": "#a2d2ab", "visited_hi": "#d9b5e4",
}


def rgb(h):
    return ",".join(str(int(h[i:i + 2], 16)) for i in (1, 3, 5))


COMMON_FG = {
    "ForegroundNormal": "text", "ForegroundActive": "text_hi", "ForegroundInactive": "dim",
    "ForegroundLink": "light", "ForegroundVisited": "visited",
    "ForegroundNegative": "neg", "ForegroundNeutral": "neu", "ForegroundPositive": "pos",
    "DecorationFocus": "light", "DecorationHover": "accent_hover",
}
SETS = {
    # rôle KDE         : (fond normal, fond alterné)
    "Colors:Window":        ("bg", "bg_alt"),        # docks, fenêtres = fond des fenêtres du système
    "Colors:View":          ("surface", "surface_alt"),  # listes (calques), champs = surfaces GTK
    "Colors:Button":        ("raised", "line"),      # boutons
    "Colors:Complementary": ("deep", "bg"),          # zones sombres = barres de titre / panel
    "Colors:Header":        ("deep", "bg"),
    "Colors:Tooltip":       ("deep", "bg"),
    "Colors:Selection":     ("accent", "accent_dark"),
}


def main():
    src, dst = sys.argv[1], sys.argv[2]
    cp = configparser.ConfigParser(interpolation=None)
    cp.optionxform = str
    cp.read(src)

    for section, (bg, alt) in SETS.items():
        if not cp.has_section(section):
            cp.add_section(section)
        s = cp[section]
        s["BackgroundNormal"] = rgb(PAL[bg])
        s["BackgroundAlternate"] = rgb(PAL[alt])
        for key, role in COMMON_FG.items():
            s[key] = rgb(PAL[role])

    sel = cp["Colors:Selection"]
    sel["ForegroundNormal"] = "255,255,255"
    sel["ForegroundActive"] = "255,255,255"
    sel["ForegroundInactive"] = rgb(PAL["text"])
    sel["ForegroundLink"] = rgb("#eef1fa")
    sel["ForegroundVisited"] = rgb(PAL["visited_hi"])
    sel["ForegroundNegative"] = rgb(PAL["neg_hi"])
    sel["ForegroundNeutral"] = rgb(PAL["neu_hi"])
    sel["ForegroundPositive"] = rgb(PAL["pos_hi"])

    cp["ColorEffects:Disabled"]["Color"] = rgb("#14161e")

    wm = cp["WM"]
    wm["activeBackground"] = rgb(PAL["deep"])
    wm["activeForeground"] = rgb(PAL["text_hi"])
    wm["activeBlend"] = rgb(PAL["text_hi"])
    wm["inactiveBackground"] = rgb(PAL["deep"])
    wm["inactiveForeground"] = rgb("#6b7186")
    wm["inactiveBlend"] = rgb("#6b7186")

    cp["General"]["ColorScheme"] = "Sphere Dark"
    cp["General"]["Name"] = "Sphere Dark"

    with open(dst, "w") as f:
        cp.write(f, space_around_delimiters=False)
    print("Écrit :", dst)


if __name__ == "__main__":
    main()
