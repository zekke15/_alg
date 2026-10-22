# -*- coding: utf-8 -*-
"""執行：py -m unittest -v test_grep.py"""
import random
import unittest
from main import dp_search, nfa_search, grep_lines


class GrepTest(unittest.TestCase):
    def test_examples(self):
        cases = [
            ('abbc', 'ab*c', True), ('ac', 'ab*c', True),
            ('abc', 'ab*c', True), ('abbbc', 'ab*c', True),
            ('axc', 'ab*c', False), ('cat', 'c.t', True),
            ('cut', 'c.t', True), ('dog', 'c.t', False),
            ('hello world', 'world', True), ('abcabc', 'bc', True),
            ('zzz', 'a*', True), ('', 'a*', True),
            ('', 'a', False), ('abc', '', True),
            ('ab', 'a*b*', True), ('xxabbbcyy', 'ab*c', True),
            ('aaaab', 'a*b', True), ('x', '.*', True),
            ('你好世界', '世界', True),
        ]
        for text, pattern, expected in cases:
            with self.subTest(text=text, pattern=pattern):
                self.assertEqual(dp_search(text, pattern), expected)
                self.assertEqual(nfa_search(text, pattern), expected)

    def test_grep_lines(self):
        lines = ['cat', 'dog', 'cot', 'cut']
        expected = [(1, 'cat'), (3, 'cot'), (4, 'cut')]
        self.assertEqual(grep_lines(lines, 'c.t', dp_search), expected)
        self.assertEqual(grep_lines(lines, 'c.t', nfa_search), expected)

    def test_invalid_patterns(self):
        for pattern in ['*a', 'a**', '**']:
            with self.subTest(pattern=pattern):
                with self.assertRaises(ValueError):
                    dp_search('abc', pattern)
                with self.assertRaises(ValueError):
                    nfa_search('abc', pattern)

    def test_random_consistency(self):
        random.seed(2026)
        for _ in range(300):
            text = ''.join(random.choices('ab', k=random.randint(0, 10)))
            pattern = ''.join(
                c + ('*' if random.random() < 0.35 else '')
                for c in random.choices('ab.', k=random.randint(0, 5))
            )
            with self.subTest(text=text, pattern=pattern):
                self.assertEqual(dp_search(text, pattern), nfa_search(text, pattern))


if __name__ == '__main__':
    unittest.main(verbosity=2)
