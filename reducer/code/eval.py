import re
import ast
import operator as op

class InlineArithmeticSimplifier:
    SAFE_OPERATORS = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
        ast.USub: op.neg,
        ast.UAdd: op.pos,
    }

    def __init__(self, validator=None):
        self.validator = validator or (lambda old, new: True)

    def equivalent(self, sql: str) -> str:
        original_sql = sql
        simplified_sql = self._equivalent_inline_arith(sql)

        if self.validator(original_sql, simplified_sql):
            return simplified_sql
        return original_sql

    def _equivalent_inline_arith(self, sql: str) -> str:
        pattern = re.compile(r'\(\s*[\d\+\-\*\%\s]+\s*\)')

        def try_eval(match):
            expr = match.group(0)
            inner = expr[1:-1].strip()
            result = self._safe_eval_expr(inner)

            if result is not None:
                candidate_sql = sql[:match.start()] + result + sql[match.end():]
                if self.validator(sql, candidate_sql):
                    return result
            return expr 

        return pattern.sub(try_eval, sql)

    def _contains_division(self, node):
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Div):
                return True
            return self._contains_division(node.left) or self._contains_division(node.right)
        elif isinstance(node, ast.UnaryOp):
            return self._contains_division(node.operand)
        return False

    def _safe_eval_expr(self, expr: str):
        try:
            parsed = ast.parse(expr, mode='eval').body
            if self._contains_division(parsed):
                return None
            result = self._eval(parsed)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            return str(result)
        except Exception:
            return None

    def _eval(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.UnaryOp) and type(node.op) in self.SAFE_OPERATORS:
            return self.SAFE_OPERATORS[type(node.op)](self._eval(node.operand))
        elif isinstance(node, ast.BinOp) and type(node.op) in self.SAFE_OPERATORS:
            return self.SAFE_OPERATORS[type(node.op)](
                self._eval(node.left), self._eval(node.right))
        else:
            raise ValueError("Unsupported expression")
        


if __name__ == "__main__":
    sql_input = """
    # CREATE TABLE F (p BOOLEAN NOT NULL NULL NOT NULL, i BOOLEAN);
    # INSERT INTO F SELECT * FROM (VALUES ((NOT false), false), (NULL, (NOT (NOT true)))) AS L WHERE (((+(+(-((+110) / (+((-(-150)) * ((247 * (91 * (-47))) + (-86)))))))) = ((((+(+(24 / (+((+89) * (+58)))))) * (-(-((193 + 223) / (-(222 / 219)))))) * (34 * 70)) * (+(+((((+(+(-202))) / (+52)) - (-(228 + (-104)))) * (-24)))))) = (false <> (66 <> 8)));

    # """

    sql_input = """
    CREATE TABLE t0 (c0 INTEGER UNIQUE, c1 INTEGER, c2 TEXT UNIQUE, c3 TEXT UNIQUE);
    CREATE INDEX i8 ON t0(c1) WHERE (t0.c3 < 'default');
    INSERT INTO t0 (c0, c1, c2, c3) VALUES (894, 89, 'unique_0_578', 'unique_0_359'), (110, (41 + 8), 'unique_1_214', 'unique_1_463'), (588, 74, 'unique_2_657', 'unique_2_44'), (155, (22 * 4), 'unique_3_705', 'unique_3_765'), (580, NULL, 'unique_4_635', 'unique_4_302'), (936, (13 + 0), 'unique_5_819', 'unique_5_766'), (888, 58, 'unique_6_681', 'unique_6_32'), (125, NULL, 'unique_7_781', 'unique_7_39'), (209, 87, 'unique_8_74', 'unique_8_945'), (30, 69, 'unique_9_330', 'unique_9_340');
    SELECT t0.c1, t0.c0, COALESCE(AVG(t0.c0) OVER (PARTITION BY t0.c3 ORDER BY t0.c0 DESC), 9) FROM t0 WHERE (t0.c1) IN (SELECT t0.c1 FROM t0)
    """

    evaluator = InlineArithmeticSimplifier()
    simplified_sql = evaluator.equivalent(sql_input)
    print(simplified_sql)

