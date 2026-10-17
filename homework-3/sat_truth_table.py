# -*- coding: utf-8 -*-
"""使用暴力列舉真值表來求解 CNF 形式的 SAT 問題。

CNF 格式：外層列表代表 AND，各內層列表代表 OR。
變數名稱例如 "A"；否定變數以驚嘆號開頭，例如 "!A"。
"""

from itertools import product


def get_variables(clauses):
    """取得公式的所有變數並檢查輸入格式。"""
    if not isinstance(clauses, (list, tuple)):
        raise TypeError("公式必須由列表或元組組成")

    variables = set()
    for clause in clauses:
        if not isinstance(clause, (list, tuple)):
            raise TypeError("每個子句必須是列表或元組")
        for literal in clause:
            if not isinstance(literal, str):
                raise TypeError("文字項必須是字串")
            name = literal[1:] if literal.startswith("!") else literal
            if not name or name.startswith("!") or not name.isidentifier():
                raise ValueError(f"無效的變數或文字項：{literal!r}")
            variables.add(name)
    return sorted(variables)


def evaluate_formula(clauses, assignment):
    """代入指定變數設定，計算整個 CNF 公式的真假。"""
    return all(
        any(
            (not assignment[literal[1:]])
            if literal.startswith("!")
            else assignment[literal]
            for literal in clause
        )
        for clause in clauses
    )


def enumerate_truth_table(clauses):
    """回傳 (變數名稱列表, 真值表資料列, 滿足條件的所有解)。"""
    variables = get_variables(clauses)
    rows = []
    solutions = []

    for values in product((False, True), repeat=len(variables)):
        assignment = dict(zip(variables, values))
        result = evaluate_formula(clauses, assignment)
        rows.append((assignment, result))
        if result:
            solutions.append(assignment)

    return variables, rows, solutions


def solve_sat(clauses):
    """列印完整真值表，並回傳滿足條件的所有解。"""
    variables, rows, solutions = enumerate_truth_table(clauses)

    headers = variables + ["F"]
    print("SAT 真值表")
    print(" | ".join(headers))
    print("-" * (4 * len(headers) - 1))

    for assignment, result in rows:
        cells = ["1" if assignment[name] else "0" for name in variables]
        cells.append("1" if result else "0")
        print(" | ".join(cells))

    print("\nSAT 判斷結果：")
    if solutions:
        print("SAT：存在滿足條件的解")
        print("符合條件的組合數：", len(solutions))
        for assignment in solutions:
            print(assignment)
    else:
        print("UNSAT：不存在滿足條件的解")

    return solutions


if __name__ == "__main__":
    # F = (A OR B) AND (NOT A OR C)
    formula = [
        ["A", "B"],
        ["!A", "C"],
    ]
    solve_sat(formula)
