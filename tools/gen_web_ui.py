#!/usr/bin/env python3
"""Generate the Remote UI page (web_ui.html) of the Schwung module from the MPC plugin's skin.

    gen_web_ui.py            writes web/web_ui.html and web/assets/logo.svg

Design source: skin/layout.conf (the MPC plugin's page layout, pinned by scripts/sync_engine.sh) and skin/skin.css (its plate), so the browser
panel looks like the plugin's screen: the same ten tabs, the same section outlines with blue italic titles, the same knobs (the four Play knobs
red), red LCD steppers, green dot-matrix readouts and the logo. Controls and their ranges come from build/contract.json (tools/gen_schwung.py),
so the panel has full control of all 202 parameters, while the Move's own pages are a playable subset.

schwung-manager loads the page in an iframe on its Remote UI page (docs/MODULES.md "Remote UI Custom HTML"). The page talks to the module
through /static/schwung-remote-api.js (schwungRemote.setParam / onParamChange); without it (opened as a file) it runs against a local stub so
the layout can be previewed and screenshotted offline (scripts/preview_web_ui.sh).
"""
import json
import os
import re
import shlex
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SKIN = os.path.join(ROOT, "skin")
OUT = os.path.join(ROOT, "web")
Y_OFFSET = 86          # the MPC layout's first panel starts at y=92 under its header; the browser page has no header
STAGE_W, STAGE_H = 1280, 628 - 6
KEYMAP = {"program": "preset", "patch_name": "preset_name"}   # MPC key -> Schwung key


def parse_layout(path):
    theme, tabs, cur = {}, [], None
    for raw in open(path):
        line = raw.strip()
        if not line or line.startswith("#"): continue
        m = re.match(r"\[tab (.+)\]$", line)
        if m:
            cur = {"name": m.group(1), "w": []}; tabs.append(cur); continue
        if line.startswith("theme_"):
            k, v = line.split("=", 1); theme[k[6:]] = v; continue
        if cur is None or line.startswith(("qlinks", "art_css")): continue
        parts = shlex.split(line)
        kind, kv = parts[0], dict(p.split("=", 1) for p in parts[1:] if "=" in p)
        w = {"k": kind}
        for k, v in kv.items():
            w[k] = int(v) if re.fullmatch(r"-?\d+", v) else v
        cur["w"].append(w)
    return theme, tabs


def plate_css(css, bg):
    """The plate: the background of the page-sized element in skin.css (diagonal sheen, arcs, rim, grain)."""
    i = css.index("#c:has(")
    j = css.index("\n}", i)
    block = css[css.index("{", i) + 1:j]
    block = block.replace("var(--bg)", "#" + bg)
    return block


def main():
    theme, tabs = parse_layout(os.path.join(SKIN, "layout.conf"))
    contract = json.load(open(os.path.join(ROOT, "build", "contract.json")))
    P = {}
    for m in contract["chain_params"]:
        P[m["key"]] = [m["type"], m.get("min", 0), m.get("max", 0), m.get("default", 0), m.get("options")]
    # keys the panel reads but that are not knobs on the Move (the sound and bank readouts)
    for k, hi in (("preset", 255), ("bank", 11)):
        P[k] = P.get(k) or ["int", 0, hi, 0, None]
    css = open(os.path.join(SKIN, "skin.css")).read()
    plate = plate_css(css, theme["bg"])
    layout = []
    for t in tabs:
        ws = []
        for w in t["w"]:
            if t["name"] == "SOUNDS": continue
            w = dict(w)
            if "cy" in w: w["cy"] -= Y_OFFSET
            if "y" in w: w["y"] -= Y_OFFSET
            if "key" in w: w["key"] = KEYMAP.get(w["key"], w["key"])
            if w["k"] in ("knob", "popup", "toggle") and w.get("key") not in P:
                raise SystemExit("layout control %r is not a declared parameter" % w.get("key"))
            ws.append(w)
        layout.append({"name": t["name"], "w": ws})
    os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
    shutil.copy(os.path.join(SKIN, "logo-plate.svg"), os.path.join(OUT, "assets", "logo.svg"))
    tpl = open(os.path.join(HERE, "web_ui.template.html")).read()
    html = (tpl.replace("/*PLATE*/", plate).replace("/*THEME*/{}", json.dumps(theme)).replace("/*PARAMS*/{}", json.dumps(P, separators=(",", ":")))
            .replace("/*LAYOUT*/[]", json.dumps(layout, separators=(",", ":"))).replace("/*W*/1280", str(STAGE_W)).replace("/*H*/616", str(STAGE_H)))
    for k, v in theme.items():
        html = html.replace("var(--t-%s)" % k, "#" + v)
    open(os.path.join(OUT, "web_ui.html"), "w").write(html)
    n = sum(len(t["w"]) for t in layout)
    print("web/web_ui.html: %d tabs, %d controls, %d bytes" % (len(layout), n, len(html)))


if __name__ == "__main__":
    main()
