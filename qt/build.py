#!/usr/bin/env python3
"""
Génère « sphere-dark.conf », palette pour qt5ct et qt6ct (Qt 5 et Qt 6).
Les applications Qt qui suivent la palette du système l'utilisent : KeePassXC (thème
« Classique »), Git Cola (thème « Default »), et la plupart des autres.

Usage : python3 build_qt_palette.py sphere-dark.conf
Ordre des rôles : celui de QPalette::ColorRole, 21 couleurs exactement : qt5ct rejette
sans message toute autre longueur, et qt6ct (Qt >= 6.6) ajoute lui-même Accent = Highlight.
"""
import sys

ROLES = ["WindowText", "Button", "Light", "Midlight", "Dark", "Mid", "Text", "BrightText",
         "ButtonText", "Base", "Window", "Shadow", "Highlight", "HighlightedText", "Link",
         "LinkVisited", "AlternateBase", "NoRole", "ToolTipBase", "ToolTipText",
         "PlaceholderText"]

ACTIVE = {
    "WindowText": "#dfe5f5", "Button": "#2f313e", "Light": "#4a4f63", "Midlight": "#3b3f4e",
    "Dark": "#0f1017", "Mid": "#22242f", "Text": "#dfe5f5", "BrightText": "#ffffff",
    "ButtonText": "#dfe5f5", "Base": "#22242f", "Window": "#191b24", "Shadow": "#06070c",
    "Highlight": "#5a6a9a", "HighlightedText": "#ffffff", "Link": "#a9b4d0",
    "LinkVisited": "#bb94c7", "AlternateBase": "#262835", "NoRole": "#191b24",
    "ToolTipBase": "#0f1017", "ToolTipText": "#dfe5f5", "PlaceholderText": "#8b92a8",
}
# Fenêtre inactive : sélection plus sourde (comme SelectInactive dans Unreal)
INACTIVE = dict(ACTIVE, Highlight="#3d4a6e", HighlightedText="#dfe5f5")
DISABLED = dict(ACTIVE, WindowText="#62687b", Text="#62687b", ButtonText="#62687b",
                Base="#1c1e29", Button="#262835", Highlight="#2f313e",
                HighlightedText="#8b92a8", PlaceholderText="#4a4f63", Link="#62687b")


def row(d):
    assert len(ROLES) == 21
    return ", ".join("#ff" + d[r].lstrip("#") for r in ROLES)


with open(sys.argv[1], "w") as f:
    f.write("[ColorScheme]\n")
    f.write("active_colors=" + row(ACTIVE) + "\n")
    f.write("disabled_colors=" + row(DISABLED) + "\n")
    f.write("inactive_colors=" + row(INACTIVE) + "\n")
print("Écrit :", sys.argv[1])
