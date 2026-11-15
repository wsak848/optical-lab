"""Optical power and fiber-only attenuation model for Lab 3."""
import math

POWER_TRIALS = (0.1, 0.5, 1.0, 2.0, 10.0)
LENGTH_TRIALS = (1, 5, 10, 15, 20)
TEACHING_PROFILES = {
    '850 nm / Multimode Fiber': 3.0,
    '1310 nm / Single-mode Fiber': 0.35,
    '1550 nm / Single-mode Fiber': 0.20,
}
DEFAULT_PROFILE = '1550 nm / Single-mode Fiber'


def finite_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('กรุณากรอกตัวเลขที่มีค่าจำกัดให้ครบถ้วน')
    return value


def mw_to_dbm(power_mw):
    if finite_number(power_mw) <= 0:
        raise ValueError('กำลังแสง (mW) ต้องมากกว่าศูนย์')
    return 10 * math.log10(power_mw)


def dbm_to_mw(power_dbm):
    finite_number(power_dbm)
    try:
        value = 10 ** (power_dbm / 10)
    except OverflowError as error:
        raise ValueError('กำลังแสงอยู่นอกช่วงที่คำนวณได้') from error
    if not math.isfinite(value) or value <= 0:
        raise ValueError('กำลังแสงอยู่นอกช่วงที่คำนวณได้')
    return value


def fiber_loss(alpha, length_km):
    if finite_number(alpha) < 0:
        raise ValueError('ค่า attenuation ต้องไม่ติดลบ')
    if finite_number(length_km) < 0:
        raise ValueError('ระยะทาง Fiber ต้องไม่ติดลบ')
    return finite_number(alpha * length_km)


def output_power(pin_dbm, alpha, length_km):
    return finite_number(finite_number(pin_dbm) - fiber_loss(alpha, length_km))


def check_db_answer(answer, reference, tolerance=0.1):
    """Absolute dB error also works for zero and negative dBm references."""
    finite_number(answer)
    finite_number(reference)
    if finite_number(tolerance) < 0:
        raise ValueError('Tolerance ต้องไม่ติดลบ')
    error = finite_number(abs(answer - reference))
    return dict(answer=answer, reference=reference, error=error,
                correct=error <= tolerance or math.isclose(error, tolerance, rel_tol=0, abs_tol=1e-12))


def check_fiber_trial(length, loss_answer, pout_answer):
    loss = fiber_loss(0.20, length)
    checked = check_db_answer(pout_answer, output_power(0, 0.20, length))
    checked['loss'] = check_db_answer(loss_answer, loss)
    checked['correct'] = checked['correct'] and checked['loss']['correct']
    return checked


def summarize(results):
    values = list(results.values())
    return (len(values), sum(r['correct'] for r in values),
            sum(r['error'] for r in values) / len(values) if values else None)
