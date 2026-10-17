# -*- coding: utf-8 -*-
"""Automated tests for the Lambda Calculus interpreter.
Run: py -m unittest -v test_lambda_calculus.py
"""
import unittest

from lambda_calculus import (Abs, App, Var, all_names, find_leftmost_outermost_redex,
                             free_vars, normalize, parse, pretty, reduce_once)


class ParserTests(unittest.TestCase):
    def test_var(self):
        self.assertEqual(parse("hello"), Var("hello"))

    def test_lambda_unicode_and_backslash(self):
        self.assertEqual(parse("λx.x"), parse(r"\x.x"))

    def test_curried_params(self):
        self.assertEqual(parse(r"\x y.x"), parse(r"\x.\y.x"))

    def test_application_left_associative(self):
        self.assertEqual(parse("a b c"), App(App(Var("a"), Var("b")), Var("c")))

    def test_application_parentheses(self):
        self.assertEqual(parse("a (b c)"), App(Var("a"), App(Var("b"), Var("c"))))

    def test_syntax_errors(self):
        for source in ("", "(", r"\x x", ")", "a + b", r"\x."):
            with self.subTest(source=source), self.assertRaises(SyntaxError):
                parse(source)

    def test_pretty_parser_round_trip(self):
        expressions = (
            r"(\x.x) a", r"\x.\y.x", r"\x.(a b) (c d)",
            r"f ((\y.y) z)", r"(\a.(\b.b) a) (\x.x)",
        )
        for expression in expressions:
            with self.subTest(expression=expression):
                ast = parse(expression)
                self.assertEqual(parse(pretty(ast)), ast)
                self.assertEqual(parse(pretty(ast, ascii_lambda=True)), ast)


class ReductionTests(unittest.TestCase):
    def get_result(self, source, limit=100):
        term, steps, complete = normalize(parse(source), limit)
        return pretty(term), steps, complete

    def test_identity(self):
        result, steps, complete = self.get_result(r"(\x.x) a")
        self.assertEqual(result, "a")
        self.assertEqual([s.kind for s in steps], ["beta"])
        self.assertTrue(complete)

    def test_constant_two_steps(self):
        result, steps, complete = self.get_result(r"((\x.\y.x) a) b")
        self.assertEqual(result, "a")
        self.assertEqual([s.kind for s in steps], ["beta", "beta"])
        self.assertTrue(complete)

    def test_shadowing(self):
        result, steps, complete = self.get_result(r"(\x.\x.x) a")
        self.assertEqual(result, "λx.x")
        self.assertEqual([s.kind for s in steps], ["beta"])
        self.assertTrue(complete)

    def test_capture_avoidance(self):
        result, steps, complete = self.get_result(r"(\x.\y.x) y")
        self.assertEqual(result, "λy_1.y")
        self.assertEqual([s.kind for s in steps], ["alpha", "beta"])
        self.assertTrue(complete)

    def test_no_unnecessary_alpha(self):
        result, steps, complete = self.get_result(r"(\x.\y.y) y")
        self.assertEqual(result, "λy.y")
        self.assertEqual([s.kind for s in steps], ["beta"])
        self.assertTrue(complete)

    def test_alpha_fresh_name_not_colliding(self):
        result, steps, complete = self.get_result(r"(\x.\y.x y) (y_1 y)")
        # First redex must rename y, but 'y_1' is already used in the full term.
        self.assertEqual(steps[0].kind, "alpha")
        self.assertIn("λy_2", pretty(steps[0].after))
        self.assertTrue(complete)
        self.assertEqual(result, "λy_2.y_1 y y_2")

    def test_two_alpha_conversions_both_visible(self):
        result, steps, complete = self.get_result(r"(\x.\y.\z.x y z) (y z)")
        self.assertEqual([s.kind for s in steps], ["alpha", "alpha", "beta"])
        self.assertEqual(result, "λy_1.λz_1.y z y_1 z_1")
        self.assertTrue(complete)

    def test_church_true_false(self):
        true, _, _ = self.get_result(r"((\x.\y.x) YES) NO")
        false, _, _ = self.get_result(r"((\x.\y.y) YES) NO")
        self.assertEqual(true, "YES")
        self.assertEqual(false, "NO")

    def test_church_not_true(self):
        result, steps, complete = self.get_result(
            r"(\p.p (\a.\b.b) (\a.\b.a)) (\x.\y.x)")
        self.assertEqual(result, "λa.λb.b")
        self.assertTrue(complete)
        self.assertGreaterEqual(len(steps), 3)

    def test_under_abstraction(self):
        result, steps, complete = self.get_result(r"\a.(\x.x) a")
        self.assertEqual(result, "λa.a")
        self.assertTrue(complete)
        self.assertEqual(len(steps), 1)

    def test_normal_order_discards_diverging_argument(self):
        result, steps, complete = self.get_result(
            r"(\x.OK) ((\z.z z) (\z.z z))", limit=10)
        self.assertEqual(result, "OK")
        self.assertEqual(len(steps), 1)
        self.assertTrue(complete)

    def test_diverging_omega_hits_limit(self):
        source = r"(\x.x x) (\x.x x)"
        result, steps, complete = self.get_result(source, limit=7)
        self.assertFalse(complete)
        self.assertEqual(len(steps), 7)
        self.assertEqual(result, pretty(parse(source)))

    def test_normal_form_has_zero_steps(self):
        result, steps, complete = self.get_result(r"\x.x", limit=0)
        self.assertEqual(result, "λx.x")
        self.assertTrue(complete)
        self.assertEqual(steps, [])

    def test_free_vars(self):
        self.assertEqual(free_vars(parse(r"\x.x y")), {"y"})
        self.assertEqual(all_names(parse(r"\x.x y")), {"x", "y"})

    def test_reduction_trace_is_one_change_per_step(self):
        term = parse(r"(\x.\y.x) y")
        step1 = reduce_once(term)
        self.assertIsNotNone(step1)
        self.assertEqual(step1.before, term)
        self.assertEqual(step1.kind, "alpha")
        step2 = reduce_once(step1.after)
        self.assertIsNotNone(step2)
        self.assertEqual(step2.kind, "beta")
        self.assertIsNone(find_leftmost_outermost_redex(step2.after))


if __name__ == "__main__":
    unittest.main(verbosity=2)
