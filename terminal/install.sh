#!/usr/bin/env bash
# Installe le schéma de couleurs « Sphere Dark » pour xfce4-terminal
# et ajoute une marge intérieure aux terminaux (VTE).
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"

dest="$HOME/.local/share/xfce4/terminal/colorschemes"
mkdir -p "$dest"
cp "$here/sphere-dark.theme" "$dest/"
echo "Schéma installé dans $dest"

css="$HOME/.config/gtk-3.0/gtk.css"
mkdir -p "$(dirname "$css")"
if ! grep -q "Sphere-Dark terminal" "$css" 2>/dev/null; then
  cat >> "$css" <<'CSS'

/* Sphere-Dark terminal : marge intérieure pour que le texte respire */
vte-terminal { padding: 10px 14px; }
CSS
  echo "Marge ajoutée dans $css"
fi
echo "Ouvre un nouveau terminal, puis Préférences > Couleurs > Préréglages > « Sphere Dark »."
