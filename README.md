# SpeedBoster

A minimal Dragon Center replacement for Zorin OS on MSI laptops: a system-tray
app that shows CPU/GPU temperatures and lets you set the fan mode (auto,
silent, basic, advanced) or trigger Cooler Boost.

## How it works

- **Temperatures**: read directly from [`msi-ec`](https://github.com/BeardOverflow/msi-ec)'s
  `cpu/realtime_temperature` and `gpu/realtime_temperature`, falling back to
  `lm-sensors` hwmon / `nvidia-smi` if msi-ec isn't loaded.
- **Fan control**: via `msi-ec`, an in-kernel driver that recognizes your
  laptop's embedded-controller firmware version and exposes safe sysfs
  controls — `fan_mode` (auto/silent/basic/advanced) and `cooler_boost`
  (on/off). This is a proper kernel driver validated against known EC
  firmware versions, not raw register poking.
- **UI**: a GTK/AppIndicator tray icon with live temps, radio buttons for
  fan mode, and a Cooler Boost checkbox.

Requires **Secure Boot disabled** in BIOS (needed for the DKMS-built kernel
module to load, or for it to be signed against your own MOK key).

## Install

```bash
git clone <this repo>
cd SpeedBoster
chmod +x install.sh
./install.sh
```

The installer sets up `lm-sensors`, builds and loads `msi-ec` via DKMS, adds a
udev rule + `msi-ec` group so SpeedBoster can control fan settings without
running as root, and places `speedboster` on your PATH plus an app-menu
shortcut.

**Log out and back in (or reboot)** after installing so your user's new group
membership takes effect.

## Run

Launch **SpeedBoster** from your app menu, or run `speedboster` in a
terminal. Click the tray icon to see live temps, pick a fan mode, or toggle
Cooler Boost.

## Notes

- `msi-ec` only supports laptops whose EC firmware version it recognizes —
  check the [supported devices list](https://github.com/BeardOverflow/msi-ec/discussions/277)
  for your model before installing. If unsupported, temperature monitoring
  still falls back to hwmon/`nvidia-smi`.
- This driver exposes fan *modes*, not an arbitrary duty-cycle percentage —
  that matches what the MSI firmware itself actually allows on supported
  models.
