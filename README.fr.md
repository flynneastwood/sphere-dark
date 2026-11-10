# Sphere Dark

*[English version](README.md)*

Un thème sombre bleu-ardoise et posé, tiré d'un seul fond d'écran éclairé en studio, et appliqué de façon cohérente au bureau et aux outils de création autour : Linux Mint XFCE, le terminal, l'écran de connexion, Blender, Krita, Unreal Engine, Ardour, KeePassXC, Git Cola, Firefox et YouTube.

![Fond d'écran d'où vient la palette](docs/wallpaper-preview.jpg)

![Aperçu du bureau](docs/screenshots/desktop.png)

## Principes

- **Trois niveaux de surface.** Le chrome (barres de titre, panel, menus) est le plus foncé, la base (fenêtres, barres latérales, barres d'état) est au milieu, le contenu (listes de fichiers, champs) est le plus clair. Des filets fins les séparent.
- **La lumière vient du haut.** Les barres de titre actives ont un léger dégradé et un liseré lumineux de 1 px, comme le faisceau du fond d'écran. Les fenêtres inactives sont plates et atténuées.
- **Un accent calme.** Bleu-ardoise `#5a6a9a` pour la sélection et les contrôles actifs ; bleu pâle `#a9b4d0` (l'intérieur de la sphère) pour les liens, le focus et les soulignés.
- **Un accent chaud, rare.** Rouille `#b4694f` (l'arête de la sphère), seulement pour les actions destructives, le survol du bouton fermer et les alertes.
- **La fonction d'abord.** Les couleurs qui ont un sens dans une application (axes de Blender, orange de sélection, VU-mètres, boutons d'enregistrement) ne sont pas touchées.

## Palette

La liste complète est dans [`palette.json`](palette.json).

| Rôle | Couleur | |
|---|---|---|
| Chrome (barres de titre, panel) | `#0f1017` | ![](docs/swatches/0f1017.png) |
| Fond des fenêtres | `#191b24` | ![](docs/swatches/191b24.png) |
| Surfaces (champs, listes, menus) | `#22242f` | ![](docs/swatches/22242f.png) |
| Relief / bordures | `#2f313e` | ![](docs/swatches/2f313e.png) |
| Texte atténué | `#8b92a8` | ![](docs/swatches/8b92a8.png) |
| Texte principal | `#dfe5f5` | ![](docs/swatches/dfe5f5.png) |
| Accent | `#5a6a9a` | ![](docs/swatches/5a6a9a.png) |
| Accent clair | `#a9b4d0` | ![](docs/swatches/a9b4d0.png) |
| Accent rouille | `#b4694f` | ![](docs/swatches/b4694f.png) |

Le texte principal est à 13,6:1 sur le fond des fenêtres ; le blanc sur l'accent est à 5,3:1.

## Composants

| Dossier | Application | Fichier à installer |
|---|---|---|
| [`desktop/`](desktop) | XFCE : GTK 2/3/4, libadwaita, xfwm4, panel, menu Whisker, Thunar | `desktop/Sphere-Dark/` |
| [`terminal/`](terminal) | xfce4-terminal | `sphere-dark.theme` |
| [`login/`](login) | Écran de connexion (slick-greeter / LightDM) | `install-login-assets.sh` |
| [`blender/`](blender) | Blender 5.2+ | extension (zip) |
| [`krita/`](krita) | Krita 5.2 / 5.3 | `Sphere Dark.colors` |
| [`unreal/`](unreal) | Unreal Engine 5 | `SphereDark.json` |
| [`ardour/`](ardour) | Ardour 9 | `sphere_dark-ardour.colors` |
| [`qt/`](qt) | Applications Qt : KeePassXC, Git Cola et la plupart des autres (qt5ct / qt6ct) | `sphere-dark.conf` |
| [`firefox/`](firefox) | Firefox | [Modules Firefox](https://addons.mozilla.org/firefox/addon/sphere-dark/) |
| [`youtube/`](youtube) | YouTube (Stylus) | `sphere-dark-youtube.user.css` |

`./build-all.sh` reconstruit tout dans `dist/` (voir [Construire](#construire)).

## Installation

### Bureau (Linux Mint XFCE)

```sh
mkdir -p ~/.themes
cp -r desktop/Sphere-Dark ~/.themes/
```

Choisis **Sphere-Dark** dans *Paramètres → Apparence* (style) et *Paramètres → Gestionnaire de fenêtres* (bordures). Dans les préférences du panel, mets l'arrière-plan sur *Aucun (utiliser le style du système)*.

### Icônes (Nordzy)

Le thème est pensé pour les icônes **Nordzy** d'alvatip, dont la palette Nord bleu-ardoise s'accorde à Sphere Dark. Elles ne sont pas incluses ici ; installe-les depuis [le dépôt de Nordzy](https://github.com/alvatip/Nordzy-icon) :

```sh
git clone https://github.com/alvatip/Nordzy-icon.git
cd Nordzy-icon
./install.sh -c dark
```

Cela installe **Nordzy-dark** dans `~/.local/share/icons`. Choisis-le dans *Paramètres → Apparence → Icônes*. Pour l'avoir aussi à l'écran de connexion, lance ensuite `sudo login/install-login-assets.sh` (voir [Écran de connexion](#écran-de-connexion)).

Autres packs qui vont bien : Papirus-Dark avec des dossiers bleu-gris (`papirus-folders -C bluegrey --theme Papirus-Dark`), Colloid (variante Nord), Kora (pgrey). Voir la [planche comparative](docs/screenshots/icon-packs.png).

### Terminal

```sh
cd terminal && ./install.sh
```

Puis *Préférences → Couleurs → Préréglages → Sphere Dark*. Le script ajoute aussi une marge intérieure aux terminaux VTE dans `~/.config/gtk-3.0/gtk.css`.

### Écran de connexion

L'écran de connexion tourne sous un autre utilisateur et ne voit que les dossiers système. Il faut donc y copier le thème et les icônes :

```sh
sudo login/install-login-assets.sh            # Sphere-Dark + icônes Nordzy*
sudo login/install-login-assets.sh 'Papirus*' # autre thème d'icônes
```

Ouvre ensuite *Fenêtre de connexion* et choisis le thème, les icônes et le fond. Relance le script après chaque modification du thème.

### Applications Qt (KeePassXC, Git Cola)

KeePassXC et Git Cola suivent la palette Qt du système. Installe qt5ct et qt6ct, puis lance le script (sans sudo) :

```sh
sudo apt install qt5ct qt6ct
qt/install-qt.sh
```

Il installe la palette pour Qt 5 et Qt 6, règle le style Fusion et ton thème d'icônes actuel, ajoute `QT_QPA_PLATFORMTHEME=qt5ct` à `~/.profile` (qt6ct répond aussi à `qt5ct`), et règle les couleurs du diff de Git Cola avec `git config --global cola.*`. Déconnecte-toi puis reconnecte-toi, puis choisis *Paramètres → Interface → Thème → Classique* dans KeePassXC. Garde Git Cola sur son thème *Default* : un thème `.qss` personnalisé fait passer Git Cola à une palette claire sur un système sombre.

![Aperçu des applications Qt](docs/screenshots/qt-apps.png)

### Blender 5.2+

Construis ou télécharge `sphere_dark-blender-1.0.0.zip`, puis *Edit → Preferences → Get Extensions → ⌄ → Install from Disk…*, et choisis **Sphere Dark** dans *Themes*. Le viewport 3D a un dégradé radial de studio ; passe *Background Type* à *Single Color* pour un fond uni.

### Krita

```sh
mkdir -p ~/.local/share/krita/color-schemes
cp "krita/Sphere Dark.colors" ~/.local/share/krita/color-schemes/
```

Pour la version Flatpak, utilise `~/.var/app/org.kde.krita/data/krita/color-schemes/`. Redémarre Krita et choisis *Configuration → Thèmes → Sphere Dark*. Mets la bordure du canevas à `#12141b` dans *Configurer Krita → Affichage*.

### Unreal Engine 5

Copie `unreal/SphereDark.json` dans `Engine/Content/Slate/Themes/` de ton installation (crée `Themes` au besoin), puis *Editor Preferences → General → Appearance → Active Theme*. Le fond des graphes se règle à part ; valeurs suggérées : fond `#12141b`, grille `#1c1e29` / `#2f313e`.

### Ardour 9

```sh
mkdir -p ~/.config/ardour9/themes
cp ardour/sphere_dark-ardour.colors ~/.config/ardour9/themes/
```

Puis *Preferences → Appearance → Colors → Color Theme → Sphere Dark*.

### Firefox

Sphere Dark est publié sur les modules Firefox : **[installe-le depuis addons.mozilla.org](https://addons.mozilla.org/firefox/addon/sphere-dark/)**. Il se met à jour automatiquement, comme tout autre thème.

Pour essayer des modifications de `firefox/manifest.json` avant de les publier, charge-le depuis `about:debugging` → *Ce Firefox* → *Charger un module complémentaire temporaire…* (retiré au redémarrage).

Astuce : coche *Barre de titre* dans *Personnaliser la barre d'outils* pour que Firefox utilise la barre de titre xfwm4 du thème.

### YouTube

Installe l'extension **Stylus**, crée un nouveau style, colle `youtube/sphere-dark-youtube.user.css`, et mets YouTube en apparence sombre. Pour les autres sites, Dark Reader avec un fond `#191b24`, un texte `#dfe5f5` et une sélection `#5a6a9a` s'en approche.

## Construire

Prérequis : Python 3 avec Pillow, `pysassc` (`pip install libsass`) ou `sassc`, `git`, `zip`.

```sh
./build-all.sh
```

Chaque `build.py` part du thème d'origine de son application (dans `*/source/`, ou Mint-Y récupéré sur GitHub pour le bureau) et le ramène à la palette. Pour retoucher une couleur, modifie la palette en haut du `build.py` concerné et relance.

## État

| Composant | Vérification |
|---|---|
| Bureau (GTK 3) | CSS compilé et rendu avec de vrais widgets GTK 3 ; utilisé au quotidien par l'auteur |
| Écran de connexion | Script testé sur une fausse racine ; widgets rendus avec GTK 3 |
| Blender | Chargé dans Blender 5.2.3 (bpy) avec le chargeur de préréglages de Blender ; extension validée |
| Firefox | Validé avec `web-ext lint` ; signé et publié sur addons.mozilla.org |
| Unreal Engine | Les clés correspondent aux 61 entrées `EStyleColor` (doc UE 5.8) |
| Ardour | Palette seulement ; les 429 alias et 41 modificateurs sont identiques à l'original |
| Applications Qt | Palette rendue avec Qt 6 en style Fusion ; script testé avec un faux dossier personnel |
| Krita, terminal, YouTube | Format vérifié ; aperçus dessinés à partir de la palette |

Les captures des vraies applications sont les bienvenues.

## Crédits

- Thème de bureau construit sur **Mint-Y** de Linux Mint ([linuxmint/mint-themes](https://github.com/linuxmint/mint-themes), GPL-3.0+).
- Thème Blender dérivé du thème par défaut de Blender ; thème Krita de *Krita darker* ; thème Ardour du thème *dark* d'Ardour.
- Noms de variables YouTube repérés dans le style utilisateur Catppuccin.
- Icônes recommandées : [Nordzy](https://github.com/alvatip/Nordzy-icon) d'alvatip (GPL-3.0), à installer à part.
- Fond d'écran de l'auteur ; seul un aperçu est inclus.

## Licence

[GPL-3.0-or-later](LICENSE), comme l'exigent les sources de Mint-Y sur lesquelles le thème de bureau est construit.
