#!/usr/bin/env bash
# Cross-compile the Schwung module for Ableton Move (aarch64 Linux) and package it as build/clementine-xt-module.tar.gz.
# Needs Docker; nothing on a device is touched. Run scripts/test.sh first.
set -euo pipefail
cd "$(dirname "$0")/.."
IMAGE=clxt-schwung-build
if ! docker image inspect "$IMAGE" &>/dev/null; then
    docker build -q -t "$IMAGE" - <<'EOF'
FROM debian:bookworm
RUN apt-get update && apt-get install -y gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu file && rm -rf /var/lib/apt/lists/*
EOF
fi
python3 tools/gen_schwung.py
python3 tools/gen_web_ui.py
OUT=build/modules/sound_generators/clementine-xt
rm -rf build/modules build/clementine-xt-module.tar.gz
mkdir -p "$OUT"
cp module.json "$OUT/"
cp web/web_ui.html "$OUT/"; mkdir -p "$OUT/assets"; cp web/assets/* "$OUT/assets/"   # the browser panel (Remote UI)
SRC="engine/engine.c engine/out.c engine/patch.c engine/syx.c engine/waves.c engine/wavedata.c engine/filter.c engine/fx.c engine/mod.c engine/presets.c src/schwung_plugin.c"
CFLAGS="-O2 -g -shared -fPIC -Wall -Wno-format-truncation -Iengine -Ivendor/schwung -Ivendor/mpc-vst-plugins -Isrc"
docker run --rm -v "$PWD":/w -w /w "$IMAGE" bash -c "
    set -e
    aarch64-linux-gnu-gcc $CFLAGS $SRC -o $OUT/dsp.so -lm -lpthread
    aarch64-linux-gnu-strip --strip-unneeded $OUT/dsp.so
    file $OUT/dsp.so
    aarch64-linux-gnu-objdump -T $OUT/dsp.so | grep -o 'GLIBC_[0-9.]*' | sort -uV | tail -1
    tar --owner=0 --group=0 -czf build/clementine-xt-module.tar.gz -C build/modules/sound_generators clementine-xt
    tar -tzf build/clementine-xt-module.tar.gz
"
echo "Built: build/clementine-xt-module.tar.gz"
