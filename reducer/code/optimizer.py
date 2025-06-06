from sqlglot.optimizer import simplify

def expr_simplify(expr):
    try:
        return simplify(expr)
    except Exception as e:
        print(f"Expression simplification error: {e}")
        return e