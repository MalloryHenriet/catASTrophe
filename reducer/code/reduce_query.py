from code.parser import SQLParser
from code.executor import execute_query
from code.delta_debugging import delta_debugging

def reduce_query(query_path, test_script, output_path):
    with open(f"{query_path}/original_test.sql", "r") as original_query:
        query_string = original_query.readlines()

    # Parse the query to an AST
    parser = SQLParser()
    ast_list = parser.parse(query_string)

    if not ast_list:
        print("No valid statement to reduce")
        return query_string
    
    # Validator function
    def validator(expr):
        parser = SQLParser()
        query_string = parser.to_sql(expr)

        return execute_query(query_string, test_script, output_path)

    # Update AST with delta debugging technique
    ast_list = delta_debugging(ast_list, validator)

    minimized = parser.to_sql(ast_list)

    if minimized is None:
        return query_string
    
    return 0