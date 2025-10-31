"""Sensor reading functions for CPU and GPU temperatures."""

import psutil

try:
    from pynvml import (
        nvmlInit,
        nvmlDeviceGetHandleByIndex,
        nvmlDeviceGetTemperature,
        NVML_TEMPERATURE_GPU,
        NVMLError,
    )
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


def get_cpu_temp():
    """
    Read CPU temperature from system sensors.

    Returns:
        float or None: CPU temperature in Celsius, or None if unavailable
    """
    try:
        temps = psutil.sensors_temperatures()

        # Try different sensor names depending on platform
        if "coretemp" in temps:
            return temps["coretemp"][0].current
        elif "cpu_thermal" in temps:
            return temps["cpu_thermal"][0].current
        elif "k10temp" in temps:  # AMD CPUs
            return temps["k10temp"][0].current

        # Fallback: return first available sensor
        for name, entries in temps.items():
            if entries:
                return entries[0].current

    except (AttributeError, IndexError, KeyError):
        pass

    return None


def get_gpu_temp():
    """
    Read GPU temperature using NVML (NVIDIA GPUs only).

    Returns:
        float or None: GPU temperature in Celsius, or None if unavailable
    """
    if not NVML_AVAILABLE:
        return None

    try:
        nvmlInit()
        handle = nvmlDeviceGetHandleByIndex(0)
        temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
        return float(temp)
    except (NVMLError, Exception):
        return None
