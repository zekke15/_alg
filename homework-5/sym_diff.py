# -*- coding: utf-8 -*-
"""第五週第二題：使用 AST 和遞迴進行符號微分（無須第三方套件）。"""

import ast


def _constant(value):
    return ast.Constant(value=value)


def _numeric_value(node):
    """只辨識數字常數及數字常數的正負號。"""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _numeric_value(node.operand)
        if value is not None:
            return -value if isinstance(node.op, ast.USub) else value
    return None


def _is(node, number):
    return _numeric_value(node) == number


def _neg(a):
    value = _numeric_value(a)
    if value is not None:
        return _constant(-value)
    return ast.UnaryOp(op=ast.USub(), operand=a)


def _add(a, b):
    if _is(a, 0):
        return b
    if _is(b, 0):
        return a
    x, y = _numeric_value(a), _numeric_value(b)
    if x is not None and y is not None:
        return _constant(x + y)
    return ast.BinOp(left=a, op=ast.Add(), right=b)


def _sub(a, b):
    if _is(b, 0):
        return a
    if _is(a, 0):
        return _neg(b)
    x, y = _numeric_value(a), _numeric_value(b)
    if x is not None and y is not None:
        return _constant(x - y)
    return ast.BinOp(left=a, op=ast.Sub(), right=b)


def _mul(a, b):
    if _is(a, 0) or _is(b, 0):
        return _constant(0)
    if _is(a, 1):
        return b
    if _is(b, 1):
        return a
    x, y = _numeric_value(a), _numeric_value(b)
    if x is not None and y is not None:
        return _constant(x * y)
    return ast.BinOp(left=a, op=ast.Mult(), right=b)


def _div(a, b):
    if _is(a, 0):
        return _constant(0)
    if _is(b, 1):
        return a
    return ast.BinOp(left=a, op=ast.Div(), right=b)


def _pow(a, b):
    if _is(b, 0):
        return _constant(1)
    if _is(b, 1):
        return a
    return ast.BinOp(left=a, op=ast.Pow(), right=b)


def _call(function_name, argument):
    return ast.Call(func=ast.Name(id=function_name, ctx=ast.Load()),
                    args=[argument], keywords=[])


def _differentiate(node, variable):
    """每一層語法樹節點都遞迴套用微分規則。"""
    if isinstance(node, ast.Constant):
        if _numeric_value(node) is None:
            raise ValueError("只支援數值常數")
        return _constant(0)

    if isinstance(node, ast.Name):
        return _constant(1 if node.id == variable else 0)

    if isinstance(node, ast.UnaryOp):
        derivative = _differentiate(node.operand, variable)
        if isinstance(node.op, ast.UAdd):
            return derivative
        if isinstance(node.op, ast.USub):
            return _neg(derivative)
        raise ValueError("不支援此一元運算")

    if isinstance(node, ast.BinOp):
        left, right = node.left, node.right
        dl = _differentiate(left, variable)
        dr = _differentiate(right, variable)

        if isinstance(node.op, ast.Add):
            return _add(dl, dr)
        if isinstance(node.op, ast.Sub):
            return _sub(dl, dr)
        if isinstance(node.op, ast.Mult):
            return _add(_mul(dl, right), _mul(left, dr))
        if isinstance(node.op, ast.Div):
            numerator = _sub(_mul(dl, right), _mul(left, dr))
            return _div(numerator, _pow(right, _constant(2)))
        if isinstance(node.op, ast.Pow):
            n = _numeric_value(right)
            if n is None:
                raise ValueError("次方指數須為數字常數，例如 x**3；不支援 x**x")
            if n == 0:
                return _constant(0)
            return _mul(_mul(_constant(n), _pow(left, _constant(n - 1))), dl)
        raise ValueError("只支援 +、-、*、/、**")

    # 另外支援四種常見函數，套用鏈鎖律。
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and len(node.args) == 1 and not node.keywords:
        function_name = node.func.id
        argument = node.args[0]
        darg = _differentiate(argument, variable)
        if function_name == "sin":
            return _mul(_call("cos", argument), darg)
        if function_name == "cos":
            return _mul(_neg(_call("sin", argument)), darg)
        if function_name == "exp":
            return _mul(_call("exp", argument), darg)
        if function_name == "log":
            return _div(darg, argument)

    raise ValueError("不支援此數學式；請使用數字、變數、四則運算、常數次方或 sin/cos/exp/log")


def sym_diff(expr, variable="x"):
    """將 Python 形式的數學式對 variable 微分，回傳可讀的式子。"""
    if not isinstance(expr, str) or not expr.strip():
        raise ValueError("expr 必須是非空字串")
    if not isinstance(variable, str) or not variable.isidentifier():
        raise ValueError("variable 必須是變數名稱")
    tree = ast.parse(expr, mode="eval")
    result = _differentiate(tree.body, variable)
    return ast.unparse(ast.fix_missing_locations(result))


if __name__ == "__main__":
    examples = ["x**3 + 2*x + 5", "(x+1)**3", "x**2 / (x+1)",
                "sin(x)", "cos(x)", "exp(x)", "log(x)"]
    for expression in examples:
        print(f"f(x)  = {expression}")
        print(f"f'(x) = {sym_diff(expression)}\n")
