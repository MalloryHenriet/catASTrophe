from code.parser import SQLParser
from code.executor import execute_query
from code.delta_debugging import delta_debugging

def must_keep(statement_str: str) -> bool:
    upper = statement_str.upper().strip()
    return upper.startswith("CREATE TABLE") or upper.startswith("INSERT INTO")

def reduce_query(query_path, test_script, output_path):
    with open(f"{query_path}/original_test.sql", "r") as original_query:
        query_string = original_query.readlines()

    # Parse the query to an AST
    parser = SQLParser()
    token_tree = parser.parse(query_string)
    token_tree_size = sum(len(parser.flatten_tokens(tree)) for tree in token_tree)

    if not token_tree:
        print("No valid statement to reduce")
        return query_string
    
    required_stmts = []
    reducible_stmts = []
    for stmt in token_tree:
        stmt_str = parser.to_sql([stmt]).strip()
        if must_keep(stmt_str):
            required_stmts.append(stmt)
        else:
            reducible_stmts.append(stmt)

    # Validator function
    def validator(expr):
        full_program = required_stmts + expr
        query_string = parser.to_sql(full_program)
        result = execute_query(query_string, test_script, output_path)

        return result == 0
    
    assert validator(reducible_stmts), "Original reducible portion does not trigger the bug."

    # Update AST with delta debugging technique
    reduced_token_tree = delta_debugging(reducible_stmts, validator)

    minimized = parser.to_sql(required_stmts + reduced_token_tree)
    minimzed_token_size = sum(len(parser.flatten_tokens(tree)) for tree in required_stmts + reduced_token_tree)

    if minimized is None:
        return query_string, token_tree_size, minimzed_token_size
    
    with open(output_path, "w") as out:
        out.write(minimized)
    
    return minimized, token_tree_size, minimzed_token_size