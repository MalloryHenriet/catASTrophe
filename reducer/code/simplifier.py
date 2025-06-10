import re
import copy

class SQLSimplifier:
    def __init__(self, parser, validator):
        self.parser = parser
        self.validator = validator

    def simplify(self, token_trees):
        updated_trees = copy.deepcopy(token_trees)
        changed = True

        while changed:
            changed = False
            for i, stmt in enumerate(updated_trees):
                sql = self.parser.to_sql([stmt])
                simplified_sql = self._simplify_sql(sql, updated_trees, i)

                if simplified_sql.strip() != sql.strip():
                    new_stmt = self.parser.parse(simplified_sql)[0]
                    updated_trees[i] = new_stmt
                    changed = True

        return updated_trees
    
    def _simplify_sql(self, sql, stmts, index):
        sql = self._remove_order_by(sql, stmts, index)
        sql = self._remove_partition_by(sql, stmts, index)
        sql = self._remove_where_conditions(sql, stmts, index)
        return sql
    
    def _validate(self, stmts):
        return self.validator(stmts)
    
    def _remove_order_by(self, sql, stmts, i):
        match = re.search(r'ORDER\s+BY\s+(.*?)(\)|$)', sql, flags=re.IGNORECASE)
        if not match:
            return sql

        expr_list = match.group(1)
        suffix = match.group(2)
        expressions = [e.strip() for e in expr_list.split(',')]
        remaining = expressions[:]

        for expr in expressions:
            temp = ', '.join([e for e in remaining if e != expr])
            clause = f'ORDER BY {temp}' if temp else ''
            new_sql = re.sub(r'ORDER\s+BY\s+.*?(\)|$)', f'{clause}{suffix}', sql, flags=re.IGNORECASE)

            new_sql_list = [self.parser.to_sql([stmt]) if idx != i else new_sql for idx, stmt in enumerate(stmts)]
            parsed_new_stmts = [self.parser.parse(sql)[0] for sql in new_sql_list]
            if self._validate(parsed_new_stmts):
                sql = new_sql
                remaining.remove(expr)
        return sql
    
    def _remove_partition_by(self, sql, stmts, i):
        match = re.search(r'(PARTITION\s+BY\s+)(.*?)(\s+ORDER\s+BY|\s+\)|\s+OVER|\))', sql, flags=re.IGNORECASE)
        if not match:
            return sql

        prefix, expr_list, suffix = match.groups()
        expressions = [e.strip() for e in expr_list.split(',')]
        remaining = expressions[:]

        for expr in expressions:
            temp_expr = ', '.join([e for e in remaining if e != expr])
            repl = f'{prefix}{temp_expr}{suffix}' if temp_expr else ('' if suffix.strip() == ')' else suffix)
            new_sql = sql[:match.start()] + repl + sql[match.end():]
            new_sql_list = [self.parser.to_sql([stmt]) if idx != i else new_sql for idx, stmt in enumerate(stmts)]
            parsed_new_stmts = [self.parser.parse(sql)[0] for sql in new_sql_list]
            if self._validate(parsed_new_stmts):
                sql = new_sql
                remaining.remove(expr)
        return sql

    def _remove_where_conditions(self, sql, stmts, i):
        pattern = r'WHERE\s+(.*?)(\s+GROUP\s+BY|\s+ORDER\s+BY|\s+LIMIT|$)'
        match = re.search(pattern, sql, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return sql

        conds, _ = match.groups()
        conditions = [c.strip(' ()') for c in re.split(r'\s+AND\s+', conds, flags=re.IGNORECASE)]
        remaining = conditions[:]

        for cond in conditions:
            temp = ' AND '.join([c for c in remaining if c != cond])

            try:
                if temp:
                    new_sql = re.sub(
                        pattern,
                        lambda m: f'WHERE {temp}{m.group(2)}',
                        sql,
                        flags=re.IGNORECASE | re.DOTALL
                    )
                else:
                    new_sql = re.sub(
                        pattern,
                        lambda m: m.group(2),
                        sql,
                        flags=re.IGNORECASE | re.DOTALL
                    )
            except re.error as e:
                print("🔥 REGEX ERROR 🔥")
                print("Pattern :", pattern)
                print("Repl    :", temp)
                print("Error   :", str(e))
                raise

            new_sql_list = [self.parser.to_sql([stmt]) if idx != i else new_sql for idx, stmt in enumerate(stmts)]
            parsed_new_stmts = [self.parser.parse(sql)[0] for sql in new_sql_list]
            if self._validate(parsed_new_stmts):
                sql = new_sql
                remaining.remove(cond)

        return sql