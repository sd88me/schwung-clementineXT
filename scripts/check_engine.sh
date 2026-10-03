#!/usr/bin/env bash
# Fails when engine/ is not an exact mirror of the MPC plugin repo's src/ at the commit pinned in engine/UPSTREAM.
#   scripts/check_engine.sh [path to the MPC plugin checkout, default ../mpc-vst-clementine]
# 1. always: engine/ must match engine/SHA256SUMS (written by sync_engine.sh), i.e. nobody edited the copy by hand.
# 2. when the checkout (with the pinned commit) is there: engine/ must also match what that commit holds (the pin is honest).
# 3. only a warning: the checkout's src/ is ahead of the pin (run sync_engine.sh, test, commit).
set -euo pipefail
cd "$(dirname "$0")/.."
UP="${1:-../mpc-vst-clementine}"
(cd engine && sha256sum -c --quiet SHA256SUMS) || { echo "engine/ was edited or is out of step with its pin: fix the engine in the MPC repo and run scripts/sync_engine.sh" >&2; exit 1; }
(cd skin && sha256sum -c --quiet SHA256SUMS) || { echo "skin/ was edited or is out of step with its pin: change the skin in the MPC repo and run scripts/sync_engine.sh" >&2; exit 1; }
PIN="$(cat engine/UPSTREAM)"
if git -C "$UP" cat-file -e "$PIN^{commit}" 2>/dev/null; then
    for f in $(cd engine && ls | grep -v -e '^UPSTREAM$' -e '^SHA256SUMS$' -e '^params.json$'); do
        git -C "$UP" show "$PIN:src/$f" | cmp -s - "engine/$f" || { echo "engine/$f differs from $UP at ${PIN:0:8}" >&2; exit 1; }
    done
    for f in layout.conf skin.css; do git -C "$UP" show "$PIN:vst/$f" | cmp -s - "skin/$f" || { echo "skin/$f differs from $UP at ${PIN:0:8}" >&2; exit 1; }; done
    git -C "$UP" show "$PIN:vst/images/logo-plate.svg" | cmp -s - skin/logo-plate.svg || { echo "skin/logo-plate.svg differs from $UP at ${PIN:0:8}" >&2; exit 1; }
    git -C "$UP" show "$PIN:vst/params.json" | cmp -s - engine/params.json || { echo "engine/params.json differs from $UP at ${PIN:0:8}" >&2; exit 1; }
    if ! git -C "$UP" diff --quiet "$PIN" HEAD -- src vst/params.json vst/layout.conf vst/skin.css; then
        echo "warning: $UP has engine changes after the pin ${PIN:0:8}; run scripts/sync_engine.sh when you want them here" >&2
    fi
    echo "engine/ matches ${PIN:0:8}"
else
    echo "engine/ matches its checksums (pin ${PIN:0:8}; the MPC checkout is not available to compare)"
fi
