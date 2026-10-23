# -*- coding: utf-8 -*-
import unittest
from main import t1, t2, t3, t4, formulas


class TestRecurrence(unittest.TestCase):
    def test_formulas(self):
        for n in [1, 2, 4, 8, 16, 32, 64]:
            with self.subTest(n=n):
                self.assertEqual((t1(n), t2(n), t3(n), t4(n)), formulas(n))

    def test_base_cases(self):
        self.assertEqual((t1(1), t2(1), t3(1), t4(1)), (1, 1, 1, 1))

    def test_invalid_inputs(self):
        for f in [t1, t2, t3, t4]:
            with self.assertRaises(ValueError):
                f(0)
        for f in [t3, t4]:
            with self.assertRaises(ValueError):
                f(3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
