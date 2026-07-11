#!/usr/bin/env bash
# Installs SpeedBoster and its dependencies on Zorin/Ubuntu.
set -euo pipefail

if [ "$(id -u)" -eq 0 ]; then
    echo "Run this as your normal user, not root (it will ask for sudo when needed)." >&2
    exit 1
fi

echo "==> Installing system dependencies"
sudo apt update
sudo apt install -y python3-gi gir1.2-appindicator3-0.1 lm-sensors dkms git build-essential \
    liblua5.4-dev pkg-config libxml2-dev

echo "==> Configuring lm-sensors (answer the prompts, defaults are fine)"
sudo sensors-detect --auto || true

if ! command -v nbfc >/dev/null 2>&1; then
    echo "==> Installing nbfc-linux (fan control daemon)"
    tmpdir=$(mktemp -d)
    git clone --depth 1 https://github.com/nbfc-linux/nbfc-linux "$tmpdir/nbfc-linux"
    (cd "$tmpdir/nbfc-linux" && sudo make install)
    sudo systemctl enable --now nbfc.service
    rm -rf "$tmpdir"
else
    echo "==> nbfc already installed, skipping"
fi

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

echo
echo "Done. Make sure $BIN_DIR is on your PATH, then:"
echo "  1. Run 'nbfc config -a' and pick your model from the list (needed once)."
echo "  2. Launch SpeedBoster from the app menu, or run 'speedboster' in a terminal."
