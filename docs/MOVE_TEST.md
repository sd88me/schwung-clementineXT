# First run on a Move: checklist

Nothing here has been done yet (no Move was available when the module was written). Do it in this order and note what you find.

1. `scripts/test.sh && scripts/build.sh`, then `scripts/deploy.sh <move host> --reboot` (save your set first; never point it at the Force).
2. Enable logs (deploy.sh does) and `tail -f /data/UserData/schwung/debug.log`. Add **Clementine-XT** as the synth of a slot.
   - Missing from the list: the module.json is read from the chain host; check for `dlopen failed` in the log (the dsp must be `dsp.so`).
   - Silent for a second or two, then the sound name appears: normal, the engine loads on its worker thread (`(loading)` shows meanwhile).
3. Pages: root shows the sound list with Play 1-4, Cutoff, Reso, Volume, Prm 1 on the eight knobs. Walk every sub-page (see README "Pages") and check
   that labels read as words, values move, enum squares read (short options), and the bank picker lists your `.syx` files.
4. Sound: play pads and an external keyboard, bend, mod wheel, the arpeggiator (Tempo 0 follows the Move's tempo), the four Play assigns.
5. CPU / dropouts: hold ten voices with a busy sound and watch for crackle; compare the per-block time with `rt_thread_audit_on` / `spi_tally_on`
   (docs/REALTIME_SAFETY.md upstream). Load a bank and change banks while playing (must not click: bank loads run on the worker).
6. Save the set, reload it: the sound should come back (the module state is the engine's `state` parameter, not tested on a Move yet).
7. Two instances in two slots, and the module on a chain bus insert position if you use one (create runs on a worker there; engine tables are guarded by a lock).
8. Report findings in the README status line; only then publish a release and the catalog entry (`catalog-entries.json`).
