import sqlparse
from sqlparse.tokens import Token
class SQLParser:
    def __init__(self, dialect="sqlite"):
        self.dialect = dialect

    # Take a SQL string and return the syntax tree
    def parse(self, sql_lines):
        sql_string = "".join(sql_lines)
        statements = [stmt.strip() for stmt in sqlparse.split(sql_string) if stmt.strip()]
        tokenized_statements = [sqlparse.parse(stmt)[0] for stmt in statements]
        return tokenized_statements
    
    # Take the syntax tree back to SQL string
    def to_sql(self, token_trees):
        return "\n".join(str(tree).strip() for tree in token_trees if tree is not None) + ";"

    def flatten_tokens(self, token_tree):
        return [token for token in token_tree.flatten() if token.ttype != Token.Text.Whitespace]


if __name__ == "__main__":
    parser = SQLParser()
    sql = "SELECT a, b FROM t WHERE a > 5 AND b < 3 ORDER BY a"
    ast = parser.parse(sql)

    if ast:
        print("Original SQL:", parser.to_sql(ast))
        print("AST:", ast)
