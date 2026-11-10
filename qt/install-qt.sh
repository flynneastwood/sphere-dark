#!/usr/bin/env bash
# Applique Sphere Dark aux applications Qt : KeePassXC, Git Cola, et la plupart des autres.
#
# Usage : ./install-qt.sh        (sans sudo)
#
# 1. installe la palette sphere-dark.conf pour qt5ct (Qt 5) et qt6ct (Qt 6) ;
# 2. règle qt5ct et qt6ct : palette Sphere Dark, style Fusion, tes icônes actuelles ;
# 3. ajoute QT_QPA_PLATFORMTHEME=qt5ct à ~/.profile (qt6ct répond aussi à « qt5ct ») ;
# 4. Git Cola : thème « Default » (qui suit la palette) et couleurs du diff.
# Les fichiers de configuration existants sont sauvegardés (.bak-date) avant modification.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"

if [[ $EUID -eq 0 ]]; then
  echo "Lance ce script sans sudo : il configure ton compte, pas le système." >&2
  exit 1
fi

missing=()
command -v qt5ct >/dev/null || missing+=(qt5ct)
command -v qt6ct >/dev/null || missing+=(qt6ct)
if (( ${#missing[@]} )); then
  echo "À installer d'abord (ou ensuite) : sudo apt install ${missing[*]}"
  echo
fi

ICONS="$(xfconf-query -c xsettings -p /Net/IconThemeName 2>/dev/null || true)"
# Polices d'XFCE (« Famille Taille »), reprises pour que Qt garde la même taille de texte
FONT="$(xfconf-query -c xsettings -p /Gtk/FontName 2>/dev/null || true)"
MONO="$(xfconf-query -c xsettings -p /Gtk/MonospaceFontName 2>/dev/null || true)"

# ---------------------------------------------------------------- qt5ct / qt6ct
for ct in qt5ct qt6ct; do
  dir="$HOME/.config/$ct"
  mkdir -p "$dir/colors"
  cp "$HERE/sphere-dark.conf" "$dir/colors/sphere-dark.conf"
  conf="$dir/$ct.conf"
  [[ -f "$conf" ]] && cp -a "$conf" "$conf.bak-$STAMP"
  python3 - "$conf" "$dir/colors/sphere-dark.conf" "$ICONS" "$FONT" "$MONO" <<'PY'
import configparser, sys
path, scheme, icons, font, mono = sys.argv[1:6]

def qfont(spec):
    """« Noto Sans 10 » -> chaîne QFont lisible par qt5ct et qt6ct."""
    parts = spec.rsplit(" ", 1)
    if len(parts) != 2 or not parts[1].replace(".", "").isdigit():
        return None
    return '"%s,%s,-1,5,50,0,0,0,0,0"' % (parts[0], parts[1])

c = configparser.ConfigParser(interpolation=None)
c.optionxform = str
c.read(path)
if not c.has_section("Appearance"):
    c.add_section("Appearance")
a = c["Appearance"]
a["color_scheme_path"] = scheme
a["custom_palette"] = "true"
a["style"] = "Fusion"
if icons:
    a["icon_theme"] = icons
a.setdefault("standard_dialogs", "default")
if not c.has_section("Fonts"):
    c.add_section("Fonts")
for key, spec in (("general", font), ("fixed", mono)):
    q = qfont(spec) if spec else None
    if q:
        c["Fonts"][key] = q
with open(path, "w") as f:
    c.write(f, space_around_delimiters=False)
PY
  echo "✓ $ct : palette Sphere Dark, style Fusion${ICONS:+, icônes $ICONS}${FONT:+, police $FONT}"
done

# ---------------------------------------------------------------- variable d'environnement
PROFILE="$HOME/.profile"
if grep -qs "^[^#]*QT_QPA_PLATFORMTHEME=[\"']\?qt5ct" "$PROFILE"; then
  echo "✓ ~/.profile : QT_QPA_PLATFORMTHEME=qt5ct déjà présent"
elif grep -qs "^[^#]*QT_QPA_PLATFORMTHEME" "$PROFILE"; then
  echo "• ~/.profile définit QT_QPA_PLATFORMTHEME avec une autre valeur :"
  grep "^[^#]*QT_QPA_PLATFORMTHEME" "$PROFILE" | sed 's/^/    /'
  echo "  Remplace-la par qt5ct pour que la palette s'applique."
else
  [[ -f "$PROFILE" ]] && cp -a "$PROFILE" "$PROFILE.bak-$STAMP"
  printf '\n# Sphere Dark : applications Qt 5 et Qt 6 via qt5ct / qt6ct\nexport QT_QPA_PLATFORMTHEME=qt5ct\n' >> "$PROFILE"
  echo "✓ ~/.profile : QT_QPA_PLATFORMTHEME=qt5ct ajouté"
fi

# ---------------------------------------------------------------- Git Cola
if command -v git >/dev/null; then
  git config --global cola.theme default          # suit la palette du système
  git config --global cola.color.text   eef1fa     # texte des lignes ajoutées / retirées
  git config --global cola.color.add    2c4535     # fond des lignes ajoutées (vert sourd)
  git config --global cola.color.remove 4d2f2b     # fond des lignes retirées (rouille sourde)
  git config --global cola.color.header 8b92a8     # en-têtes de diff
  echo "✓ Git Cola : thème Default et couleurs du diff (git config --global cola.*)"
fi

echo
echo "Déconnecte-toi puis reconnecte-toi pour que la variable soit prise en compte."
echo "Dans KeePassXC : Paramètres → Interface → Thème de l'application → Classique."
