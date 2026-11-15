import math
import unittest

from core.optical_power import (
    TEACHING_PROFILES, LENGTH_TRIALS, check_db_answer, check_fiber_trial,
    dbm_to_mw, fiber_loss, mw_to_dbm, output_power, summarize,
)
from core.optical_power_ui import experiment_rows, power_rows


class OpticalPowerTests(unittest.TestCase):
    def test_conversions(self):
        for mw, dbm in [(0.1, -10), (0.5, -3.01029995664), (1, 0), (2, 3.01029995664), (10, 10)]:
            with self.subTest(mw=mw):
                self.assertAlmostEqual(mw_to_dbm(mw), dbm)
                self.assertAlmostEqual(dbm_to_mw(dbm), mw)
        self.assertEqual(dbm_to_mw(0), 1)
        self.assertEqual(mw_to_dbm(1), 0)

    def test_loss_and_output(self):
        for length, loss in zip(LENGTH_TRIALS, (0.2, 1, 2, 3, 4)):
            self.assertAlmostEqual(fiber_loss(0.20, length), loss)
            self.assertAlmostEqual(output_power(0, 0.20, length), -loss)
        self.assertEqual(output_power(3, 0, 20), 3)
        self.assertEqual(output_power(-3, 2, 0), -3)
        self.assertEqual(output_power(10, 0.35, 10), 6.5)

    def test_invalid_inputs(self):
        for value in (None, True, '1', math.nan, math.inf, -math.inf):
            for function in (mw_to_dbm, dbm_to_mw, lambda x: fiber_loss(x, 1),
                             lambda x: fiber_loss(0.2, x), lambda x: output_power(x, 0.2, 1),
                             lambda x: check_db_answer(x, 0)):
                with self.subTest(value=value, function=function), self.assertRaises(ValueError):
                    function(value)
        for value in (0, -1):
            with self.assertRaises(ValueError):
                mw_to_dbm(value)
        for function in (lambda: fiber_loss(-0.2, 10), lambda: fiber_loss(0.2, -1),
                         lambda: fiber_loss(1e308, 10), lambda: dbm_to_mw(10000),
                         lambda: dbm_to_mw(-10000), lambda: check_db_answer(0, 0, -1)):
            with self.assertRaises(ValueError):
                function()

    def test_absolute_tolerance_at_zero_and_negative_dbm(self):
        for reference in (0, -4, 10):
            for delta, correct in ((0, True), (0.1, True), (-0.1, True), (0.10001, False), (-0.10001, False)):
                r = check_db_answer(reference + delta, reference)
                self.assertEqual(r['correct'], correct)
                self.assertAlmostEqual(r['error'], abs(delta))

    def test_all_teaching_profiles(self):
        self.assertEqual(list(TEACHING_PROFILES.values()), [3.0, 0.35, 0.20])
        for profile, alpha in TEACHING_PROFILES.items():
            with self.subTest(profile=profile):
                self.assertAlmostEqual(fiber_loss(alpha, 10), alpha * 10)
                self.assertAlmostEqual(output_power(0, alpha, 10), -alpha * 10)

    def test_fiber_requires_both_answers(self):
        self.assertTrue(check_fiber_trial(5, 1, -1)['correct'])
        self.assertFalse(check_fiber_trial(5, 2, -1)['correct'])
        self.assertFalse(check_fiber_trial(5, 1, 1)['correct'])
        with self.assertRaises(ValueError):
            check_fiber_trial(5, None, -1)

    def test_hidden_rows_and_latest_summary(self):
        self.assertEqual(summarize({}), (0, 0, None))
        for row in experiment_rows({}):
            self.assertEqual(row['Pout จาก Simulation (dBm)'], 'ยังไม่เปิดเผย')
            self.assertNotIn(None, row.values())
        for row in power_rows({}):
            self.assertEqual(row['ค่าอ้างอิง (dBm)'], 'ยังไม่เปิดเผย')
        results = {1: check_fiber_trial(1, 0.2, -0.4)}
        self.assertEqual(summarize(results)[:2], (1, 0))
        results[1] = check_fiber_trial(1, 0.2, -0.2)
        self.assertEqual(summarize(results), (1, 1, 0))
        rows = experiment_rows(results)
        self.assertEqual(rows[0]['Pout จาก Simulation (dBm)'], '-0.200')
        self.assertTrue(all(row['Pout จาก Simulation (dBm)'] == 'ยังไม่เปิดเผย' for row in rows[1:]))


if __name__ == '__main__':
    unittest.main()
