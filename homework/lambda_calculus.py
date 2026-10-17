# -*- coding: utf-8 -*-
"""Lambda Calculus interpreter: named variables, capture-avoiding substitution,
and a COMPLETE trace of alpha-conversions and beta-reductions.

Python 3.10+. No third-party packages.

Run:
    py lambda_calculus.py
    py lambda_calculus.py --expr "(\\x.x) a"
    py lambda_calculus.py --example 4
    py lambda_calculus.py --expr "(\\x.\\y.x) y" --ascii
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from typing import Optional, Union


# --------------------------- Abstract Syntax Tree -------------------------- #
@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Abs:
    param: str
    body: Term


@dataclass(frozen=True)
class App:
    fn: Term
    arg: Term


Term = Union[Var, Abs, App]


# ------------------------------- Tokenizer -------------------------------- #
@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    position: int


TOKEN_RE = re.compile(r"[A-Za-z_][A-Za-z_0-9]*|[λ\\.()]|\s+", re.UNICODE)


def tokenize(source: str) -> list[Token]:
    tokens: list[Token] = []
    pos = 0
    while pos < len(source):
        match = TOKEN_RE.match(source, pos)
        if match is None:
            raise SyntaxError(f"Unsupported character {source[pos]!r} at position {pos + 1}")
        value = match.group(0)
        if not value.isspace():
            kinds = {"λ": "LAMBDA", "\\": "LAMBDA", ".": "DOT",
                     "(": "LPAREN", ")": "RPAREN"}
            tokens.append(Token(kinds.get(value, "NAME"), value, pos))
        pos = match.end()
    tokens.append(Token("EOF", "", len(source)))
    return tokens


class Parser:
    def __init__(self, source: str):
        self.tokens = tokenize(source)
        self.index = 0

    def current(self) -> Token:
        return self.tokens[self.index]

    def accept(self, kind: str) -> Optional[Token]:
        if self.current().kind == kind:
            token = self.current()
            self.index += 1
            return token
        return None

    def expect(self, kind: str, explanation: str) -> Token:
        token = self.accept(kind)
        if token is None:
            found = self.current().value or "end of expression"
            raise SyntaxError(f"Expected {explanation} at position "
                              f"{self.current().position + 1}, found {found!r}")
        return token

    def parse(self) -> Term:
        if self.current().kind == "EOF":
            raise SyntaxError("The Lambda expression is empty")
        result = self.parse_expression()
        self.expect("EOF", "end of expression")
        return result

    def parse_expression(self) -> Term:
        if self.accept("LAMBDA"):
            parameters: list[str] = []
            parameters.append(self.expect("NAME", "parameter name after λ").value)
            while self.current().kind == "NAME":
                parameters.append(self.accept("NAME").value)
            self.expect("DOT", "'.' after the parameter(s)")
            body = self.parse_expression()
            for name in reversed(parameters):
                body = Abs(name, body)
            return body
        return self.parse_application()

    def parse_application(self) -> Term:
        result = self.parse_atom()
        while self.current().kind in ("NAME", "LPAREN"):
            result = App(result, self.parse_atom())
        return result

    def parse_atom(self) -> Term:
        token = self.accept("NAME")
        if token is not None:
            return Var(token.value)
        if self.accept("LPAREN"):
            expression = self.parse_expression()
            self.expect("RPAREN", "')'")
            return expression
        found = self.current().value or "end of expression"
        raise SyntaxError(f"Expected a variable or '(' at position "
                          f"{self.current().position + 1}, found {found!r}")


def parse(source: str) -> Term:
    return Parser(source).parse()


# ------------------------------- Formatting ------------------------------- #
def pretty(term: Term, ascii_lambda: bool = False) -> str:
    lam = "\\" if ascii_lambda else "λ"
    if isinstance(term, Var):
        return term.name
    if isinstance(term, Abs):
        return f"{lam}{term.param}.{pretty(term.body, ascii_lambda)}"
    left = pretty(term.fn, ascii_lambda)
    right = pretty(term.arg, ascii_lambda)
    if isinstance(term.fn, Abs):
        left = f"({left})"
    if isinstance(term.arg, (Abs, App)):
        right = f"({right})"
    return f"{left} {right}"


# --------------------------- Free/Bound Variables ------------------------- #
def free_vars(term: Term) -> set[str]:
    if isinstance(term, Var):
        return {term.name}
    if isinstance(term, Abs):
        return free_vars(term.body) - {term.param}
    return free_vars(term.fn) | free_vars(term.arg)


def all_names(term: Term) -> set[str]:
    if isinstance(term, Var):
        return {term.name}
    if isinstance(term, Abs):
        return {term.param} | all_names(term.body)
    return all_names(term.fn) | all_names(term.arg)


def fresh_name(base: str, unavailable: set[str]) -> str:
    index = 1
    while f"{base}_{index}" in unavailable:
        index += 1
    return f"{base}_{index}"


def rename_bound_occurrences(term: Term, old: str, new: str) -> Term:
    """Rename uses of an outer binder, leaving inner binders of old untouched."""
    if isinstance(term, Var):
        return Var(new) if term.name == old else term
    if isinstance(term, App):
        return App(rename_bound_occurrences(term.fn, old, new),
                   rename_bound_occurrences(term.arg, old, new))
    if term.param == old:
        return term  # this nested lambda shadows the outer binder
    return Abs(term.param, rename_bound_occurrences(term.body, old, new))


def first_required_alpha(term: Term, target: str, argument: Term,
                         unavailable: set[str]) -> Optional[tuple[Term, str, str]]:
    """Prepare *one* visible α-conversion, before β-substitution.

    The return value is (new_term, old_name, fresh_name). Returning only one
    change is intentional: each alpha conversion is shown as its own step.
    """
    if isinstance(term, Var):
        return None
    if isinstance(term, App):
        changed = first_required_alpha(term.fn, target, argument, unavailable)
        if changed is not None:
            new_fn, old, new = changed
            return App(new_fn, term.arg), old, new
        changed = first_required_alpha(term.arg, target, argument, unavailable)
        if changed is not None:
            new_arg, old, new = changed
            return App(term.fn, new_arg), old, new
        return None

    if term.param == target:
        return None  # substitution must not enter a lambda that rebinds target
    if term.param in free_vars(argument) and target in free_vars(term.body):
        new = fresh_name(term.param, unavailable)
        renamed = rename_bound_occurrences(term.body, term.param, new)
        return Abs(new, renamed), term.param, new
    changed = first_required_alpha(term.body, target, argument, unavailable)
    if changed is None:
        return None
    new_body, old, new = changed
    return Abs(term.param, new_body), old, new


def substitute_safe_after_alpha(term: Term, target: str, argument: Term) -> Term:
    """Substitute once ALL required alpha-renamings have been handled."""
    if isinstance(term, Var):
        return argument if term.name == target else term
    if isinstance(term, App):
        return App(substitute_safe_after_alpha(term.fn, target, argument),
                   substitute_safe_after_alpha(term.arg, target, argument))
    if term.param == target:
        return term
    return Abs(term.param, substitute_safe_after_alpha(term.body, target, argument))


# ---------------------------- Reduction Engine ---------------------------- #
# Each path element describes a child of the current AST node.
Path = tuple[str, ...]


def find_leftmost_outermost_redex(term: Term, path: Path = ()) -> Optional[Path]:
    """Full normal order: leftmost-outermost, including inside lambda bodies."""
    if isinstance(term, App):
        if isinstance(term.fn, Abs):
            return path
        left = find_leftmost_outermost_redex(term.fn, path + ("fn",))
        if left is not None:
            return left
        return find_leftmost_outermost_redex(term.arg, path + ("arg",))
    if isinstance(term, Abs):
        return find_leftmost_outermost_redex(term.body, path + ("body",))
    return None


def node_at(term: Term, path: Path) -> Term:
    for component in path:
        term = getattr(term, component)
    return term


def replace_at(term: Term, path: Path, replacement: Term) -> Term:
    if not path:
        return replacement
    head, *tail = path
    rest = tuple(tail)
    if isinstance(term, Abs) and head == "body":
        return Abs(term.param, replace_at(term.body, rest, replacement))
    if isinstance(term, App):
        if head == "fn":
            return App(replace_at(term.fn, rest, replacement), term.arg)
        if head == "arg":
            return App(term.fn, replace_at(term.arg, rest, replacement))
    raise ValueError(f"Invalid reduction path: {path}")


@dataclass(frozen=True)
class ReductionStep:
    kind: str  # 'alpha' or 'beta'
    before: Term
    after: Term
    explanation: str


def reduce_once(term: Term) -> Optional[ReductionStep]:
    path = find_leftmost_outermost_redex(term)
    if path is None:
        return None
    redex = node_at(term, path)
    assert isinstance(redex, App) and isinstance(redex.fn, Abs)
    function, argument = redex.fn, redex.arg

    alpha = first_required_alpha(function.body, function.param,
                                 argument, all_names(term))
    if alpha is not None:
        changed_body, old, new = alpha
        changed_redex = App(Abs(function.param, changed_body), argument)
        updated = replace_at(term, path, changed_redex)
        return ReductionStep(
            "alpha", term, updated,
            f"Rename bound variable {old} -> {new} to avoid variable capture")

    contracted = substitute_safe_after_alpha(function.body, function.param,
                                             argument)
    updated = replace_at(term, path, contracted)
    return ReductionStep("beta", term, updated,
                         f"Replace free occurrences of {function.param} in the "
                         "function body with its argument")


def normalize(term: Term, max_steps: int = 100) -> tuple[Term, list[ReductionStep], bool]:
    if max_steps < 0:
        raise ValueError("max_steps must be nonnegative")
    steps: list[ReductionStep] = []
    current = term
    for _ in range(max_steps):
        step = reduce_once(current)
        if step is None:
            return current, steps, True
        steps.append(step)
        current = step.after
    return current, steps, find_leftmost_outermost_redex(current) is None


def show_trace(source: str, max_steps: int = 100,
               ascii_lambda: bool = False) -> bool:
    term = parse(source)
    final, steps, completed = normalize(term, max_steps)
    print("=" * 64)
    print("LAMBDA CALCULUS INTERPRETER — Normal Order")
    print("=" * 64)
    print(f"Input : {source}")
    print(f"Step 0 [start] : {pretty(term, ascii_lambda)}")
    for index, step in enumerate(steps, 1):
        print(f"Step {index} [{step.kind}] : {pretty(step.after, ascii_lambda)}")
        print(f"         Reason: {step.explanation}")
    print("-" * 64)
    print(f"Result      : {pretty(final, ascii_lambda)}")
    print(f"Alpha steps : {sum(step.kind == 'alpha' for step in steps)}")
    print(f"Beta steps  : {sum(step.kind == 'beta' for step in steps)}")
    print(f"Total steps : {len(steps)}")
    print("Status      : NORMAL FORM" if completed else
          f"Status      : STEP LIMIT REACHED ({max_steps}); not a normal form")
    print("=" * 64)
    return completed


# ---------------------------- Input Examples ------------------------------ #
# The examples deliberately use ASCII backslashes for easy Windows typing.
EXAMPLES: list[tuple[str, str]] = [
    ("Identity: (λx.x) a", r"(\x.x) a"),
    ("Two-argument constant function", r"((\x.\y.x) a) b"),
    ("Shadowed variable", r"(\x.\x.x) a"),
    ("Alpha-renaming prevents variable capture", r"(\x.\y.x) y"),
    ("Church TRUE chooses first argument", r"((\x.\y.x) YES) NO"),
    ("Church FALSE chooses second argument", r"((\x.\y.y) YES) NO"),
    ("Normalizing under a lambda", r"(\f.\x.f x) (\z.z)"),
    ("Church NOT TRUE becomes FALSE", r"(\p.p (\a.\b.b) (\a.\b.a)) (\x.\y.x)"),
    ("Nonterminating Omega: step limit", r"(\x.x x) (\x.x x)"),
    ("Nested capture avoidance", r"(\x.\y.x y) y"),
]


def print_examples() -> None:
    for index, (description, source) in enumerate(EXAMPLES, 1):
        print(f"{index:>2}. {description}\n    {source}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Lambda Calculus interpreter with full step trace")
    ap.add_argument("--expr", help=r"Expression, e.g. '(\x.x) a'")
    ap.add_argument("--example", type=int, help="Run a built-in example (1–10)")
    ap.add_argument("--list", action="store_true", help="Show the built-in examples")
    ap.add_argument("--max-steps", type=int, default=100, help="Alpha+beta step cap (default: 100)")
    ap.add_argument("--ascii", action="store_true", help=r"Print \ instead of λ")
    args = ap.parse_args()
    if args.max_steps <= 0:
        ap.error("--max-steps must be greater than zero")
    if args.list:
        print_examples()
        return 0
    if args.expr is not None and args.example is not None:
        ap.error("Choose either --expr or --example, not both")
    if args.example is not None:
        if not (1 <= args.example <= len(EXAMPLES)):
            ap.error(f"--example must be between 1 and {len(EXAMPLES)}")
        expression = EXAMPLES[args.example - 1][1]
    elif args.expr is not None:
        expression = args.expr
    else:
        print("Lambda Calculus interpreter (named variables, normal order)")
        print("Input: (\\x.x) a   or   (λx.x) a")
        print("Use parentheses around a lambda when applying it.")
        print("Examples:")
        print_examples()
        print(" 0. Enter your own expression")
        try:
            choice = input("Choose 0–10 (Enter = 1, q = quit): ").strip().lower()
            if choice == "q":
                return 0
            if choice in ("", "1"):
                expression = EXAMPLES[0][1]
            elif choice == "0":
                expression = input("Expression: ").strip()
            elif choice.isdigit() and 1 <= int(choice) <= len(EXAMPLES):
                expression = EXAMPLES[int(choice) - 1][1]
            else:
                print("Invalid choice")
                return 2
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled")
            return 0
    try:
        complete = show_trace(expression, args.max_steps, args.ascii)
        return 0 if complete else 3
    except (SyntaxError, RecursionError) as exc:
        print(f"Input error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
