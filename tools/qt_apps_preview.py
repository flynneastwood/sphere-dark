"""Aperçu : palette Sphere Dark (qt6ct .conf) appliquée en style Fusion, avec des fenêtres
qui imitent la disposition de KeePassXC et de Git Cola. Usage : preview.py palette.conf sortie.png"""
import sys, configparser
from PySide6.QtWidgets import *
from PySide6.QtGui import QPalette, QColor, QFont, QTextCharFormat, QSyntaxHighlighter
from PySide6.QtCore import Qt
ROLES = [QPalette.WindowText, QPalette.Button, QPalette.Light, QPalette.Midlight, QPalette.Dark, QPalette.Mid,
         QPalette.Text, QPalette.BrightText, QPalette.ButtonText, QPalette.Base, QPalette.Window, QPalette.Shadow,
         QPalette.Highlight, QPalette.HighlightedText, QPalette.Link, QPalette.LinkVisited, QPalette.AlternateBase,
         QPalette.NoRole, QPalette.ToolTipBase, QPalette.ToolTipText, QPalette.PlaceholderText, QPalette.Accent]
cp = configparser.ConfigParser(); cp.read(sys.argv[1])
app = QApplication(sys.argv); app.setStyle("Fusion"); app.setFont(QFont("Inter", 10))
pal = QPalette()
for grp, key in ((QPalette.Active, "active_colors"), (QPalette.Inactive, "inactive_colors"), (QPalette.Disabled, "disabled_colors")):
    for role, c in zip(ROLES, cp["ColorScheme"][key].split(", ")):
        pal.setColor(grp, role, QColor("#" + c[3:]))
app.setPalette(pal)

root = QWidget(); root.setFixedSize(1300, 560); root.setAutoFillBackground(True)
p = root.palette(); p.setColor(QPalette.Window, QColor("#0f1017")); root.setPalette(p)
lay = QHBoxLayout(root); lay.setContentsMargins(12, 12, 12, 12); lay.setSpacing(12)

# --- KeePassXC
kp = QMainWindow(); kp.setPalette(pal); kp.setAutoFillBackground(True)
tb = QToolBar(); kp.addToolBar(tb)
for t in ["Base", "＋ Entrée", "✎", "🗑", "⧉ Copier"]: tb.addAction(t)
s = QLineEdit(); s.setPlaceholderText("Rechercher (Ctrl+F)…"); s.setFixedWidth(200); tb.addWidget(QWidget()); tb.addWidget(s)
split = QSplitter()
tree = QTreeWidget(); tree.setHeaderHidden(True)
rootg = QTreeWidgetItem(["Racine"]); tree.addTopLevelItem(rootg)
for g in ["Clients freelance", "Écoles", "Serveurs", "Personnel"]: rootg.addChild(QTreeWidgetItem([g]))
rootg.setExpanded(True); tree.setCurrentItem(rootg.child(0))
tab = QTableWidget(6, 3); tab.setHorizontalHeaderLabels(["Titre", "Nom d'utilisateur", "URL"]); tab.setAlternatingRowColors(True)
tab.verticalHeader().hide(); tab.horizontalHeader().setStretchLastSection(True); tab.setSelectionBehavior(QAbstractItemView.SelectRows)
for r, row in enumerate([("aflynn.xyz", "antoine", "https://aflynn.xyz"), ("GitHub", "aflynn", "https://github.com"),
                          ("Blender Extensions", "antoine", "extensions.blender.org"), ("Epic Games", "antoine", "epicgames.com"),
                          ("Hébergeur", "admin", "panel.example"), ("Banque", "••••", "—")]):
    for c, v in enumerate(row): tab.setItem(r, c, QTableWidgetItem(v))
tab.selectRow(1); tab.setColumnWidth(0, 150); tab.setColumnWidth(1, 130)
split.addWidget(tree); split.addWidget(tab); split.setSizes([170, 470])
cw = QWidget(); v = QVBoxLayout(cw); v.setContentsMargins(0, 0, 0, 0); v.addWidget(split)
prev = QGroupBox("Aperçu de l'entrée"); f = QFormLayout(prev)
f.addRow("Nom d'utilisateur", QLabel("aflynn")); pw = QLineEdit("motdepasse"); pw.setEchoMode(QLineEdit.Password); f.addRow("Mot de passe", pw)
f.addRow("URL", QLabel('<a href="#">https://github.com</a>')); v.addWidget(prev)
kp.setCentralWidget(cw); kp.statusBar().showMessage("Base déverrouillée · 42 entrées")
lay.addWidget(kp, 6)

# --- Git Cola
gc = QWidget(); gc.setPalette(pal); gc.setAutoFillBackground(True); g = QVBoxLayout(gc); g.setContentsMargins(0, 0, 0, 0)
top = QSplitter()
st = QTreeWidget(); st.setHeaderHidden(True)
staged = QTreeWidgetItem(["Indexé"]); mod = QTreeWidgetItem(["Modifié"])
for it, files in ((staged, ["desktop/build.py"]), (mod, ["README.md", "README.fr.md"])):
    st.addTopLevelItem(it); it.setExpanded(True)
    for fn in files: it.addChild(QTreeWidgetItem([fn]))
st.setCurrentItem(staged.child(0))
diff = QPlainTextEdit(); diff.setFont(QFont("DejaVu Sans Mono", 9)); diff.setLineWrapMode(QPlainTextEdit.NoWrap)
diff.setPlainText("diff --git a/desktop/build.py b/desktop/build.py\n@@ -412,6 +412,18 @@ scrolledwindow undershoot {\n   padding: 0;\n-  background-image: linear-gradient(dashes);\n+  background-image: linear-gradient(to bottom,\n+    rgba(6, 7, 12, 0.45), transparent);\n   background-repeat: no-repeat;\n }")
class Hl(QSyntaxHighlighter):
    def highlightBlock(self, t):
        fmt = QTextCharFormat()
        if t.startswith("+"): fmt.setBackground(QColor("#2c4535")); fmt.setForeground(QColor("#eef1fa"))
        elif t.startswith("-"): fmt.setBackground(QColor("#4d2f2b")); fmt.setForeground(QColor("#eef1fa"))
        elif t.startswith(("diff", "@@")): fmt.setForeground(QColor("#8b92a8"))
        else: return
        self.setFormat(0, len(t), fmt)
hl = Hl(diff.document())
top.addWidget(st); top.addWidget(diff); top.setSizes([170, 420]); g.addWidget(top, 3)
msg = QLineEdit(); msg.setPlaceholderText("Résumé du commit"); g.addWidget(msg)
body = QTextEdit(); body.setPlaceholderText("Description détaillée"); body.setFixedHeight(70); g.addWidget(body)
bl = QHBoxLayout(); bl.addWidget(QCheckBox("Amender")); bl.addStretch()
for t in ["Indexer", "Valider"]: bl.addWidget(QPushButton(t))
g.addLayout(bl); lay.addWidget(gc, 5)

root.show(); app.processEvents(); root.grab().save(sys.argv[2])
