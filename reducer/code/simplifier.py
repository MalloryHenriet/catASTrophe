import re
import copy

# Applies transformations to individual SQL statements
def simplifier(statements, validator=False):
    def try_removal(pattern, replacement, sql):
        modified = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
        if modified != sql:
            test_statements = updated_statements[:i] + [modified] + updated_statements[i + 1:]
            if validator(test_statements):
                return modified
        return modified

    updated_statements = copy.deepcopy(statements)
    changed = True

    def remove_order_by_expressions(sql):
        order_by_match = re.search(r'ORDER\s+BY\s+(.*?)(\)|$)', sql, flags=re.IGNORECASE)
        if not order_by_match:
            return sql

        expr_list = order_by_match.group(1)
        suffix = order_by_match.group(2)
        expressions = [e.strip() for e in expr_list.split(',')]
        remaining = expressions[:]

        for expr in expressions:
            temp = ', '.join([e for e in remaining if e != expr])
            temp_clause = f'ORDER BY {temp}' if temp else ''
            modified_sql = re.sub(
                r'ORDER\s+BY\s+.*?(\)|$)',
                f'{temp_clause}{suffix}',
                sql,
                flags=re.IGNORECASE
            )
            test_statements = updated_statements[:i] + [modified_sql] + updated_statements[i + 1:]
            if validator(test_statements):
                remaining.remove(expr)
                sql = modified_sql
        return sql
    
    def remove_partition_by_expressions(sql):
        match = re.search(r'(PARTITION\s+BY\s+)(.*?)(\s+ORDER\s+BY|\s+\)|\s+OVER|\))', sql, flags=re.IGNORECASE)
        if not match:
            return sql

        prefix = match.group(1)
        expr_list = match.group(2).strip()
        suffix = match.group(3)

        expressions = [e.strip() for e in expr_list.split(',')]
        remaining = expressions[:]

        for expr in expressions:
            temp_exprs = ', '.join([e for e in remaining if e != expr])
            if temp_exprs:
                replacement = f'{prefix}{temp_exprs}{suffix}'
            else:
                # No expressions left → remove PARTITION BY entirely
                replacement = '' if suffix.strip() == ')' else suffix

            modified_sql = sql[:match.start()] + replacement + sql[match.end():]
            test_statements = updated_statements[:i] + [modified_sql] + updated_statements[i + 1:]

            if validator(test_statements):
                remaining.remove(expr)
                sql = modified_sql
        return sql
    
    def remove_where_conditions(sql):
        match = re.search(r'WHERE\s+(.*?)(GROUP\s+BY|ORDER\s+BY|LIMIT|$)', sql, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return sql
        condition_str = match.group(1).strip()
        suffix = match.group(2)

        # Only split top-level AND conditions (basic case)
        conditions = [c.strip(' ()') for c in re.split(r'\s+AND\s+', condition_str, flags=re.IGNORECASE)]
        remaining = conditions[:]
        for cond in conditions:
            temp = ' AND '.join([c for c in remaining if c != cond])
            if temp:
                modified = re.sub(r'WHERE\s+.*?(GROUP\s+BY|ORDER\s+BY|LIMIT|$)', f'WHERE {temp} {suffix}', sql, flags=re.IGNORECASE | re.DOTALL)
            else:
                modified = re.sub(r'\s*WHERE\s+.*?(GROUP\s+BY|ORDER\s+BY|LIMIT|$)', '', sql, flags=re.IGNORECASE | re.DOTALL)
            test_statements = updated_statements[:i] + [modified] + updated_statements[i + 1:]
            if validator(test_statements):
                remaining.remove(cond)
                sql = modified
        return sql

    while changed:
        changed = False
        for i, sql in enumerate(updated_statements):
            original = sql

            sql = remove_order_by_expressions(sql)
            sql = remove_partition_by_expressions(sql)
            sql = remove_where_conditions(sql)

            if sql != original:
                updated_statements[i] = sql
                changed = True

    return updated_statements


if __name__ == "__main__":

    sql_statements = [
    "CREATE TABLE t0 (c0 INTEGER UNIQUE, c1 INTEGER, c2 TEXT UNIQUE, c3 TEXT UNIQUE);",
    "CREATE INDEX i8 ON t0(c1) WHERE (t0.c3 < 'default');",
    """INSERT INTO t0 (c0, c1, c2, c3) VALUES 
        (894, 89, 'unique_0_578', 'unique_0_359'), 
        (110, (41 + 8), 'unique_1_214', 'unique_1_463'), 
        (588, 74, 'unique_2_657', 'unique_2_44'), 
        (155, (22 * 4), 'unique_3_705', 'unique_3_765'), 
        (580, NULL, 'unique_4_635', 'unique_4_302'), 
        (936, (13 + 0), 'unique_5_819', 'unique_5_766'), 
        (888, 58, 'unique_6_681', 'unique_6_32'), 
        (125, NULL, 'unique_7_781', 'unique_7_39'), 
        (209, 87, 'unique_8_74', 'unique_8_945'), 
        (30, 69, 'unique_9_330', 'unique_9_340');""",
    "SELECT t0.c1, t0.c0, COALESCE(AVG(t0.c0) OVER (PARTITION BY t0.c3 ORDER BY t0.c0 DESC), 9) FROM t0 WHERE (t0.c1) IN (SELECT t0.c1 FROM t0);"]

    reduced = simplifier(sql_statements)
    print("\n-- Reduced SQL --")
    for line in reduced:
        print(line)