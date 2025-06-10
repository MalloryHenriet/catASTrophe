import re
import ast
import operator as op

# Supported operators (excluding division)
SAFE_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Pow: op.pow,
    ast.Mod: op.mod,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def contains_division(node):
    if isinstance(node, ast.BinOp):
        if isinstance(node.op, ast.Div):
            return True
        return contains_division(node.left) or contains_division(node.right)
    elif isinstance(node, ast.UnaryOp):
        return contains_division(node.operand)
    return False

def safe_eval_expr(expr: str):
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
            return SAFE_OPERATORS[type(node.op)](_eval(node.operand))
        elif isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
            return SAFE_OPERATORS[type(node.op)](_eval(node.left), _eval(node.right))
        else:
            raise ValueError("Unsupported expression")

    try:
        parsed = ast.parse(expr, mode='eval').body
        if contains_division(parsed):
            return None
        return _eval(parsed)
    except Exception:
        return None

def strip_outer_parens(expr: str) -> str:
    while expr.startswith('(') and expr.endswith(')'):
        inner = expr[1:-1].strip()
        if inner.count('(') == inner.count(')'):
            expr = inner
        else:
            break
    return expr

def simplify_sql_numeric_exprs(sql: str) -> str:
    def replace_arith(match):
        expr = match.group(0)
        inner = strip_outer_parens(expr)

        result = safe_eval_expr(inner)
        if result is not None:
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)

        cleaned = re.sub(r'(?<![\d\)])\+\s*', '', inner)
        return f'({cleaned})'

    pattern = re.compile(r'\((?:[^\(\)]*|\([^()]*\))*\)')
    prev_sql = None
    while sql != prev_sql:
        prev_sql = sql
        sql = pattern.sub(replace_arith, sql)
    return sql

# Example SQL
sql_input = """
CREATE TABLE F (p BOOLEAN NOT NULL NULL NOT NULL, i BOOLEAN);
INSERT INTO F SELECT * FROM (VALUES ((NOT false), false), (NULL, (NOT (NOT true)))) AS L WHERE (((+(+(-((+110) / (+((-(-150)) * ((247 * (91 * (-47))) + (-86)))))))) = ((((+(+(24 / (+((+89) * (+58)))))) * (-(-((193 + 223) / (-(222 / 219)))))) * (34 * 70)) * (+(+((((+(+(-202))) / (+52)) - (-(228 + (-104)))) * (-24)))))) = (false <> (66 <> 8)));
"""

# Run the simplifier
print(simplify_sql_numeric_exprs(sql_input))
