import sys
from PIL import Image
import colorsys

img = Image.open(sys.argv[1]).convert("RGB")
print("size", img.size)
small = img.resize((200, 112))
q = small.quantize(colors=10, method=Image.Quantize.MEDIANCUT)
pal = q.getpalette()[:30]
counts = sorted(q.getcolors(), reverse=True)
for n, idx in counts:
    r, g, b = pal[idx*3:idx*3+3]
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    print(f"#{r:02x}{g:02x}{b:02x}  {n/ (200*112)*100:5.1f}%  H={h*360:5.1f} S={s:.2f} L={l:.2f}")

# points d'échantillonnage utiles
W, H = img.size
pts = {
 "fond haut-gauche": (int(W*0.05), int(H*0.1)),
 "fond centre-haut (brume)": (int(W*0.5), int(H*0.1)),
 "sol bas": (int(W*0.5), int(H*0.95)),
 "sol milieu": (int(W*0.5), int(H*0.75)),
 "sphère clair": (int(W*0.55), int(H*0.4)),
 "sphère intérieur": (int(W*0.5), int(H*0.55)),
}
for k, p in pts.items():
    r, g, b = img.getpixel(p)
    print(f"{k:28s} #{r:02x}{g:02x}{b:02x}")
