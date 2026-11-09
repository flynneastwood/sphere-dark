import sys, configparser
from PySide6.QtWidgets import *
from PySide6.QtGui import QPalette, QColor, QPainter, QLinearGradient, QFont
from PySide6.QtCore import Qt
cp = configparser.ConfigParser(interpolation=None); cp.optionxform = str; cp.read(sys.argv[1])
def c(sec, key): return QColor(*map(int, cp[f"Colors:{sec}"][key].split(",")))
app = QApplication(sys.argv); app.setStyle("Fusion")
p = QPalette()
for grp in (QPalette.Active, QPalette.Inactive, QPalette.Disabled):
    for role, (sec, key) in {QPalette.Window: ("Window","BackgroundNormal"), QPalette.WindowText: ("Window","ForegroundNormal"),
        QPalette.Base: ("View","BackgroundNormal"), QPalette.AlternateBase: ("View","BackgroundAlternate"), QPalette.Text: ("View","ForegroundNormal"),
        QPalette.Button: ("Button","BackgroundNormal"), QPalette.ButtonText: ("Button","ForegroundNormal"),
        QPalette.Highlight: ("Selection","BackgroundNormal"), QPalette.HighlightedText: ("Selection","ForegroundNormal"),
        QPalette.ToolTipBase: ("Tooltip","BackgroundNormal"), QPalette.ToolTipText: ("Tooltip","ForegroundNormal"),
        QPalette.Link: ("View","ForegroundLink"), QPalette.LinkVisited: ("View","ForegroundVisited"),
        QPalette.PlaceholderText: ("View","ForegroundInactive")}.items():
        p.setColor(grp, role, c(sec, key))
    b = c("Button","BackgroundNormal")
    p.setColor(grp, QPalette.Light, b.lighter(130)); p.setColor(grp, QPalette.Midlight, b.lighter(115))
    p.setColor(grp, QPalette.Mid, b.darker(130)); p.setColor(grp, QPalette.Dark, b.darker(160)); p.setColor(grp, QPalette.Shadow, QColor(0,0,0))
for role in (QPalette.WindowText, QPalette.Text, QPalette.ButtonText):
    p.setColor(QPalette.Disabled, role, c("View","ForegroundInactive"))
app.setPalette(p); app.setFont(QFont("Inter", 10))

class Canvas(QWidget):
    def paintEvent(self, e):
        q = QPainter(self); q.fillRect(self.rect(), QColor("#12141b"))
        r = self.rect().adjusted(90, 50, -90, -50); g = QLinearGradient(r.topLeft(), r.bottomLeft())
        g.setColorAt(0, QColor("#0b0c12")); g.setColorAt(1, QColor("#3a3e4f")); q.fillRect(r, g)
        q.setBrush(QColor("#d8dde9")); q.setPen(Qt.NoPen); q.drawEllipse(r.center(), 70, 70)

win = QMainWindow(); win.resize(1200, 720); win.setWindowTitle("Krita")
mb = win.menuBar()
for m in ["Fichier","Édition","Affichage","Image","Calque","Sélection","Filtre","Outils","Configuration","Fenêtre","Aide"]: mb.addMenu(m)
tb = win.addToolBar("t")
for t in ["Nouveau","Ouvrir","Enregistrer"]: tb.addAction(t)
tb.addSeparator(); cb = QComboBox(); cb.addItems(["Normal","Produit","Écran"]); tb.addWidget(QLabel("  Mode ")); tb.addWidget(cb)
tb.addWidget(QLabel("  Opacité ")); s = QSlider(Qt.Horizontal); s.setValue(80); s.setFixedWidth(140); tb.addWidget(s)
tb.addWidget(QLabel("  Taille ")); sp = QDoubleSpinBox(); sp.setValue(24); tb.addWidget(sp)

center = QWidget(); hl = QHBoxLayout(center); hl.setContentsMargins(0,0,0,0)
tools = QWidget(); tl = QGridLayout(tools)
for i, n in enumerate(["✎","▭","◯","⬚","✥","⤢","T","◐","⌖","✂"]):
    bt = QToolButton(); bt.setText(n); bt.setCheckable(True); bt.setChecked(i == 0); bt.setFixedSize(32,32); tl.addWidget(bt, i//2, i%2)
tl.setRowStretch(6, 1); hl.addWidget(tools)
tabs = QTabWidget(); tabs.addTab(Canvas(), "sphere_concept.kra"); tabs.addTab(QWidget(), "croquis_02.kra"); hl.addWidget(tabs, 1)
win.setCentralWidget(center)

dock = QDockWidget("Calques"); dw = QWidget(); dl = QVBoxLayout(dw)
row = QHBoxLayout(); c2 = QComboBox(); c2.addItems(["Normal"]); row.addWidget(c2); o = QSpinBox(); o.setSuffix(" %"); o.setMaximum(100); o.setValue(100); row.addWidget(o); dl.addLayout(row)
lw = QListWidget(); lw.setAlternatingRowColors(True)
for n in ["Lumière d'ambiance","Sphère — détails","Sphère — base","Sol","Fond"]: lw.addItem(QListWidgetItem("👁  " + n))
lw.setCurrentRow(1); dl.addWidget(lw)
br = QHBoxLayout()
for t in ["+","Dupliquer","Supprimer"]: br.addWidget(QPushButton(t))
dl.addLayout(br); dock.setWidget(dw); win.addDockWidget(Qt.RightDockWidgetArea, dock)

dock2 = QDockWidget("Réglages de l'outil"); w2 = QWidget(); f = QFormLayout(w2)
f.addRow("Lissage", QComboBox()); ch = QCheckBox("Stabilisateur"); ch.setChecked(True); f.addRow("", ch); f.addRow("", QCheckBox("Aligner sur la grille"))
pb = QProgressBar(); pb.setValue(62); f.addRow("Rendu", pb); le = QLineEdit(); le.setPlaceholderText("Rechercher une brosse…"); f.addRow("Brosse", le)
lab = QLabel('<a href="#">Documentation</a> · <span style="color:#d59087">Avertissement</span> · <span style="color:#7eb488">Enregistré</span>'); f.addRow("", lab)
dis = QPushButton("Bouton désactivé"); dis.setEnabled(False); f.addRow("", dis)
dock2.setWidget(w2); win.addDockWidget(Qt.RightDockWidgetArea, dock2)
win.statusBar().showMessage("RVB/Alpha (8 bits) · sRGB · 3000 × 2000 px · 72 %")
win.show(); app.processEvents(); win.grab().save(sys.argv[2])
