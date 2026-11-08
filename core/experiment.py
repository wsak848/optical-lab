"""Experiment records use the existing vacuum wavelength model."""
import math

from core.optical_calculations import wavelength_to_frequency


def create_trial(wavelength_nm):
    wavelength_m, _, frequency_thz = wavelength_to_frequency(wavelength_nm)
    return dict(wavelength_nm=wavelength_nm, wavelength_m=wavelength_m,
                simulation_thz=frequency_thz, student_thz=None,
                difference=None, percent_error=None, correct=None)


def check_trial(trial, student_thz):
    """Return a checked copy, retaining the recorded wavelength and reference."""
    if student_thz is None or not math.isfinite(student_thz) or student_thz <= 0:
        raise ValueError("กรุณากรอกค่าความถี่เป็นจำนวนบวกที่มีค่าจำกัด")
    difference = abs(trial['simulation_thz'] - student_thz)
    percent_error = difference / trial['simulation_thz'] * 100
    return {**trial, 'student_thz': student_thz, 'difference': difference,
            'percent_error': percent_error,
            'correct': percent_error <= 0.5 or math.isclose(percent_error, 0.5, abs_tol=1e-12)}


def summarize(trials):
    completed = [t for t in trials if t['student_thz'] is not None]
    return (len(completed), sum(t['correct'] for t in completed),
            sum(t['percent_error'] for t in completed) / len(completed) if completed else None)
