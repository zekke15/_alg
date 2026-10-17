# -*- coding: utf-8 -*-
"""自動測試三題；執行 py test_homework.py。"""
import ast
import math
import unittest
from pathlib import Path

from hanoi import hanoi_recursive, hanoi_iterative
from sym_diff import sym_diff
from functional_bubble import (
    my_map, my_filter, my_reduce, bubble_sort, is_sorted
)


class HanoiTests(unittest.TestCase):
    def test_same_steps_and_legality(self):
        for n in range(8):
            recursive = hanoi_recursive(n)
            iterative = hanoi_iterative(n)
            self.assertEqual(recursive, iterative)
            self.assertEqual(len(recursive), 2**n - 1)
            pegs = {"A": list(range(n, 0, -1)), "B": [], "C": []}
            for disk, origin, destination in recursive:
                self.assertEqual(pegs[origin][-1], disk)
                pegs[origin].pop()
                if pegs[destination]:
                    self.assertGreater(pegs[destination][-1], disk)
                pegs[destination].append(disk)
            self.assertEqual(pegs["C"], list(range(n, 0, -1)))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            hanoi_recursive(-1)
        with self.assertRaises(ValueError):
            hanoi_iterative(-1)


class SymbolicDifferentiationTests(unittest.TestCase):
    @staticmethod
    def evaluate(formula, x):
        return eval(formula, {"__builtins__": {}, "sin": math.sin,
                              "cos": math.cos, "exp": math.exp,
                              "log": math.log}, {"x": x})

    def test_known_outputs(self):
        self.assertEqual(sym_diff("x**3 + 2*x + 5"), "3 * x ** 2 + 2")
        self.assertEqual(sym_diff("2*x + 8"), "2")
        self.assertEqual(sym_diff("5"), "0")
        self.assertEqual(sym_diff("x"), "1")
        self.assertEqual(sym_diff("x**0"), "0")

    def test_derivatives_numerically(self):
        expressions = ["x**3 + 2*x + 5", "(x+1)**3", "x**2/(x+1)",
                       "sin(x**2)", "cos(x)", "exp(x)", "log(x)", "-x + x/2"]
        for expr in expressions:
            derivative = sym_diff(expr)
            x = 1.6
            h = 1e-6
            approx = (self.evaluate(expr, x + h) - self.evaluate(expr, x - h)) / (2 * h)
            exact = self.evaluate(derivative, x)
            self.assertAlmostEqual(approx, exact, places=5, msg=expr)

    def test_unsupported(self):
        with self.assertRaises(ValueError):
            sym_diff("x**x")
        with self.assertRaises(ValueError):
            sym_diff("unknown_func(x)")


class FunctionalBubbleTests(unittest.TestCase):
    def test_custom_functions(self):
        self.assertEqual(my_map(lambda n: n*n, [2, 3]), [4, 9])
        self.assertEqual(my_filter(lambda n: n % 2 == 0, [1, 2, 3, 4]), [2, 4])
        self.assertEqual(my_reduce(lambda a, b: a + b, [1, 2, 3], 0), 6)
        self.assertEqual(my_reduce(lambda a, b: a + b, [], 10), 10)

    def test_sort_cases(self):
        cases = [[], [1], [3, 2, 1], [1, 2, 3], [5, 1, 4, 2, 8, 2],
                 [-3, 0, -1, -3], [2, 2, 2, 2]]
        for values in cases:
            original = values[:]
            result = bubble_sort(values)
            self.assertEqual(result, sorted(values))
            self.assertEqual(values, original)
            self.assertTrue(is_sorted(result))

    def test_no_loop_or_builtin_functions(self):
        path = Path(__file__).with_name("functional_bubble.py")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        prohibited = (ast.For, ast.AsyncFor, ast.While, ast.ListComp,
                      ast.SetComp, ast.DictComp, ast.GeneratorExp)
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, prohibited)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                self.assertNotIn(node.func.id, {"map", "filter", "reduce", "sorted", "sort"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
