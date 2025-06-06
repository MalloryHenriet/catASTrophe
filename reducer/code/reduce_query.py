from code.parser import SQLParser

def reduce_query(query, test_script):

    # Parse the query to an AST
    parser = SQLParser()
    ast = parser.parse(query)

    if ast is None:
        return query

    # Optimize query

    # Apply modifications

    # Translate the AST to SQL string
    minimized = parser.to_sql(ast)

    if minimized is None:
        return query

    return 0