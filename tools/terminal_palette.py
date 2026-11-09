"""Calcule la palette ANSI du terminal (OKLCH) et ses contrastes. Usage : python3 terminal_palette.py [sortie.json]"""
import math
def oklch(L, C, h):
    a, b = C*math.cos(math.radians(h)), C*math.sin(math.radians(h))
    l_ = L + 0.3963377774*a + 0.2158037573*b
    m_ = L - 0.1055613458*a - 0.0638541728*b
    s_ = L - 0.0894841775*a - 1.2914855480*b
    l, m, s = l_**3, m_**3, s_**3
    r = 4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bb = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    f = lambda c: 12.92*c if c <= 0.0031308 else 1.055*c**(1/2.4) - 0.055
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(f(c)*255))) for c in (r, g, bb))
def lum(h):
    r,g,b=[int(h[i:i+2],16)/255 for i in (1,3,5)]
    f=lambda c: c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4
    return .2126*f(r)+.7152*f(g)+.0722*f(b)
def cr(a,b):
    x,y=sorted([lum(a),lum(b)]); return (y+.05)/(x+.05)
BG="#191b24"
hues={"rouge":28,"vert":150,"jaune":85,"bleu":262,"magenta":318,"cyan":200}
pal={"noir":"#2f313e"}
for n,h in hues.items(): pal[n]=oklch(0.72,0.085 if n!="jaune" else 0.09,h)
pal["blanc"]="#b8bfd3"
pal["noir+"]="#6f768c"
for n,h in hues.items(): pal[n+"+"]=oklch(0.82,0.075 if n!="jaune" else 0.085,h)
pal["blanc+"]="#eef1fa"
for k,v in pal.items(): print(f"{k:9s} {v}  {cr(v,BG):5.2f}:1")
import json, sys
if len(sys.argv) > 1: json.dump(pal, open(sys.argv[1], "w"), indent=2)
