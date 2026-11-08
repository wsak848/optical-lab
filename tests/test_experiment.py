import math
import unittest

from core.experiment import check_trial, create_trial, summarize


class ExperimentTests(unittest.TestCase):
    def test_record_has_no_student_answer(self):
        trial = create_trial(1000)
        self.assertAlmostEqual(trial['wavelength_m'], 1e-6)
        self.assertAlmostEqual(trial['simulation_thz'], 300)
        for key in ('student_thz', 'difference', 'percent_error', 'correct'):
            self.assertIsNone(trial[key])

    def test_difference_is_absolute_in_both_directions(self):
        for answer in (297, 303):
            result = check_trial(create_trial(1000), answer)
            self.assertAlmostEqual(result['difference'], 3)
            self.assertAlmostEqual(result['percent_error'], 1)
            self.assertFalse(result['correct'])

    def test_tolerance_inclusive_boundary(self):
        for answer, correct in ((300, True), (298.5, True), (301.5, True), (298.49, False)):
            self.assertEqual(check_trial(create_trial(1000), answer)['correct'], correct)

    def test_normal_rounding_accepted(self):
        self.assertTrue(check_trial(create_trial(1310), 229.01)['correct'])

    def test_invalid_answers_rejected(self):
        for answer in (None, 0, -1, math.nan, math.inf, -math.inf):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                check_trial(create_trial(850), answer)

    def test_check_preserves_record_and_does_not_mutate_original(self):
        original = create_trial(850)
        checked = check_trial(original, 352.94)
        self.assertIsNone(original['student_thz'])
        self.assertEqual(checked['wavelength_nm'], 850)
        self.assertEqual(checked['simulation_thz'], original['simulation_thz'])

    def test_summary_excludes_pending_and_counts_latest_answer(self):
        trials = [create_trial(850), check_trial(create_trial(1000), 300),
                  check_trial(create_trial(1000), 303)]
        completed, correct, average = summarize(trials)
        self.assertEqual((completed, correct), (2, 1))
        self.assertAlmostEqual(average, 0.5)
        trials[2] = check_trial(trials[2], 300)
        completed, correct, average = summarize(trials)
        self.assertEqual((completed, correct), (2, 2))
        self.assertAlmostEqual(average, 0)

    def test_empty_summary(self):
        self.assertEqual(summarize([]), (0, 0, None))
