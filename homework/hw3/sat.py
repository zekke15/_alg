import itertools


class TruthTableSATSolver:

    def __init__(self, num_vars: int, clauses: list):
        self.num_vars = num_vars
        self.clauses = clauses
        self.var_names = [f"x{i}" for i in range(1, num_vars + 1)]

    def evaluate_clause(self, clause: list, assignment: dict) -> bool:
        for lit in clause:
            var_idx = abs(lit)
            val = assignment[var_idx]
            if (lit > 0 and val) or (lit < 0 and not val):
                return True
        return False

    def evaluate_formula(self, assignment: dict) -> bool:
        for clause in self.clauses:
            if not self.evaluate_clause(clause, assignment):
                return False
        return True

    def format_formula(self) -> str:
        clause_strs = []
        for c in self.clauses:
            parts = [f"x{lit}" if lit > 0 else f"¬x{abs(lit)}" for lit in c]
            clause_strs.append("(" + " ∨ ".join(parts) + ")")
        return " ∧ ".join(clause_strs)

    def solve(self):
        n = self.num_vars
        formula_str = self.format_formula()
        satisfying_solutions = []

        print(f"\n公式: {formula_str}")
        header = self.var_names + ["| 公式结果"]
        print("  ".join(f"{h:>6}" for h in header))
        print("-" * (8 * len(header)))

        for values in itertools.product([False, True], repeat=n):
            assignment = {i + 1: values[i] for i in range(n)}
            result = self.evaluate_formula(assignment)

            row_str = "  ".join(
                f"{'1' if assignment[i+1] else '0':>6}" for i in range(n)
            )
            print(f"{row_str}  | {'1' if result else '0':>8}")

            if result:
                satisfying_solutions.append(assignment)

        print("-" * (8 * len(header)))

        if satisfying_solutions:
            print(
                f"判定结果: SATISFIABLE (可满足，共有 {len(satisfying_solutions)} 组满足解)"
            )
            print("其中可行解为:")
            for sol in satisfying_solutions:
                sol_desc = ", ".join(
                    f"x{k}={'T' if v else 'F'}" for k, v in sol.items()
                )
                print(f"  [{sol_desc}]")
        else:
            print("判定结果: UNSATISFIABLE (不可满足 / 无解)")

        return satisfying_solutions


if __name__ == "__main__":
    print("=== 测试范例 1 ===")
    solver1 = TruthTableSATSolver(
        num_vars=3, clauses=[[1, -2], [-1, 2, 3], [-1]]
    )
    solver1.solve()

    print("\n" + "=" * 50)

    print("=== 测试范例 2 ===")
    solver2 = TruthTableSATSolver(num_vars=1, clauses=[[1], [-1]])
    solver2.solve()