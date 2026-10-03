#!/usr/bin/env bash
# Screenshot every tab of web/web_ui.html against its local stub (no Move needed). Uses the mpc-vst-html-art Docker image (Playwright + Chromium)
# from the mpc-vst-plugins checkout's tools/build_port.sh. Output: build/web_preview/tab_N.png
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tools/gen_schwung.py >/dev/null && python3 tools/gen_web_ui.py
mkdir -p build/web_preview
docker run --rm -i -v "$PWD":/w -w /w mpc-vst-html-art python3 - <<'PY'
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1280, "height": 700})
    for i in range(5):
        pg.goto("file:///w/web/web_ui.html?tab=%d" % i); pg.wait_for_timeout(300)
        pg.screenshot(path="/w/build/web_preview/tab_%d.png" % i, full_page=True)
    b.close()
PY
ls build/web_preview
