"""Temperature readers for CPU and NVIDIA GPU."""
import glob
import re
import subprocess


def read_cpu_temp():
    """Return CPU package temperature in Celsius, or None if unavailable."""
    for path in glob.glob("/sys/class/hwmon/hwmon*/name"):
        try:
            with open(path) as f:
                name = f.read().strip()
        except OSError:
            continue
        if name not in ("coretemp", "k10temp", "zenpower"):
            continue
        hwmon_dir = path.rsplit("/", 1)[0]
        for temp_input in sorted(glob.glob(f"{hwmon_dir}/temp*_input")):
            label_path = temp_input.replace("_input", "_label")
            label = ""
            try:
                with open(label_path) as f:
                    label = f.read().strip()
            except OSError:
                pass
            if name == "coretemp" and label and "Package" not in label:
                continue
            try:
                with open(temp_input) as f:
                    milli = int(f.read().strip())
                return milli / 1000.0
            except (OSError, ValueError):
                continue
    return None


def read_gpu_temp():
    """Return NVIDIA GPU temperature in Celsius, or None if unavailable."""
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=2,
        )
        if out.returncode == 0:
            match = re.search(r"\d+", out.stdout)
            if match:
                return float(match.group())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None
