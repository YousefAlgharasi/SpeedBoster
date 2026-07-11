"""Fan control via nbfc-linux (Notebook FanControl)."""
import re
import subprocess

NBFC = "nbfc"


class FanControlError(RuntimeError):
    pass


def _run(args):
    try:
        result = subprocess.run([NBFC, *args], capture_output=True, text=True, timeout=5)
    except FileNotFoundError as exc:
        raise FanControlError("nbfc is not installed. See README for setup.") from exc
    if result.returncode != 0:
        raise FanControlError(result.stderr.strip() or f"nbfc {' '.join(args)} failed")
    return result.stdout


def status():
    """Return dict with keys: fan_speed (percent, float|None), auto (bool)."""
    out = _run(["status", "-a"])
    fan_speed = None
    auto = True
    m = re.search(r"Current Fan Speed\s*:\s*([\d.]+)", out)
    if m:
        fan_speed = float(m.group(1))
    m = re.search(r"Auto Control\s*:\s*(\w+)", out)
    if m:
        auto = m.group(1).lower() == "enabled"
    return {"fan_speed": fan_speed, "auto": auto}


def set_speed(percent):
    """Lock fan to a manual speed percentage (0-100)."""
    percent = max(0, min(100, int(percent)))
    _run(["set", "-s", str(percent)])


def set_auto():
    """Release manual control, let firmware manage the fan again."""
    _run(["set", "-a"])
