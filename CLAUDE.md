# Clementine-XT for Schwung: agent guide

A Schwung (Ableton Move) sound-generator module around the Clementine-XT engine. Start with README.md. The engine is developed, calibrated and
documented in the MPC plugin repo (sd88me/mpc-vst-clementineXT: docs/DESIGN.md, docs/CALIBRATION.md); `engine/` here is a copy refreshed by
`scripts/sync_engine.sh`, so fix engine bugs there and sync, not here.

Ground rules:
- Never commit Waldorf ROM/OS files, extracted or dumped waves/tables, factory `.syx` banks, recordings of factory sounds, or Waldorf logos/panel
  artwork. Test fixtures derived from them stay on the developer's machine.
- Don't use "Waldorf" or "Microwave" in the product name, module id or name, or art. Factual wording in the README is fine.
- Vendored code goes in `vendor/` with an entry in `VENDORED.md`.
- Schwung's threading contract (vendor/schwung/plugin_api_v1.h): every entry point runs on the audio callback. No file I/O, allocation, blocking
  or logging there; slow work belongs to the worker thread in `src/schwung_plugin.c`.
- Run `scripts/test.sh` before building; `scripts/build.sh` cross-builds for aarch64.
