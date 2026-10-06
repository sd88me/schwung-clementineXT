#!/usr/bin/env python3
"""Generate the Schwung (Ableton Move) module description from engine/params.json.

    gen_schwung.py            writes module.json, src/schwung_meta.h and build/contract.json

module.json is small on purpose (the loader caps it at 8 KB, and a sound generator's chain_params / ui_hierarchy are read from the plugin,
never from module.json). schwung_meta.h embeds the two JSON strings (`chain_params`: type, range, options of every control;
`ui_hierarchy`: the pages the Move's knob grid walks, eight controls per page) and the enum option tables, so the plugin can answer
`get_param("chain_params")`, `get_param("ui_hierarchy")` and turn an enum label into the index the engine takes. build/contract.json holds
the same two for scripts/test.sh and for Schwung's tools/param-pages. Limits: 256 params, 128 options of 31 characters per enum, 64 KB each.
Naming (docs/MODULES.md "Naming a parameter"): `name` is the full name shown in the held-knob header ("Osc 1 Octave"), `short_name` the cell
label (the page already says which oscillator), `short_options` the 3-4 character enum square.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
VERSION = "0.1.1"


def load():
    d = json.load(open(os.path.join(ROOT, "engine", "params.json")))
    return {p["key"]: p for p in d["params"]}


# (level key, page name, label prefix, [param keys]); eight controls per page at most, in knob order
def pages():
    P = []
    def add(key, name, pre, keys): P.append((key, name, pre, keys))
    add("osc1", "Oscillator 1", "O1", ["osc1_oct", "osc1_semi", "osc1_detune", "osc1_bend", "osc1_keytrack", "osc1_fm", "wavetable", "osc2_link"])
    add("osc2", "Oscillator 2", "O2", ["osc2_oct", "osc2_semi", "osc2_detune", "osc2_bend", "osc2_keytrack", "osc2_sync"])
    add("wave1", "Wave 1", "W1", ["w1_start", "w1_phase", "w1_env", "w1_velo", "w1_keytrack", "w1_limit"])
    add("wave2", "Wave 2", "W2", ["w2_start", "w2_phase", "w2_env", "w2_velo", "w2_keytrack", "w2_limit", "w2_link"])
    add("mixer", "Mixer", "Mix", ["mix_w1", "mix_w2", "mix_ring", "mix_noise", "mix_ext"])
    add("quality", "Quality", "Q", ["aliasing", "quantize", "clipping", "accuracy"])
    add("filter1", "Filter 1", "F1", ["f1_cutoff", "f1_reso", "f1_type", "f1_keytrack", "f1_env", "f1_velo", "f1_special"])
    add("filter2", "Filter 2", "F2", ["f2_cutoff", "f2_type", "f2_keytrack"])
    add("fenv", "Filter Envelope", "FE", ["fenv_a", "fenv_d", "fenv_s", "fenv_r", "fenv_trig"])
    add("amp", "Amplifier", "Amp", ["volume", "amp_velo", "amp_keytrack", "pan", "pan_keytrack", "chorus"])
    add("aenv", "Amp Envelope", "AE", ["aenv_a", "aenv_d", "aenv_s", "aenv_r", "aenv_trig"])
    add("wenv_t", "Wave Env Times", "WT", ["wenv_t%d" % i for i in range(1, 9)])
    add("wenv_l", "Wave Env Levels", "WL", ["wenv_l%d" % i for i in range(1, 9)])
    add("wenv_x", "Wave Env Loops", "WE", ["wenv_trig", "wenv_on_loop", "wenv_on_loop_start", "wenv_on_loop_end", "wenv_off_loop", "wenv_off_loop_start", "wenv_off_loop_end"])
    add("free", "Free Envelope", "FR", ["fre_t1", "fre_l1", "fre_t2", "fre_l2", "fre_t3", "fre_l3", "fre_rt", "fre_rl"])
    add("free_t", "Free Env Trigger", "FR", ["fre_trig"])
    add("lfo1", "LFO 1", "L1", ["lfo1_rate", "lfo1_shape", "lfo1_delay", "lfo1_sync", "lfo1_sym", "lfo1_human"])
    add("lfo2", "LFO 2", "L2", ["lfo2_rate", "lfo2_shape", "lfo2_delay", "lfo2_sync", "lfo2_sym", "lfo2_human", "lfo2_phase"])
    add("glide", "Glide", "Gl", ["glide_on", "glide_type", "glide_mode", "glide_time"])
    add("voices", "Voices", "Vc", ["alloc", "assign", "detune", "depan"])
    add("fx", "Effect", "FX", ["fx_type", "fx_p1", "fx_p2", "fx_p3"])
    add("arp", "Arpeggiator", "Arp", ["arp_on", "arp_tempo", "arp_clock", "arp_range", "arp_pattern", "arp_dir", "arp_order", "arp_velo"])
    add("arp_r", "Arp Reset", "Arp", ["arp_reset"])
    for half in range(2):
        lo = 8 * half + 1
        ids = list(range(lo, lo + 8))
        add("mod_amt%d" % (half + 1), "Mod Amount %d-%d" % (lo, lo + 7), "Amt", ["m%d_amt" % n for n in ids])
        add("mod_src%d" % (half + 1), "Mod Source %d-%d" % (lo, lo + 7), "Src", ["m%d_src" % n for n in ids])
        add("mod_dst%d" % (half + 1), "Mod Dest %d-%d" % (lo, lo + 7), "Dst", ["m%d_dst" % n for n in ids])
    for n in range(1, 5):
        add("modifier%d" % n, "Modifier %d" % n, "Mf%d" % n, ["mod%d_src1" % n, "mod%d_src2" % n, "mod%d_op" % n, "mod%d_par" % n])
    add("mdelay", "Control Delay", "CD", ["mdelay_src", "mdelay_time"])
    return P


# The Move's hardware pages are a playable subset; every control stays in chain_params so the web GUI (web_ui.html) has full control.
HW_PAGES = ["osc1", "osc2", "wave1", "wave2", "mixer", "filter1", "amp", "fenv", "aenv", "lfo1", "lfo2", "fx"]

PLAY_KNOBS = ["play_v1", "play_v2", "play_v3", "play_v4", "f1_cutoff", "f1_reso", "volume", "fx_p1"]
LABELS = {"play_v1": "Play 1", "play_v2": "Play 2", "play_v3": "Play 3", "play_v4": "Play 4", "play1": "Play 1 Param", "play2": "Play 2 Param",
          "play3": "Play 3 Param", "play4": "Play 4 Param"}


FULLPRE = {"O1": "Osc 1", "O2": "Osc 2", "W1": "Wave 1", "W2": "Wave 2", "Mix": "Mix", "Q": "Quality", "F1": "Filter 1", "F2": "Filter 2",
           "FE": "Filter Env", "Amp": "Amp", "AE": "Amp Env", "WT": "Wave Env", "WL": "Wave Env", "WE": "Wave Env", "FR": "Free Env",
           "L1": "LFO 1", "L2": "LFO 2", "Gl": "Glide", "Vc": "Voice", "FX": "Effect", "CD": "Ctl Delay", "Root": ""}
# enum squares are about 4 characters wide: the options worth shortening (the rest are cut by the renderer, and the long lists stay as they are)
SHORT_OPT = {"saturate": "Sat", "overflow": "Ovfl", "linear": "Lin", "normal": "Norm", "single": "Sngl", "retrigger": "Retr", "unison": "Uni",
             "random": "Rnd", "played": "Plyd", "root note": "Root", "last note": "Last", "24dB LP": "24LP", "12dB LP": "12LP", "24dB BP": "24BP",
             "12dB BP": "12BP", "12dB HP": "12HP", "Sin(x)>LP": "SinL", "WaveShapr": "Shpr", "Dual L/BP": "Dual", "FM-Filter": "FM", "S&H>L12dB": "S&H",
             "24dB Notch": "24N", "12dB Notch": "12N", "Band Stop": "Stop", "Ctl Filter": "CFlt", "Switch": "Sw"}


# cell labels the renderer would squeeze into non-words (checked with labelForCell, see README "Checking the pages")
SHORT = {"Wavetable": "Table", "Ringmod": "Ring", "External": "Ext", "Aliasing": "Alias", "Clipping": "Clip", "Accuracy": "Acc", "Special": "Spec",
         "Pan Keyt": "PKey", "Pattern": "Patt", "Direction": "Dir", "Note Order": "Order", "Param 1": "Prm 1", "Param 2": "Prm 2", "Param 3": "Prm 3",
         "Rel Time": "RelT", "Rel Level": "RelL", "Off Loop": "OffLp", "On Loop": "OnLp"}
LABELS.update({"play1": "Play 1 Param", "play2": "Play 2 Param", "play3": "Play 3 Param", "play4": "Play 4 Param"})
SHORT_KEY = {"play1": "Assign 1", "play2": "Assign 2", "play3": "Assign 3", "play4": "Assign 4"}


def label(key, p, pre):
    """(full name for the held-knob header, short_name for the cell)."""
    if key in SHORT_KEY: return LABELS[key], SHORT_KEY[key]
    if key in LABELS: return LABELS[key], LABELS[key]
    name = p["name"]
    if key.startswith("m") and key[1:2].isdigit() and "_" in key:   # matrix slot: "Amt 3" in the cell, "Mod 3 Amount" in the header
        n = key[1:key.index("_")]
        return "Mod %s %s" % (n, {"amt": "Amount", "src": "Source", "dst": "Dest"}[key.split("_")[1]]), "%s %s" % (pre, n)
    if key.startswith("mod") and key[3:4].isdigit(): return ("Modifier %s %s" % (key[3], name))[:31], SHORT.get(name, name)
    full = {"osc2_link": "Osc 2 Link", "wavetable": "Wavetable"}.get(key) or ("%s %s" % (FULLPRE.get(pre, pre), name)).strip()
    return full[:31], SHORT.get(name, name)


def param_meta(key, p, pre):
    full, short = label(key, p, pre)
    m = {"key": key, "name": full}
    if short != full: m["short_name"] = short
    if "options" in p:
        m["type"] = "enum"; m["options"] = [o[:31] for o in p["options"]]; m["default"] = p.get("default", 0)
        if len(p["options"]) <= 16 and any(o in SHORT_OPT for o in p["options"]):
            m["short_options"] = [SHORT_OPT.get(o, o[:4]) for o in p["options"]]
    else:
        m["type"] = "int"; m["min"] = p["min"]; m["max"] = p["max"]; m["default"] = p.get("default", 0)
    return m


def build():
    params = load()
    metas = []; seen = set(); levels = {}
    root_items = []
    for key, name, pre, keys in pages():
        items = []
        for k in keys:
            if k in seen: continue
            seen.add(k); metas.append(param_meta(k, params[k], pre)); items.append(k)
        if not items: continue
        metas_only = key not in HW_PAGES
        if metas_only: continue
        levels[key] = {"name": name, "params": [{"key": k, "name": next(m.get("short_name", m["name"]) for m in metas if m["key"] == k)} for k in items], "knobs": items[:8]}
        root_items.append({"level": key, "name": name})
    # the four Play knobs and the parameter each controls (the sound's own choice of four), on the first page
    play = []
    for i in range(1, 5):
        k = "play_v%d" % i; seen.add(k)
        metas.append({"key": k, "name": LABELS[k], "type": "int", "min": 0, "max": 127, "default": 0}); play.append(k)
        k2 = "play%d" % i
        metas.append(param_meta(k2, params[k2], "Play")); metas[-1]["name"] = LABELS[k2]
    # (controls on pages left off the hardware are still declared above, for the web GUI)
    # readouts for the web GUI: on no hardware page. They are declared so the host forwards their values to the browser panel.
    metas.append({"key": "preset", "name": "Sound", "type": "int", "min": 0, "max": 255, "default": 0})
    metas.append({"key": "preset_name", "name": "Sound Name", "type": "string", "default": ""})
    metas.append({"key": "bank", "name": "Bank", "type": "int", "min": 0, "max": 11, "default": 0})
    metas.append({"key": "bank_name", "name": "Bank Name", "type": "string", "default": ""})
    levels["play_assign"] = {"name": "Play Assign", "params": [{"key": "play%d" % i, "name": LABELS["play%d" % i]} for i in range(1, 5)],
                             "knobs": ["play%d" % i for i in range(1, 5)]}
    root_items.insert(0, {"level": "play_assign", "name": "Play Assign"})
    root_items.insert(0, {"level": "banks", "name": "Bank"})
    root_knobs = PLAY_KNOBS
    for k in root_knobs:
        if k not in {m["key"] for m in metas}:
            metas.append(param_meta(k, params[k], "Root"))
    levels["banks"] = {"name": "Bank", "items_param": "bank_list", "select_param": "bank"}
    root = {"name": "Clementine-XT", "list_param": "preset", "count_param": "preset_count", "name_param": "preset_name",
            "params": root_items, "knobs": root_knobs}
    levels = dict(root=root, **levels)
    hier = {"modes": None, "levels": levels}
    return metas, hier


def main():
    metas, hier = build()
    assert len(metas) <= 256, len(metas)
    for m in metas:
        if m["type"] == "enum": assert len(m["options"]) <= 128, m["key"]
    cp = json.dumps(metas, separators=(",", ":"))
    uh = json.dumps(hier, separators=(",", ":"))
    print("params %d, chain_params %d bytes, ui_hierarchy %d bytes" % (len(metas), len(cp), len(uh)), file=sys.stderr)
    assert len(cp) < 60000 and len(uh) < 60000, "JSON too large for Schwung's 64 KB buffers"
    module = {"id": "clementine-xt", "name": "Clementine-XT", "abbrev": "CLXT", "version": VERSION,
              "description": "Ten-voice wavetable synth: two wavetable oscillators, 13 filters, 16-slot mod matrix, arpeggiator and effects", "dsp": "dsp.so", "api_version": 2,
              "component_type": "sound_generator", "author": "sd88me",
              "capabilities": {"audio_out": True, "midi_in": True, "midi_out": False, "chainable": True, "component_type": "sound_generator"}}
    os.makedirs(os.path.join(ROOT, "src"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    json.dump(module, open(os.path.join(ROOT, "module.json"), "w"), indent=1)
    json.dump({"chain_params": metas, "ui_hierarchy": hier}, open(os.path.join(ROOT, "build", "contract.json"), "w"))
    # C header: the two JSON strings (split into chunks), and the enum tables for label -> index
    def cstr(s):
        out = []
        for i in range(0, len(s), 120):
            out.append('"%s"' % s[i:i + 120].replace("\\", "\\\\").replace('"', '\\"'))
        return "\n    ".join(out)
    h = ["/* Generated by tools/gen_schwung.py; do not edit. */", "#pragma once",
         "static const char SCHWUNG_CHAIN_PARAMS[] =\n    %s;" % cstr(cp),
         "static const char SCHWUNG_UI_HIERARCHY[] =\n    %s;" % cstr(uh),
         "typedef struct { const char *key; int nopt; const char *const *opt; } schwung_enum_t;"]
    enums = [m for m in metas if m["type"] == "enum"]
    for i, m in enumerate(enums):
        h.append("static const char *const SCHWUNG_OPT_%d[] = { %s };" % (i, ", ".join('"%s"' % o.replace('"', "'") for o in m["options"])))
    h.append("static const schwung_enum_t SCHWUNG_ENUMS[] = {")
    for i, m in enumerate(enums):
        h.append('    { "%s", %d, SCHWUNG_OPT_%d },' % (m["key"], len(m["options"]), i))
    h.append("};")
    h.append("#define SCHWUNG_NENUMS %d" % len(enums))
    open(os.path.join(ROOT, "src", "schwung_meta.h"), "w").write("\n".join(h) + "\n")


if __name__ == "__main__":
    main()
