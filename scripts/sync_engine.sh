#!/usr/bin/env bash
# Refresh engine/ from a checkout of the MPC plugin repo (sd88me/mpc-vst-clementineXT), where the engine is developed and calibrated.
#   scripts/sync_engine.sh [path to that checkout, default ../mpc-vst-clementine]
set -euo pipefail
cd "$(dirname "$0")/.."
UP="${1:-../mpc-vst-clementine}"
for f in engine.c filter.c filter.h fx.c fx.h mod.c mod.h out.c out.h patch.c patch.h patch_tab.h presets.c presets.h syx.c syx.h wavedata.c wavedata.h waves.c waves.h; do
    cp "$UP/src/$f" engine/
done
cp "$UP/vst/params.json" engine/params.json
echo "$(git -C "$UP" rev-parse HEAD)" > engine/UPSTREAM
python3 tools/gen_schwung.py
echo "engine/ now matches $(cat engine/UPSTREAM | cut -c1-8) of $UP; run scripts/test.sh, then commit"
