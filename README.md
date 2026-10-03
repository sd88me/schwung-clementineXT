# Clementine-XT for Schwung

A wavetable synthesizer for Ableton Move, as a [Schwung](https://github.com/charlesvestal/schwung) sound-generator module. It plays the way the
Waldorf Microwave II and Microwave XT did: two wavetable oscillators with FM, sync and ring modulation, thirteen filter types, a 16-slot modulation
matrix with modifiers, an arpeggiator and a chain of effects, in ten voices at the original's 40 kHz internal rate. It loads the instrument's own
`.syx` sound banks.

**Status: not yet run on a Move.** The engine is the one from the MPC plugin
([sd88me/mpc-vst-clementineXT](https://github.com/sd88me/mpc-vst-clementineXT)), which runs on an Akai Force and is calibrated against the original
firmware. What exists here has passed a host simulation under ASan, cross-builds for aarch64 and is built against Schwung 1.6.3's header; load time, CPU and the knob pages still need a
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
scripts/test.sh     # engine pin check, regenerates module.json, then the engine's unit tests and a host simulation of the module (x86, ASan)
scripts/build.sh    # aarch64 module tarball in build/ (needs Docker)
scripts/deploy.sh <move host> [--reboot]   # staged install on a Move (see docs/MOVE_TEST.md for the first-run checklist)
```
**The engine is developed in the MPC plugin repo, not here.** `scripts/sync_engine.sh` copies its `src/` into `engine/` and records the commit
(`engine/UPSTREAM`) and the files' checksums (`engine/SHA256SUMS`); `scripts/check_engine.sh` (run by `test.sh`) fails if `engine/` was edited by hand
or no longer matches the pinned commit, and warns when the MPC repo has engine changes newer than the pin.

## How it works
Schwung runs every module entry point on the SPI audio callback, where file access, allocation and blocking are forbidden. The engine scans the ROMS
folder, reads the ROM and builds its tables when it starts, and reads a `.syx` file when a bank is loaded. So `create_instance` only starts a worker thread
(demoted to SCHED_OTHER on cores 0-2, as the API header requires); the worker creates the engine and publishes it, and until then the module renders
silence. A bank change is queued to the same worker, and `destroy_instance` only sets a flag for the worker to free everything. The controls (202 of them)
and the pages are generated from `engine/params.json` by `tools/gen_schwung.py`. A sound generator's `chain_params` and `ui_hierarchy` are read from
the plugin (`get_param`), not from `module.json`, so `module.json` stays a few hundred bytes (the loader caps it at 8 KB) and the two JSON documents
are compiled into the plugin (`src/schwung_meta.h`).

| Path | |
|---|---|
| `engine/` | the synth engine (a copy of the MPC repo's `src/`, see `engine/UPSTREAM`), and `params.json`, the control list it was generated from |
| `src/schwung_plugin.c` | `plugin_api_v2` around the engine: loader thread, parameter and MIDI plumbing, the preset and bank pickers |
| `module.json` | generated: id, version, capabilities (the pages and controls are served by the plugin) |
| `vendor/` | Schwung's API header (MIT) and the engine interface; see `VENDORED.md` |
| `test/` | the engine's unit tests and `host_sim.c` |

## Pages
The knob grid has eight knobs per page; the root page is the sound list (sounds 0-255 of the current bank). The Move's hardware pages are a
playable subset (`HW_PAGES` in `tools/gen_schwung.py`); all 202 controls stay declared in `chain_params`, and the web GUI has full control of them.

| Page | Knobs |
|---|---|
| **Root** (sound list) | Play 1-4, Cutoff, Reso, Volume, Prm 1 (effect parameter 1) |
| Bank, Play Assign | the `.syx` bank picker; which parameter each Play knob drives |
| Oscillator 1 / 2 | Octave, Semi, Detune, Bend, Keytrack, FM Amt, Table, Link / Octave, Semi, Detune, Bend, Keytrack, Sync |
| Wave 1 / 2, Mixer | Start, Phase, Env Amt, Env Velo, Keytrack, Limit (+ Link) / Wave 1, Wave 2, Ring, Noise, Ext |
| Filter 1, Filter Envelope | Cutoff, Reso, Type, Keytrack, Env Amt, Env Velo, Spec / A, D, S, R, Trigger |
| Amplifier, Amp Envelope | Volume, Velo, Keytrack, Panning, PKey, Chorus / A, D, S, R, Trigger |
| LFO 1, LFO 2 | Rate, Shape, Delay, Sync, Symm, Human (+ Phase on LFO 2) |
| Effect | Type, Prm 1-3 |

Web GUI only: Filter 2, quality, the wave and free envelopes, glide and voices, the arpeggiator, the 16-slot modulation matrix, the modifiers and
the control delay.

Naming follows Schwung's rules (`docs/MODULES.md` upstream): `name` is the full name ("Osc 1 Octave", shown while a knob is held), `short_name`
the cell label, `short_options` the enum square. Checked with Schwung's contract validator (info findings only: filter graphics are inferred).

## Web GUI
`web_ui.html` (Schwung's Remote UI custom panel, `http://<move>:7700/remote-ui`) is the full-control surface: the MPC plugin's pages stacked vertically into five tabs (SOUND = Global + Sounds, OSC + WAVE, FILTER + ENV, LFO ARP + MODIFIERS, MOD MATRIX; the page scrolls)
with its skin (same layout, blue section titles, red Play knobs, red LCD steppers, logo), every one of the 202 controls, plus a bank picker and a
1-256 sound grid under the global page (the module does not publish sound names, so the grid is numbered). It is generated by `tools/gen_web_ui.py` from `skin/` (the MPC
plugin's layout and stylesheet, pinned with the engine) and `build/contract.json`; `scripts/preview_web_ui.sh` screenshots every tab offline
(Docker, against a local stub of `schwungRemote`). Drag a knob (Shift: fine), mouse wheel steps, double-click resets.
Not yet checked on a Move: that the host forwards the readout values (`preset_name`, `bank_name`, `bank`, `preset`, declared in `chain_params` for
that reason) to the panel.

## To do
- Run it on a Move (checklist: [docs/MOVE_TEST.md](docs/MOVE_TEST.md)): load time, CPU (the Force runs 8 voices at about 15 % of a core), the knob pages,
  the bank picker, saving a set.
- A first release and a catalog entry (`catalog-entries.json` is ready, a PR against Schwung's `module-catalog.json`), after it has run on a Move.
- Sound names show only for the selected sound; the engine's sound-state key is unused (Schwung keeps the control values).

## Acknowledgements and legal
Clementine-XT exists because of the Waldorf Microwave II and Microwave XT. Its sound engine is original C code, measured against the instrument's
behaviour, and it reads the instrument's waves from your own ROM at runtime. **No ROM, wave, sound bank, logo or panel art of the original is
included in this repository or its releases.** Waldorf and Microwave are trademarks of their owners. This project is independent and not affiliated
with or endorsed by Waldorf.

## Licence
GPL-3.0-only (see `LICENSE`). Vendored third-party code is listed in `VENDORED.md`.
