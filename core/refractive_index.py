"""Approximate educational phase refractive indices and calculation checks."""
import math

from core.optical_calculations import SPEED_OF_LIGHT_M_S

MEDIA = {
    'อากาศ (Air)': 1.0003,
    'น้ำ (Water)': 1.333,
    'อะคริลิก (Acrylic / PMMA)': 1.49,
    'ซิลิกาหลอม (Fused Silica)': 1.458,
    'เพชร (Diamond)': 2.4168,
}


def light_speed(n):
    """Return c/n for a finite positive refractive index."""
    if isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) or n <= 0:
        raise ValueError('Refractive index must be a finite positive number.')
    speed = SPEED_OF_LIGHT_M_S / n
    if not math.isfinite(speed) or speed <= 0:
        raise ValueError('Refractive index produces an unrepresentable speed.')
    return speed


def check_calculation(medium, answer):
    if isinstance(answer, bool) or not isinstance(answer, (int, float)) or not math.isfinite(answer) or answer <= 0:
        raise ValueError('กรุณากรอกความเร็วเป็นจำนวนบวกที่มีค่าจำกัด')
    reference = light_speed(MEDIA[medium])
    difference = abs(answer - reference)
    error = difference / reference * 100
    return dict(medium=medium, n=MEDIA[medium], reference=reference,
                answer=answer, difference=difference, error=error,
                correct=error <= 0.5 or math.isclose(error, 0.5, abs_tol=1e-12))


def summarize(results):
    values = list(results.values())
    return (len(values), sum(r['correct'] for r in values),
            sum(r['error'] for r in values) / len(values) if values else None)
