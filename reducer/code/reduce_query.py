from code.parser import SQLParser
from code.executor import execute_query
from code.delta_debugging import delta_debugging
from code.semantic import reduce_where_clause

def reduce_query(query_path, test_script, output_path):
    with open(f"{query_path}/original_test.sql", "r") as original_query:
        query_string = original_query.read()


    reduced_query = reduce_where_clause(query_string, test_script, output_path)
    print("reduced_query ", reduced_query)

    # Parse the query to an AST
    parser = SQLParser()
    token_tree = parser.parse([reduced_query])
    token_tree_size = sum(len(parser.flatten_tokens(tree)) for tree in token_tree)

    if not token_tree:
        print("No valid statement to reduce")
        return query_string
    
    # Validator function
    def validator(expr):
        parser = SQLParser()
        query_string = parser.to_sql(expr)

        return execute_query(query_string, test_script, output_path)

    # Update AST with delta debugging technique
    # token_tree = delta_debugging(token_tree, validator)

    minimzed_token_size = sum(len(parser.flatten_tokens(tree)) for tree in token_tree)
    minimized = parser.to_sql(token_tree)

    if minimized is None:
        return query_string, token_tree_size, minimzed_token_size
    
    return minimized, token_tree_size, minimzed_token_size