import math
import unittest

from core.optical_calculations import wavelength_to_frequency


class WavelengthToFrequencyTests(unittest.TestCase):
    def test_independent_expected_values(self):
        # Reference values for c = 3.0e8 m/s, including both slider endpoints.
        cases = (
            (400, 4.00e-7, 7.50000000000000e14, 750.000000000000),
            (850, 8.50e-7, 3.52941176470588e14, 352.941176470588),
            (1310, 1.31e-6, 2.29007633587786e14, 229.007633587786),
            (1550, 1.55e-6, 1.93548387096774e14, 193.548387096774),
            (1700, 1.70e-6, 1.76470588235294e14, 176.470588235294),
        )
        for nm, expected_m, expected_hz, expected_thz in cases:
            with self.subTest(wavelength_nm=nm):
                actual = wavelength_to_frequency(nm)
                for value, expected, absolute_tolerance in zip(
                    actual,
                    (expected_m, expected_hz, expected_thz),
                    (1e-18, 1.0, 1e-9),
                ):
                    self.assertTrue(
                        math.isclose(value, expected, rel_tol=1e-12, abs_tol=absolute_tolerance),
                        f"{value} differs from expected {expected}",
                    )

    def test_frequency_decreases_as_wavelength_increases(self):
        frequencies = [wavelength_to_frequency(nm)[1] for nm in (400, 850, 1310, 1550, 1700)]
        for shorter, longer in zip(frequencies, frequencies[1:]):
            self.assertGreater(shorter, longer)

    def test_rejects_zero(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            wavelength_to_frequency(0)

    def test_rejects_negative_wavelength(self):
        with self.assertRaisesRegex(ValueError, "greater than zero"):
            wavelength_to_frequency(-1)

    def test_rejects_nan(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            wavelength_to_frequency(float("nan"))

    def test_rejects_infinity(self):
        for value in (float("inf"), float("-inf")):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "finite"):
                    wavelength_to_frequency(value)


if __name__ == "__main__":
    unittest.main()
