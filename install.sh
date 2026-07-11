#!/usr/bin/env bash
# Installs SpeedBoster and its dependencies on Zorin/Ubuntu for MSI laptops.
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    echo "Run this as your normal user, not root (it will ask for sudo when needed)." >&2
    exit 1
fi

echo "==> Installing system dependencies"
sudo apt update
sudo apt install -y python3-gi gir1.2-appindicator3-0.1 lm-sensors dkms git build-essential \
    "linux-headers-$(uname -r)"

echo "==> Configuring lm-sensors (answer the prompts, defaults are fine)"
sudo sensors-detect --auto || true

if ! dkms status 2>/dev/null | grep -q '^msi_ec'; then
    echo "==> Installing msi-ec (MSI embedded-controller driver)"
    tmpdir=$(mktemp -d)
    git clone --depth 1 https://github.com/BeardOverflow/msi-ec.git "$tmpdir/msi-ec"
    (cd "$tmpdir/msi-ec" && sudo make dkms-install)
    rm -rf "$tmpdir"
else
    echo "==> msi-ec already registered with DKMS, skipping build"
fi
sudo modprobe msi-ec

echo "==> Setting up permissions so SpeedBoster can control fan settings without root"
sudo groupadd -f msi-ec
sudo usermod -aG msi-ec "$USER"
sudo tee /etc/udev/rules.d/99-msi-ec.rules > /dev/null <<'EOF'
SUBSYSTEM=="platform", KERNEL=="msi-ec", RUN+="/bin/chgrp msi-ec /sys/devices/platform/msi-ec/fan_mode /sys/devices/platform/msi-ec/cooler_boost", RUN+="/bin/chmod 664 /sys/devices/platform/msi-ec/fan_mode /sys/devices/platform/msi-ec/cooler_boost"
EOF
sudo udevadm control --reload-rules
sudo rmmod msi_ec 2>/dev/null || true
sudo modprobe msi-ec

echo "==> Installing SpeedBoster"
INSTALL_DIR="$HOME/.local/share/speedboster"
mkdir -p "$INSTALL_DIR"
cp -r "$(dirname "$0")/speedboster" "$INSTALL_DIR/"

BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/speedboster" <<EOF
#!/usr/bin/env bash
export PYTHONPATH="$INSTALL_DIR:\$PYTHONPATH"
exec python3 -m speedboster.tray
EOF
chmod +x "$BIN_DIR/speedboster"

DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"
cp "$(dirname "$0")/speedboster.desktop" "$DESKTOP_DIR/"

echo "==> Enabling autostart on login"
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"
cp "$(dirname "$0")/speedboster.desktop" "$AUTOSTART_DIR/"

echo
echo "Done. You were added to the 'msi-ec' group -- log out and back in (or reboot)"
echo "for that to take effect, otherwise fan control will fail with a permission error."
echo "Make sure $BIN_DIR is on your PATH, then launch SpeedBoster from the app menu"
echo "or run 'speedboster' in a terminal. It will now also start automatically on login."
