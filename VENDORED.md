# Vendored code

Third-party code committed into this repo (never fetched at build time). For each entry: upstream, exact commit, licence, local changes.

| Component | Upstream | Commit | Licence | Local changes |
|---|---|---|---|---|
| `vendor/schwung/plugin_api_v1.h` | https://github.com/charlesvestal/schwung `src/host/plugin_api_v1.h` | cfeb2b0a (v1.6.3) | MIT | none |
| `vendor/mpc-vst-plugins/engine.h` | https://github.com/sd88me/mpc-vst-plugins `wrapper/engine.h` | 0c2081e | GPL-3.0 (same author) | none |
| `engine/` (not third party: the synth engine copied from the MPC plugin repo) | https://github.com/sd88me/mpc-vst-clementineXT `src/`, `vst/params.json` | see `engine/UPSTREAM` | GPL-3.0 (same author) | none; refreshed by `scripts/sync_engine.sh` |
