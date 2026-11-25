"""Fenêtre qui imite OBS (docks Scènes, Sources, Mixeur, Contrôles, aperçu), stylée avec une
feuille composée par obs_compose.py. Usage : obs_preview.py feuille.qss fond.jpg sortie.png titre"""
import sys
from PySide6.QtWidgets import *
from PySide6.QtGui import QPixmap, QFont, QPainter, QColor
from PySide6.QtCore import Qt
qss_path, wall, out, title = sys.argv[1:5]
app = QApplication(sys.argv); app.setStyle("Fusion"); app.setFont(QFont("Inter", 10))
app.setStyleSheet(open(qss_path).read())

win = QMainWindow(); win.setObjectName("OBSBasic"); win.resize(1120, 640); win.setWindowTitle(title)
mb = win.menuBar()
for m in ["Fichier", "Édition", "Affichage", "Docks", "Profil", "Collection de scènes", "Outils", "Aide"]: mb.addMenu(m)

class Preview(QWidget):
    def paintEvent(self, e):
        p = QPainter(self); bg = self.palette().color(self.backgroundRole())
        p.fillRect(self.rect(), QColor(PREVIEW_BG))
        r = self.rect().adjusted(40, 20, -40, -20)
        w = min(r.width(), int(r.height() * 16 / 9)); h = int(w * 9 / 16)
        x = r.x() + (r.width() - w) // 2; y = r.y() + (r.height() - h) // 2
        p.drawPixmap(x, y, w, h, QPixmap(wall))
PREVIEW_BG = "#12141b" if "Sphere" in title else "#13141a"
prev = Preview(); prev.setMinimumHeight(330); win.setCentralWidget(prev)

def dock(name, w, area=Qt.BottomDockWidgetArea):
    d = QDockWidget(name); d.setWidget(w); d.setFeatures(QDockWidget.DockWidgetMovable); win.addDockWidget(area, d); return d

sc = QListWidget(); [sc.addItem(s) for s in ["Intro", "Tuto Blueprint — écran", "Caméra + écran", "Pause"]]; sc.setCurrentRow(1)
src = QListWidget(); [src.addItem(s) for s in ["🎙  Micro", "🖥  Capture d'écran", "📷  Webcam", "🖼  Logo aflynn.xyz"]]; src.setCurrentRow(1)
mix = QWidget(); ml = QVBoxLayout(mix)
for n, v in (("Audio du bureau", 45), ("Micro/Aux", 72)):
    row = QHBoxLayout(); lab = QLabel(n); lab.setMinimumWidth(110); row.addWidget(lab)
    pb = QProgressBar(); pb.setValue(v); pb.setTextVisible(False); pb.setFixedHeight(8); row.addWidget(pb)
    ml.addLayout(row); s = QSlider(Qt.Horizontal); s.setValue(80); ml.addWidget(s)
ml.addStretch()
ctl = QWidget(); cl = QVBoxLayout(ctl)
for name, label, chk in (("streamButton", "Démarrer le streaming", False), ("recordButton", "Arrêter l'enregistrement", True),
                         ("virtualCamButton", "Caméra virtuelle", False), ("modeSwitch", "Mode studio", False), ("settingsButton", "Paramètres", False)):
    b = QPushButton(label); b.setObjectName(name); b.setCheckable(True); b.setChecked(chk)
    if chk: b.setProperty("class", "state-active")
    cl.addWidget(b)
cl.addStretch()
for n, w in (("Scènes", sc), ("Sources", src), ("Mixeur audio", mix), ("Contrôles", ctl)):
    dock(n, w)
win.statusBar().showMessage("REC 00:12:48    CPU : 3,1 %    60,00 / 60,00 FPS")
win.show(); app.processEvents(); win.grab().save(out)
