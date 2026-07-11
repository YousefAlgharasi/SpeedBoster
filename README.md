# SpeedBoster

A minimal Dragon Center replacement for Zorin OS: a system-tray app that shows
CPU/GPU temperatures and lets you manually lock the fan to a chosen speed.

## How it works

- **Temperatures**: CPU via `lm-sensors` hwmon (`coretemp`/`k10temp`), GPU via `nvidia-smi`.
- **Fan control**: via [`nbfc-linux`](https://github.com/nbfc-linux/nbfc-linux), which
  talks to the laptop's embedded controller through ACPI — no MSI-specific kernel
  module required, and it supports a wide range of MSI models out of the box.
- **UI**: a GTK/AppIndicator tray icon with live temps, a fan speed slider, and a
  "Lock fan speed" toggle (unlocked = firmware auto control).

## Install

```bash
git clone <this repo>
cd SpeedBoster
chmod +x install.sh
./install.sh
```

The installer sets up `lm-sensors`, builds and installs `nbfc-linux`, and places
`speedboster` on your PATH plus an app-menu shortcut.

After installing, run once:

```bash
nbfc config -a
```

and pick the config matching your MSI model from the list. If your exact model
isn't listed, pick the closest one (same chassis generation) — this is the same
approach Windows tools like NBFC/Dragon Center use internally.

## Run

Launch **SpeedBoster** from your app menu, or run `speedboster` in a terminal.
Click the tray icon to see temps, drag the slider to set a fan percentage, and
check "Lock fan speed" to apply it (uncheck to hand control back to firmware).

## Notes

- If `nbfc config -a` doesn't list your model, fan control won't work reliably —
  temperature monitoring will still work fine on its own.
- Tested against generic MSI EC behavior; some models expose CPU/GPU as
  separate fans (`nbfc set -f 0 -s N` / `-f 1 -s N`) — this can be added if
  your model needs per-fan control.
