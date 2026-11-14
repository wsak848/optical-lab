import math
import unittest

from core.refractive_index import MEDIA, check_calculation, light_speed, summarize
from core.refractive_index_ui import experiment_rows


class RefractiveIndexTests(unittest.TestCase):
    def test_five_media_and_reference_speeds(self):
        expected = [
            ('อากาศ (Air)', 1.0003, 299910026.9919024),
            ('น้ำ (Water)', 1.333, 225056264.0660165),
            ('อะคริลิก (Acrylic / PMMA)', 1.49, 201342281.8791946),
            ('ซิลิกาหลอม (Fused Silica)', 1.458, 205761316.8724280),
            ('เพชร (Diamond)', 2.4168, 124131082.4230387),
        ]
        self.assertEqual(len(MEDIA), 5)
        for name, n, speed in expected:
            with self.subTest(medium=name):
                self.assertEqual(MEDIA[name], n)
                self.assertAlmostEqual(light_speed(n), speed, places=5)
                self.assertTrue(check_calculation(name, float(f'{speed:.3g}'))['correct'])

    def test_vacuum_and_inverse_relation(self):
        self.assertEqual(light_speed(1), 3e8)
        speeds = [light_speed(n) for n in sorted(MEDIA.values())]
        self.assertLess(max(speeds), light_speed(1))
        self.assertTrue(all(a > b for a, b in zip(speeds, speeds[1:])))
        self.assertAlmostEqual(light_speed(2), light_speed(1) / 2)

    def test_invalid_indices(self):
        for n in (0, -1, math.nan, math.inf, -math.inf, None, '1.3', True, 1e-320):
            with self.subTest(n=n), self.assertRaises(ValueError):
                light_speed(n)

    def test_invalid_answers(self):
        for answer in (None, 0, -1, math.nan, math.inf, '2e8', True):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                check_calculation(next(iter(MEDIA)), answer)

    def test_inclusive_tolerance_and_absolute_difference(self):
        for medium, n in MEDIA.items():
            reference = light_speed(n)
            for factor, correct in ((1, True), (.995, True), (1.005, True), (.99499, False), (1.00501, False)):
                with self.subTest(medium=medium, factor=factor):
                    result = check_calculation(medium, reference * factor)
                    self.assertEqual(result['correct'], correct)
                    self.assertAlmostEqual(result['error'], abs(factor - 1) * 100)
                    self.assertGreaterEqual(result['difference'], 0)

    def test_pending_answers_hidden_and_summary_uses_latest(self):
        self.assertEqual(summarize({}), (0, 0, None))
        results = {}
        for row in experiment_rows(results):
            self.assertIsNone(row['ความเร็วจาก Simulation (m/s)'])
        medium = next(iter(MEDIA))
        results[medium] = check_calculation(medium, light_speed(MEDIA[medium]) * 1.01)
        self.assertEqual(summarize(results)[:2], (1, 0))
        results[medium] = check_calculation(medium, light_speed(MEDIA[medium]))
        self.assertEqual(summarize(results), (1, 1, 0))
        rows = experiment_rows(results)
        self.assertIsNotNone(rows[0]['ความเร็วจาก Simulation (m/s)'])
        self.assertTrue(all(row['ความเร็วจาก Simulation (m/s)'] is None for row in rows[1:]))


if __name__ == '__main__':
    unittest.main()
