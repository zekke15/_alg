def sym_diff(expr, var='x'):
 
    if isinstance(expr, (int, float)):
        return 0
    if isinstance(expr, str):
        return 1 if expr == var else 0

    op = expr[0]
    
    if op == '+':
      
        return ('+', sym_diff(expr[1], var), sym_diff(expr[2], var))
        
    elif op == '-':
    
        return ('-', sym_diff(expr[1], var), sym_diff(expr[2], var))
        
    elif op == '*':
   
        u, v = expr[1], expr[2]
        du = sym_diff(u, var)
        dv = sym_diff(v, var)
        return ('+', ('*', du, v), ('*', u, dv))
        
    elif op == '^':
    
        base, exp = expr[1], expr[2]
        db = sym_diff(base, var)
        return ('*', ('*', exp, ('^', base, exp - 1)), db)
        
    else:
        raise ValueError(f"不支援的運算子: {op}")


expr = ('+', ('^', 'x', 3), ('*', 4, 'x'))
diff_expr = sym_diff(expr, 'x')
print("微分結果語法樹:", diff_expr)
