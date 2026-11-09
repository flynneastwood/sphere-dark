#!/usr/bin/env bash
# Rend Sphere-Dark et tes icônes (Nordzy par défaut) visibles pour l'écran de connexion.
#
# Usage :
#   sudo ./installer-pour-connexion.sh                 # thème Sphere-Dark + icônes Nordzy*
#   sudo ./installer-pour-connexion.sh 'Papirus*'      # autre motif pour les icônes
#
# L'outil « Fenêtre de connexion » et l'écran de connexion ne voient que les dossiers système :
#   thèmes  -> /usr/share/themes  (le thème doit avoir gtk-2.0 et gtk-3.0)
#   icônes  -> /usr/share/icons   (index.theme avec une ligne « Directories= »)
# Ce script y copie tes thèmes personnels. Il ne modifie aucune configuration :
# tu choisis ensuite le thème et les icônes dans « Fenêtre de connexion ».
set -uo pipefail

PREFIX="${PREFIX:-}"   # pour les tests uniquement
ICON_PATTERN="${1:-Nordzy*}"

if [[ -z "$PREFIX" && $EUID -ne 0 ]]; then
  echo "Lance ce script avec sudo : sudo $0" >&2
  exit 1
fi

TARGET_USER="${SUDO_USER:-$(id -un)}"
USER_HOME="${USER_HOME:-$(getent passwd "$TARGET_USER" | cut -d: -f6)}"
echo "Dossier personnel utilisé : $USER_HOME"
echo

ok=0

# ---------------------------------------------------------------- thème GTK
THEME_SRC=""
for d in "$USER_HOME/.themes/Sphere-Dark" "$USER_HOME/.local/share/themes/Sphere-Dark"; do
  [[ -d "$d" ]] && { THEME_SRC="$d"; break; }
done

if [[ -z "$THEME_SRC" ]]; then
  echo "✗ Thème Sphere-Dark introuvable dans ~/.themes ni ~/.local/share/themes."
elif [[ ! -d "$THEME_SRC/gtk-2.0" || ! -d "$THEME_SRC/gtk-3.0" ]]; then
  echo "✗ $THEME_SRC n'a pas gtk-2.0 et gtk-3.0 : l'outil de connexion l'ignorerait."
else
  mkdir -p "$PREFIX/usr/share/themes"
  rm -rf "$PREFIX/usr/share/themes/Sphere-Dark"
  cp -a "$THEME_SRC" "$PREFIX/usr/share/themes/Sphere-Dark"
  [[ -z "$PREFIX" ]] && chown -R root:root "/usr/share/themes/Sphere-Dark"
  chmod -R a+rX "$PREFIX/usr/share/themes/Sphere-Dark"
  echo "✓ Thème copié : /usr/share/themes/Sphere-Dark"
  if ! grep -q "window.background.lightdm" "$THEME_SRC/gtk-3.0/gtk.css" 2>/dev/null; then
    echo "  (ancienne version du thème : elle fonctionnera, sans les retouches du champ de mot de passe)"
  fi
  ok=$((ok + 1))
fi
echo

# ---------------------------------------------------------------- icônes
found=0
shopt -s nullglob
for base in "$USER_HOME/.local/share/icons" "$USER_HOME/.icons"; do
  for d in "$base"/$ICON_PATTERN; do
    [[ -d "$d" && -f "$d/index.theme" ]] || continue
    grep -q "^Directories=" "$d/index.theme" || continue
    name="$(basename "$d")"
    mkdir -p "$PREFIX/usr/share/icons"
    rm -rf "$PREFIX/usr/share/icons/$name"
    cp -a "$d" "$PREFIX/usr/share/icons/$name"
    [[ -z "$PREFIX" ]] && chown -R root:root "/usr/share/icons/$name"
    chmod -R a+rX "$PREFIX/usr/share/icons/$name"
    if command -v gtk-update-icon-cache >/dev/null; then
      gtk-update-icon-cache -q -f -t "$PREFIX/usr/share/icons/$name" 2>/dev/null || true
    fi
    echo "✓ Icônes copiées : /usr/share/icons/$name"
    found=$((found + 1))
  done
done
if [[ $found -eq 0 ]]; then
  echo "✗ Aucun thème d'icônes « $ICON_PATTERN » trouvé dans ~/.local/share/icons ni ~/.icons."
  echo "  Contenu de ~/.local/share/icons :"; ls -1 "$USER_HOME/.local/share/icons" 2>/dev/null | sed 's/^/    /'
else
  ok=$((ok + 1))
fi
echo

# ---------------------------------------------------------------- bilan
echo "Ce que l'outil « Fenêtre de connexion » pourra proposer :"
echo -n "  Thèmes : "; ls -1 "$PREFIX/usr/share/themes" | while read -r t; do
  [[ -d "$PREFIX/usr/share/themes/$t/gtk-2.0" && -d "$PREFIX/usr/share/themes/$t/gtk-3.0" ]] && echo -n "$t  "; done | grep -o "Sphere-Dark" || echo "(Sphere-Dark absent)"
echo -n "  Icônes : "; for t in "$PREFIX"/usr/share/icons/$ICON_PATTERN; do
  grep -q "^Directories=" "$t/index.theme" 2>/dev/null && echo -n "$(basename "$t")  "; done; echo
echo
if [[ $ok -eq 2 ]]; then
  echo "Ferme puis rouvre « Fenêtre de connexion », choisis Sphere-Dark et tes icônes, puis déconnecte-toi pour voir le résultat."
fi
