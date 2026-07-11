"""Fan control via the msi-ec kernel driver's sysfs interface."""
import glob

MSI_EC_ROOT = "/sys/devices/platform/msi-ec"

MODES = ("auto", "silent", "basic", "advanced")


class FanControlError(RuntimeError):
    pass


def _read(relpath):
    path = f"{MSI_EC_ROOT}/{relpath}"
    try:
        with open(path) as f:
            return f.read().strip()
    except OSError as exc:
        raise FanControlError(f"msi-ec not available ({path}): {exc}") from exc


def _write(relpath, value):
    path = f"{MSI_EC_ROOT}/{relpath}"
    try:
        with open(path, "w") as f:
            f.write(str(value))
    except OSError as exc:
        raise FanControlError(f"failed writing {path}: {exc}") from exc


def available():
    return bool(glob.glob(MSI_EC_ROOT))


def status():
    """Return dict with fan_mode, cooler_boost (bool), cpu_rpm_pct, gpu_rpm_pct."""
    return {
        "fan_mode": _read("fan_mode"),
        "cooler_boost": _read("cooler_boost") == "on",
        "cpu_fan_speed": _read("cpu/realtime_fan_speed"),
        "gpu_fan_speed": _read("gpu/realtime_fan_speed"),
    }


def set_mode(mode):
    if mode not in MODES:
        raise FanControlError(f"unknown fan mode {mode!r}, expected one of {MODES}")
    _write("fan_mode", mode)


def set_cooler_boost(enabled):
    _write("cooler_boost", "on" if enabled else "off")
