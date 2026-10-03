#!/usr/bin/env bash
# Host simulation of the Schwung module plus the engine's own unit tests, on x86 under ASan/UBSan. No Move needed.
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/check_engine.sh
python3 tools/gen_schwung.py
python3 - <<'PY'
import json, os
d = json.load(open("build/contract.json"))
assert os.path.getsize("module.json") < 8192, "module.json over the loader's 8 KB cap"
cp = d["chain_params"]; keys = [m["key"] for m in cp]
assert len(keys) == len(set(keys)) <= 256, "duplicate or too many params"
levels = d["ui_hierarchy"]["levels"]
for name, lv in levels.items():
    for p in lv.get("params", []):
        if "key" in p: assert p["key"] in keys, (name, p["key"])
    assert len(lv.get("knobs", [])) <= 8, name
txt = json.dumps(d)
assert all(ord(c) < 128 for c in txt), "non-ASCII text (the device's 5x7 font cannot draw it)"
for m in cp:
    if m["type"] == "enum": assert m["options"] and all(len(o) <= 31 for o in m["options"]), m["key"]
    assert len(m["name"]) <= 31 and len(m.get("short_name", "")) <= 15, m["key"]
    if "short_options" in m: assert len(m["short_options"]) == len(m["options"]), m["key"]
assert levels["root"]["list_param"] == "preset" and levels["banks"]["select_param"] == "bank"
print("module.json: %d params, %d levels" % (len(keys), len(levels)))
PY
mkdir -p build /tmp/clxt_sim_data
ENG="engine/engine.c engine/out.c engine/patch.c engine/syx.c engine/waves.c engine/wavedata.c engine/filter.c engine/fx.c engine/mod.c engine/presets.c"
INC="-Iengine -Ivendor/schwung -Ivendor/mpc-vst-plugins -Isrc"
FLAGS="-O1 -g -Wall -Wno-format-truncation -fsanitize=address,undefined"
for t in test_arp test_presets test_play test_patch test_waves test_out; do
    gcc $FLAGS $INC $ENG test/$t.c -o build/$t -lm -lpthread
    echo "== $t"; ASAN_OPTIONS=detect_leaks=0 ./build/$t | tail -1
done
gcc $FLAGS $INC $ENG src/schwung_plugin.c test/host_sim.c -o build/host_sim -lm -lpthread
echo "== host_sim"; ASAN_OPTIONS=detect_leaks=0 ./build/host_sim
