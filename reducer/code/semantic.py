# import sqlparse
# from code.executor import execute_query


# def extract_where_expressions(where_clause):
#     return [expr.strip() for expr in where_clause.split("AND")]

# def rebuild_query(base_query, where_exprs):
#     if not where_exprs:
#         return base_query.split("WHERE")[0].strip() + ";"
#     new_where = " AND ".join(where_exprs)
#     return base_query.split("WHERE")[0].strip() + f" WHERE {new_where};"

# def reduce_where_clause(query_str, test_script, query_output_path="query.sql"):
#     if "WHERE" not in query_str.upper():
#         return query_str

#     where_start = query_str.upper().find("WHERE")
#     base_query = query_str[:where_start]
#     where_clause = query_str[where_start + len("WHERE"):].strip().rstrip(";")

#     expressions = extract_where_expressions(where_clause)
#     i = 0

#     while i < len(expressions):
#         trial_exprs = expressions[:i] + expressions[i+1:]
#         trial_query = rebuild_query(base_query, trial_exprs)

#         result_code = execute_query(trial_query, test_script, query_output_path)

#         if result_code == 0:
#             print(f"[REDUCED] Removed WHERE clause: {expressions[i]}")
#             expressions = trial_exprs
#         else:
#             print(f"[RETAINED] Keeping WHERE clause: {expressions[i]}")
#             i += 1

#     return rebuild_query(base_query, expressions)
import re
from code.executor import execute_query

def remove_where_clause(query_string: str) -> str:
    """
    Removes the WHERE clause from the SQL query using regex (simplified).
    Assumes only one WHERE clause exists and is not nested in subqueries.
    """
    pattern = re.compile(r"\bWHERE\b.+?(?=(GROUP BY|ORDER BY|LIMIT|;|$))", re.IGNORECASE | re.DOTALL)
    return pattern.sub('', query_string)


def reduce_where_clause(query_string: str, test_script: str, query_path: str) -> str:
    """
    Try to semantically reduce the WHERE clause. Only keep the reduction
    if the test script returns exit code 0 (bug still happens).
    """
    reduced_query = remove_where_clause(query_string)
    
    # Test the reduced query
    result = execute_query(reduced_query, test_script, query_path)

    if result == 0:
        print("[✔] Removed WHERE clause — bug still happens.")
        return reduced_query
    else:
        print("[✘] Removing WHERE clause changed behavior — keeping original.")
        return query_string

