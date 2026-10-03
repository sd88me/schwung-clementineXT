# Clementine-XT for Schwung

A wavetable synthesizer for Ableton Move, as a [Schwung](https://github.com/charlesvestal/schwung) sound-generator module. It plays the way the
Waldorf Microwave II and Microwave XT did: two wavetable oscillators with FM, sync and ring modulation, thirteen filter types, a 16-slot modulation
matrix with modifiers, an arpeggiator and a chain of effects, in ten voices at the original's 40 kHz internal rate. It loads the instrument's own
`.syx` sound banks and wavetables from factory ROM.

It is the same engine as the [MPC plugin](https://github.com/sd88me/mpc-vst-clementineXT) (a native VST2 instrument for Akai MPC OS devices), with
two ways to play it on a Move: a **playable subset on the Move's own knobs and screen**, and **full control of every parameter in a browser panel**.

*Clementine-XT is an independent project. The XT in the name is a nod to the Microwave XT (and, like Surge XT, reads as "extended").
It is not affiliated with or endorsed by Waldorf. See [Acknowledgements](#acknowledgements-and-legal).*

<img width="288" height="290" alt="image" src="https://github.com/user-attachments/assets/83babac8-4e38-4cd0-a3b5-29e43a0d569a" />

## Your ROM and sound banks

User files live in `/data/UserData/schwung/clementine-xt/ROMS/` (created on first load; override with the `CLEMENTINE_XT_DATA` environment variable).
It sits outside the module folder, so module updates and reinstalls keep it.

- **Waves and wave tables:** copy your Microwave II ROM dump there, either the two 128 KB chip images (for example `lower_Am29F010.bin` and
  `upper_Am29F010.bin`; any `.bin` names work) or one 256 KB image. Add a fresh instance of the module (remove it from the track and add it again) and
  the 506 original waves and the factory wave tables load. Tables 28-51 are computed by the module itself, so they work whatever the chips hold.
- **Sound banks:** copy any Microwave II/XT `.syx` file (a single sound or a whole bank dump) there. Each file appears as a bank on the Bank page
  (and in the browser panel), named after the file (`Factory.syx` is the bank "Factory").
- **No ROM:** the built-in bank (12 sounds) plays on an original open set of wave tables. Sounds that use the original tables will sound different
  from the instrument.

You must own the instrument or have the right to use its ROM. The project does not provide it and will not help find it.

## How it is built, and how close it is to the original

Clementine-XT is **not an emulation of the instrument's firmware or ROM**. It is a new engine in portable C (no 64-bit-only code, so it also runs on
32-bit ARM devices) built around the Microwave XT's own data model, then tuned against the real firmware's output. This module and the MPC plugin
share that engine, which is developed and calibrated in the MPC plugin's repository.

**Design**

- **The XT's sound format.** A sound is the XT's 256-byte parameter block (`.syx` single sounds and bank dumps load as they are), so every parameter has
  the original's range, meaning and MIDI controller number.
- **Waves as the instrument holds them.** A wave is 128 signed 8-bit samples, read through the instrument's mip levels and 64-slot wave tables, so the
  stepped, slightly aliased character comes from the same data rather than from an imitation of it. The 506 original waves and the factory tables are read
  at runtime from *your* ROM dump; without one, 12 open wave tables stand in.
- **The original's rate.** Voices run at the XT's 40 kHz internal rate and are resampled to the host's rate, so aliasing falls where it did on the
  hardware. Ten voices, as on the XT.
- **Signal path in the XT's order.** Two wavetable oscillators (FM, sync, ring modulation, noise, external input) into the mixer, Filter 1 (13 types) and
  Filter 2, amplifier, pan, then the effect and chorus; four envelopes (filter, amplifier, wave, free), two LFOs, the 16-slot matrix with four modifiers and
  the control delay, glide, poly / mono / dual / unison allocation, and the arpeggiator.

**How the accuracy was checked**

The original firmware was run offline on a desktop computer, with its own ROM, as a reference rig. Test sounds were rendered through both it and this
engine at 40 kHz and compared: pitch, spectrum, level, envelope timing and modulation. That rig is a development tool only; it is never shipped and none of
its output is in either repository. What the measurements found (the MPC repository's `docs/CALIBRATION.md` has each one):

- Oscillator pitch matches to 0.0 cents, and the harmonic content of a wave follows the original's.
- Of the 248 comparable factory sounds, 183 are within 3 dB of the original's level and 221 within 6 dB (mean spectral band error 13 dB).
- The modulation matrix and LFOs, mixer sources, wave and free envelopes, voice allocation, glide, the arpeggiator and the effects were each measured and
  fitted. Filter 1 types 0-4, 7, 10 and 11 are fitted to the original's responses; 20 of the 24 computed wave tables reproduce it.

So it is faithful in structure and close in sound, not identical. The remaining differences are listed under [Known limitations](#known-limitations).

**Numbers**

| | |
|---|---|
| Polyphony | 10 voices (mono, dual and unison modes use them) |
| Internal rate | 40 kHz, resampled to the host rate; Move block size 128 |
| Oscillators | 2 wavetable oscillators, 506 waves, 64-slot tables, 8-bit stepped waves, FM, sync, ring mod, noise, external input |
| Filters | Filter 1: 13 types; Filter 2: 6 dB low or high pass |
| Modulation | 16 matrix slots, 4 modifiers, 2 LFOs, 4 envelopes, control delay |
| Effects | the XT's ten effect types plus chorus |
| Controls | 202 parameters; 14 pages on the Move, all of them in the browser panel |
| Module | `sound_generator`, plugin API v2, aarch64, GLIBC 2.34 or older |
| Licence | GPL-3.0-only |


## Two ways to play it

The Move has eight knobs and a small screen, and the engine has 202 controls. So the module splits the job:

| | On the Move (knobs, jog wheel, screen) | In the browser panel |
|---|---|---|
| **Purpose** | Play and tweak: the controls you reach for while performing | **Full control** of every parameter, laid out like the MPC plugin |
| **Sounds** | Sound list (0-255 of the current bank) and a Bank picker | Bank picker and a numbered 1-256 sound grid |
| **Controls** | 14 pages of up to eight knobs (below) | All 202 controls on five tabs |
| **Not reachable** | Filter 2, quality, the wave and free envelopes, glide, voices, the arpeggiator, the 16-slot modulation matrix, the modifiers, the control delay | none |

Everything the Move's pages leave out is still a normal parameter: it is saved with the set, and the browser panel moves it.

### On the Move

The root page is the sound list (turn the jog wheel to pick a sound, click to open the pages). The eight knobs on the root page are **Play 1-4**,
**Cutoff**, **Reso**, **Volume** and **Prm 1** (the effect's first parameter). The pages, at most eight knobs each:

| Page | Knobs |
|---|---|
| Bank, Play Assign | the `.syx` bank picker; which parameter each Play knob drives, over its whole range |
| Oscillator 1 / 2 | Octave, Semi, Detune, Bend, Keytrack, FM Amt, Table, Link / Octave, Semi, Detune, Bend, Keytrack, Sync |
| Wave 1 / 2, Mixer | Start, Phase, Env Amt, Env Velo, Keytrack, Limit (+ Link) / Wave 1, Wave 2, Ring, Noise, Ext |
| Filter 1, Filter Envelope | Cutoff, Reso, Type, Keytrack, Env Amt, Env Velo, Spec / Attack, Decay, Sustain, Release, Trigger |
| Amplifier, Amp Envelope | Volume, Velo, Keytrack, Panning, PKey, Chorus / Attack, Decay, Sustain, Release, Trigger |
| LFO 1, LFO 2 | Rate, Shape, Delay, Sync, Symm, Human (+ Phase on LFO 2) |
| Effect | Type, Prm 1-3 |

**Play knobs.** On the Microwave every sound chooses four parameters to put under four knobs for performance. Here the Play Assign page chooses them,
and Play 1-4 on the root page turn whichever parameter you picked, over its whole range.

**MIDI.** Notes, pitch bend, mod wheel, aftertouch, sustain, breath and foot follow the XT's own controller map; most sound parameters answer to their
Microwave controller numbers. With the arpeggiator Tempo set to 0 (extern) it follows the Move's tempo.

### In the browser

Open Schwung Manager's Remote UI (`http://<move>:7700/remote-ui`) and the Clementine-XT slot shows the panel; the module's page in the manager also
links to it. It is the MPC plugin's screen: the same layout, blue section titles over an orange plate, dark knobs with the four Play knobs in red, red
LCD steppers, green dot-matrix readouts and the logo. The MPC plugin's ten tabs are stacked in pairs into five (the page scrolls):

| Tab | Holds |
|---|---|
| **SOUND** | Play knobs and their parameter pickers, bank and sound steppers with names, effect, voices, glide, output; below them the bank picker and the 1-256 sound grid |
| **OSC + WAVE** | Oscillators 1 and 2, quality; Waves 1 and 2, mixer |
| **FILTER + ENV** | Filter 1 and 2, filter and amp envelopes; the wave and free envelopes |
| **LFO ARP + MODIFIERS** | LFO 1 and 2, the arpeggiator; the four modifiers and the control delay |
| **MOD MATRIX** | The 16 modulation slots (source, destination, amount) |

Drag a knob to turn it (Shift for fine), use the mouse wheel to step it, double-click to reset it. Popups are dropdown lists. The sound grid is numbered
because the module does not publish sound names; the current sound's name shows in the readout.

**Saving.** The sound you are playing is part of the set (Schwung keeps the control values), so a set reloads as you left it. There is no separate
"save preset" button in the module.

## Known limitations

- Four of the 24 computed wave tables (43, 46, 50 and 51) and the user tables are stand-ins, and some of the filter types (waveshaper, FM, S&H, band
  stop) are approximations. About three quarters of the factory sounds are within 3 dB of the original in level.
- Several effects are approximate (wah sensitivity, mod delay depth), and the arpeggiator's hold mode, user pattern and a few edge cases differ from
  the original.
- Free-running oscillator phase makes two oscillators at the same pitch add up differently from note to note, as on the original, but not the same way in
  every sound.
- The Move's own screen shows the name of the selected sound only, and the browser panel's sound grid is numbered, because the module does not publish
  the names of all 256 sounds.
- Controls left off the Move's pages (see the table) can be changed from the browser panel or from automation, not from the pages.

## What you need

- An Ableton Move running Schwung (the module is built against Schwung 1.6.3's plugin API).
- **Optional but recommended: your own copy of the Microwave II ROM.** The module does not include one (see below). Without it you get 12 built-in
  sounds on an original set of wave tables; with it you get the real waves and can load the instrument's factory banks.

## Install

1. Download `clementine-xt-module.tar.gz` from the releases page, or build it (below).
2. Install it with Schwung Manager (Custom Install from a file), or unpack it into `/data/UserData/schwung/modules/sound_generators/`
   (`scripts/deploy.sh <move host>` does that over ssh, and reboots the Move with `--reboot`; the native DSP is only loaded at boot).
3. Copy your ROM and banks as below, then add **Clementine-XT** as the synth of a track in the chain.
  
## Troubleshooting

- **The module is not in the list of synths:** reboot the Move (the native DSP loads at boot), and look for `dlopen failed` in
  `/data/UserData/schwung/debug.log` (create `/data/UserData/schwung/debug_log_on` to enable it). The DSP file must be called `dsp.so`.
- **The sound name says "(loading)" for a moment:** normal, the engine starts on its worker thread. If it stays, check the log and that the ROM files are
  the expected size.
- **The waves sound plain, or the factory bank is missing:** the ROM or `.syx` files are not in `ROMS`, or the ROM files are not 128 KB each (or 256 KB
  combined). Add a fresh instance after copying them.
- **The browser panel shows the default controls:** the slot in Schwung Manager has an Interface toggle; set it to the custom panel.

## Build and test

```
scripts/test.sh     # engine pin check, regenerates module.json and the browser panel, engine unit tests, a host simulation of the module (x86, ASan)
scripts/build.sh    # aarch64 module tarball in build/ (needs Docker)
scripts/deploy.sh <move host> [--reboot]   # staged install on a Move (see docs/MOVE_TEST.md for the first-run checklist)
scripts/preview_web_ui.sh                  # screenshots of every tab of the browser panel (Docker, no device)
```

**The engine and the skin are developed in the MPC plugin repository, not here.** `scripts/sync_engine.sh` copies its `src/` into `engine/` and its
layout, stylesheet and logo into `skin/`, and records the commit (`engine/UPSTREAM`) and the files' checksums; `scripts/check_engine.sh` (run by
`test.sh`) fails if either folder was edited by hand or no longer matches the pinned commit, and warns when the MPC repository has newer engine changes.

| Path | |
|---|---|
| `engine/` | the synth engine (a copy of the MPC repo's `src/`, see `engine/UPSTREAM`), and `params.json`, the control list |
| `skin/` | the MPC plugin's layout, stylesheet and logo: the design source of the browser panel |
| `src/schwung_plugin.c` | `plugin_api_v2` around the engine: loader thread, parameter and MIDI plumbing, the preset and bank pickers |
| `tools/gen_schwung.py` | generates `module.json` and `src/schwung_meta.h` (the controls and the Move's pages) |
| `tools/gen_web_ui.py` | generates `web/web_ui.html`, the browser panel |
| `vendor/` | Schwung's API header (MIT) and the engine interface; see `VENDORED.md` |
| `test/` | the engine's unit tests and `host_sim.c` |

`catalog-entries.json` is the entry for Schwung's module catalog (a pull request against `charlesvestal/schwung`), for when a release exists.

## Acknowledgements and legal

Clementine-XT exists because of the Waldorf Microwave II and Microwave XT. Its sound engine is original C code, measured against the instrument's
behaviour, and it reads the instrument's waves from your own ROM at runtime. **No ROM, wave, sound bank, logo or panel art of the original is
included in this repository or its releases.** Waldorf and Microwave are trademarks of their owners. This project is independent and not affiliated
with or endorsed by Waldorf.

Built for [Schwung](https://github.com/charlesvestal/schwung); the plugin API header is vendored from it (MIT).

## Licence

GPL-3.0-only (see `LICENSE`). Vendored third-party code is listed in `VENDORED.md`.
