"""Compose la feuille de style finale d'une variante OBS : variables de la base + celles de la
variante, puis résolution de var() et calc()/min()/max(), comme le fait OBS. Usage :
obs_compose.py Yami.obt variante.ovt sortie.qss"""
import re, sys
base, variant, out = sys.argv[1:4]

def split(text):
    blk = re.search(r"@OBSThemeVars\s*\{(.*?)\n\}", text, re.S)
    vars_ = dict(re.findall(r"^\s*(--[\w]+)\s*:\s*(.+?);\s*(?:/\*.*\*/)?\s*$", blk.group(1), re.M)) if blk else {}
    rest = re.sub(r"@OBSThemeMeta\s*\{.*?\}", "", text, flags=re.S)
    rest = re.sub(r"@OBSThemeVars\s*\{.*?\n\}", "", rest, flags=re.S)
    return vars_, rest

bv, bqss = split(open(base).read())
vv, vqss = split(open(variant).read())
V = {**bv, **vv, "--obsFontScale": "10", "--obsPadding": "2"}

def resolve(s, depth=0):
    for _ in range(30):
        n = re.sub(r"var\((--[\w]+)\)", lambda m: V.get(m.group(1), m.group(0)), s)
        if n == s: break
        s = n
    return s

UNIT = r"(-?\d*\.?\d+)(px|pt|%)?"
def evaluate(expr):
    units = re.findall(r"\d(px|pt)", expr)
    py = re.sub(r"(\d*\.?\d+)(px|pt)", r"\1", expr)
    py = py.replace("calc(", "(")
    val = eval(py, {"__builtins__": {}}, {"min": min, "max": max})
    v = round(val, 2)
    v = int(v) if float(v).is_integer() else v
    return f"{v}{units[0] if units else ''}"

FN = re.compile(r"(calc|min|max)\(([^()]*)\)")
FAILED = []
def compute(s):
    def one(m):
        txt = f"{m.group(1)}({m.group(2)})" if m.group(1) != "calc" else f"({m.group(2)})"
        try:
            return evaluate(txt)
        except Exception:
            FAILED.append(m.group(0)); return "\x00" + m.group(0)[:-1] + "\x01"
    for _ in range(40):
        n = FN.sub(one, s)
        if n == s: break
        s = n
    return s.replace("\x00", "").replace("\x01", ")")

qss = resolve(bqss + "\n" + vqss)
qss = compute(qss)
open(out, "w").write(qss)
left = re.findall(r"var\(--[\w]+\)", qss)
print("échecs:", sorted(set(FAILED))[:5]); print("feuille composée :", len(qss.splitlines()), "lignes | var() non résolues :", sorted(set(left))[:8], "| calc restants :", qss.count("calc("))
