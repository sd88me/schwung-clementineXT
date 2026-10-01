# Clementine-XT for Schwung

A wavetable synthesizer for Ableton Move, as a [Schwung](https://github.com/charlesvestal/schwung) sound-generator module. It plays the way the
Waldorf Microwave II and Microwave XT did: two wavetable oscillators with FM, sync and ring modulation, thirteen filter types, a 16-slot modulation
matrix with modifiers, an arpeggiator and a chain of effects, in ten voices at the original's 40 kHz internal rate. It loads the instrument's own
`.syx` sound banks.

**Status: first cut, not yet run on a Move.** The engine is the one from the MPC plugin
([sd88me/mpc-vst-clementineXT](https://github.com/sd88me/mpc-vst-clementineXT)), which runs on an Akai Force and is calibrated against the original
firmware. What exists here has passed a host simulation under ASan and cross-builds for aarch64; load time, CPU and the knob pages still need a
Move.

*Clementine-XT is an independent project. The XT in the name is a nod to the Microwave XT (and, like Surge XT, reads as "extended"). It is not
affiliated with or endorsed by Waldorf. See [Acknowledgements](#acknowledgements-and-legal).*

## Your ROM and sound banks
User files live in `/data/UserData/schwung/clementine-xt/ROMS/` (created on first load; override with the `CLEMENTINE_XT_DATA` environment variable). It
sits outside the module folder so module updates keep it.

- **Waves and wave tables:** copy your Microwave II ROM dump there, either the two 128 KB chip images or one 256 KB image (any `.bin` names). Without a ROM
  you get 12 built-in sounds on an original open set of wave tables. The module ships no ROM data of any kind.
- **Sound banks:** copy any Microwave II/XT `.syx` file (a single sound or a whole bank dump) there; each file is a bank on the Bank page.

You must own the instrument or have the right to use its ROM. The project does not provide it and will not help find it.

## Using it
The root page is the sound picker (sounds 0-255 of the current bank) with the four **Play** knobs, filter cutoff and resonance, volume and effect
parameter 1 on the eight knobs. From it: **Bank** (the `.syx` banks), **Play Assign** (which parameter each Play knob controls over its whole range),
then oscillators, waves, mixer, filters and envelopes, LFOs, glide, voices, effect, arpeggiator, the modulation matrix (amounts, sources and
destinations, eight slots a page) and the modifiers. Enum controls open a list; a two-option enum flips on click. The arpeggiator's Tempo 0 (extern)
follows the Move's tempo.

## Install
Build the module (below) and install `build/clementine-xt-module.tar.gz` with Schwung Manager (Custom Install from a file) or by unpacking it into
`/data/UserData/schwung/modules/sound_generators/`. Then copy your ROM and banks as above and add Clementine-XT to a track from the chain.

## Build and test
```
scripts/test.sh     # regenerates module.json, then the engine's unit tests and a host simulation of the module (x86, ASan)
scripts/build.sh    # aarch64 module tarball in build/ (needs Docker)
```
`scripts/sync_engine.sh` refreshes `engine/` from a checkout of the MPC plugin repo, where the engine is developed.

## How it works
Schwung runs every module entry point on the SPI audio callback, where file access, allocation and blocking are forbidden. The engine scans the ROMS
folder, reads the ROM and builds its tables when it starts, and reads a `.syx` file when a bank is loaded. So `create_instance` only starts a worker thread
(demoted to SCHED_OTHER on cores 0-2, as the API header requires); the worker creates the engine and publishes it, and until then the module renders
silence. A bank change is queued to the same worker, and `destroy_instance` only sets a flag for the worker to free everything. The controls (202 of them)
and the 37 pages are generated from `engine/params.json` by `tools/gen_schwung.py` into `module.json`.

| Path | |
|---|---|
| `engine/` | the synth engine (a copy of the MPC repo's `src/`, see `engine/UPSTREAM`), and `params.json`, the control list it was generated from |
| `src/schwung_plugin.c` | `plugin_api_v2` around the engine: loader thread, parameter and MIDI plumbing, the preset and bank pickers |
| `module.json` | generated: `chain_params` and `ui_hierarchy` |
| `vendor/` | Schwung's API header (MIT) and the engine interface; see `VENDORED.md` |
| `test/` | the engine's unit tests and `host_sim.c` |

## To do
- Run it on a Move: load time, CPU (the Force runs 8 voices at about 15 % of a core), the knob pages, the bank picker.
- Check the pages with Schwung's own validator (`tools/param-pages/validate.mjs`, needs Node) and preview tools.
- Add the catalog files (`release.json`, a catalog entry) the way other Schwung modules do, then a first release.
- Sound names show only for the selected sound; the engine's sound-state key is unused (Schwung keeps the control values).

## Acknowledgements and legal
Clementine-XT exists because of the Waldorf Microwave II and Microwave XT. Its sound engine is original C code, measured against the instrument's
behaviour, and it reads the instrument's waves from your own ROM at runtime. **No ROM, wave, sound bank, logo or panel art of the original is
included in this repository or its releases.** Waldorf and Microwave are trademarks of their owners. This project is independent and not affiliated
with or endorsed by Waldorf.

## Licence
GPL-3.0-only (see `LICENSE`). Vendored third-party code is listed in `VENDORED.md`.
