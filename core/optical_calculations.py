import math


SPEED_OF_LIGHT_M_S = 3.0e8


def wavelength_to_frequency(wavelength_nm: float) -> tuple[float, float, float]:
    """Convert a finite positive vacuum wavelength (nm) to meters, Hz, and THz."""
    if not math.isfinite(wavelength_nm):
        raise ValueError("Wavelength must be finite (not NaN or infinity).")
    if wavelength_nm <= 0:
        raise ValueError("Wavelength must be greater than zero.")

    wavelength_m = wavelength_nm * 1e-9
    frequency_hz = SPEED_OF_LIGHT_M_S / wavelength_m
    frequency_thz = frequency_hz / 1e12
    return wavelength_m, frequency_hz, frequency_thz
