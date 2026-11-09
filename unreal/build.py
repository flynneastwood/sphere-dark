#!/usr/bin/env python3
"""
Génère « SphereDark.json », thème d'éditeur Unreal Engine 5 (clés EStyleColor),
avec la palette Sphere-Dark. Les valeurs sont écrites en couleur linéaire, comme UE l'attend.

Usage : python3 build_unreal_theme.py SphereDark.json
"""
import json
import math
import sys

# Rôles (sRGB) -----------------------------------------------------------------
UI = {
    "Black":              "#06070c",
    "Background":         "#191b24",  # fond des fenêtres
    "Title":              "#0f1017",  # barre de titre = chrome
    "WindowBorder":       "#0f1017",
    "Foldout":            "#12141b",
    "Input":              "#13151d",  # champs, comme Blender
    "InputOutline":       "#2f313e",
    "Recessed":           "#12141b",  # zones en retrait (navigateur de contenu)
    "Panel":              "#22242f",  # panneau Détails
    "Header":             "#2f313e",  # en-têtes de catégories, onglets
    "Dropdown":           "#383c4e",  # boutons, comme Blender
    "DropdownOutline":    "#0f1017",
    "Hover":              "#4a4f63",
    "Hover2":             "#6f768c",
    "White":              "#ffffff",
    "Highlight":          "#5a6a9a",
    "Primary":            "#5a6a9a",  # accent du système
    "PrimaryHover":       "#6b7cae",
    "PrimaryPress":       "#3d4a6e",
    "Secondary":          "#383c4e",
    "Foreground":         "#b8bfd3",  # UE garde le texte courant un cran sous le blanc
    "ForegroundHover":    "#eef1fa",
    "ForegroundInverted": "#0f1017",
    "ForegroundHeader":   "#dfe5f5",
    "Select":             "#5a6a9a",
    "SelectInactive":     "#3d4a6e",
    "SelectParent":       "#2c3450",
    "SelectHover":        "#3b3f4e",
    "Notifications":      "#2f313e",
    "AccentBlack":        "#12141b",
    "AccentGray":         "#62687b",
    "AccentWhite":        "#dfe5f5",
    "AccentFolder":       "#7d8ab3",  # dossiers bleu-ardoise, comme les icônes
}
ALPHA = {"White25": ("#ffffff", 0.25)}


def oklch(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    lin = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
           -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
           -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return tuple(max(0.0, min(1.0, v)) for v in lin)  # déjà linéaire


# Accents sémantiques (types d'assets, nœuds, états) : même clarté, saturation retenue
ACCENTS_LIN = {
    "AccentBlue":   oklch(0.70, 0.11, 255),
    "AccentPurple": oklch(0.66, 0.12, 300),
    "AccentPink":   oklch(0.70, 0.12, 350),
    "AccentRed":    oklch(0.62, 0.15, 25),
    "AccentOrange": oklch(0.68, 0.12, 45),   # proche de la rouille du thème
    "AccentYellow": oklch(0.80, 0.11, 90),
    "AccentGreen":  oklch(0.72, 0.12, 150),
    "AccentBrown":  oklch(0.45, 0.06, 50),
}
STATES = {"Warning": "AccentOrange", "Error": "AccentRed", "Success": "AccentGreen"}

ORDER = ["Black", "Background", "Title", "WindowBorder", "Foldout", "Input", "InputOutline", "Recessed",
         "Panel", "Header", "Dropdown", "DropdownOutline", "Hover", "Hover2", "White", "White25", "Highlight",
         "Primary", "PrimaryHover", "PrimaryPress", "Secondary", "Foreground", "ForegroundHover",
         "ForegroundInverted", "ForegroundHeader", "Select", "SelectInactive", "SelectParent", "SelectHover",
         "Notifications", "AccentBlue", "AccentPurple", "AccentPink", "AccentRed", "AccentOrange",
         "AccentYellow", "AccentGreen", "AccentBrown", "AccentBlack", "AccentGray", "AccentWhite",
         "AccentFolder", "Warning", "Error", "Success"] + ["User%d" % i for i in range(1, 17)]


def srgb_to_lin(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16)) for i in (1, 3, 5))


def fmt(rgb, a=1.0):
    return "(R=%.6f,G=%.6f,B=%.6f,A=%.6f)" % (rgb[0], rgb[1], rgb[2], a)


def main():
    colors = {}
    for k in ORDER:
        if k in UI:
            v = fmt(srgb_to_lin(UI[k]))
        elif k in ALPHA:
            v = fmt(srgb_to_lin(ALPHA[k][0]), ALPHA[k][1])
        elif k in ACCENTS_LIN:
            v = fmt(ACCENTS_LIN[k])
        elif k in STATES:
            v = fmt(ACCENTS_LIN[STATES[k]])
        else:  # User1..16 : inutilisées par l'éditeur
            v = fmt((0, 0, 0), 0)
        colors["EStyleColor::" + k] = v
    theme = {"Version": 1, "Id": "5D3A0E2C7B4F4A1E9C6B2F8A1D0E7C35",
             "DisplayName": "Sphere Dark", "Colors": colors}
    with open(sys.argv[1], "w") as f:
        json.dump(theme, f, indent="\t")
    print("Écrit :", sys.argv[1], "-", len(colors), "couleurs")


if __name__ == "__main__":
    main()
