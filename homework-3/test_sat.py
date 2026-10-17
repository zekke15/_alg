# -*- coding: utf-8 -*-
"""以 Python 內建 unittest 測試 SAT 列舉程式。"""

import unittest

from sat_truth_table import enumerate_truth_table, evaluate_formula, get_variables


class TestSatTruthTable(unittest.TestCase):
    def test_three_variables_sat(self):
        formula = [["A", "B"], ["!A", "C"]]
        variables, rows, solutions = enumerate_truth_table(formula)
        self.assertEqual(variables, ["A", "B", "C"])
        self.assertEqual(len(rows), 8)
        self.assertEqual(len(solutions), 4)
        self.assertTrue(all(evaluate_formula(formula, x) for x in solutions))

    def test_unsat(self):
        variables, rows, solutions = enumerate_truth_table([["A"], ["!A"]])
        self.assertEqual(variables, ["A"])
        self.assertEqual(len(rows), 2)
        self.assertEqual(solutions, [])

    def test_simple_or(self):
        _, rows, solutions = enumerate_truth_table([["A", "B"]])
        self.assertEqual(len(rows), 4)
        self.assertEqual(len(solutions), 3)

    def test_tautology(self):
        _, rows, solutions = enumerate_truth_table([["A", "!A"]])
        self.assertEqual(len(rows), 2)
        self.assertEqual(len(solutions), 2)

    def test_empty_formula(self):
        variables, rows, solutions = enumerate_truth_table([])
        self.assertEqual(variables, [])
        self.assertEqual(rows, [({}, True)])
        self.assertEqual(solutions, [{}])

    def test_empty_clause_is_unsat(self):
        variables, rows, solutions = enumerate_truth_table([[]])
        self.assertEqual(variables, [])
        self.assertEqual(rows, [({}, False)])
        self.assertEqual(solutions, [])

    def test_more_variables(self):
        variables, rows, _ = enumerate_truth_table([["D", "A"], ["B", "C"]])
        self.assertEqual(variables, ["A", "B", "C", "D"])
        self.assertEqual(len(rows), 16)

    def test_invalid_literals(self):
        for formula in ([['']], [['!!A']], [[1]]):
            with self.subTest(formula=formula):
                with self.assertRaises((ValueError, TypeError)):
                    get_variables(formula)


if __name__ == "__main__":
    unittest.main()
