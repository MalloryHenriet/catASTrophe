import sqlglot

class SQLParser:
    def __init__(self, dialect="sqlite"):
        self.dialect = dialect

    # Take a SQL string and return the syntax tree
    def parse(self, sql_string):
        try:
            return sqlglot.parse_one(sql_string, self.dialect)
        except Exception as e:
            print(f"Parsing error: {e}")
            return None
    
    # Take the syntax tree back to SQL string
    def to_sql(self, ast):
        try:
            return ast.sql(dialect=self.dialect)
        except Exception as e:
            print(f"SQL Translation to string error: {e}")
            return None


if __name__ == "__main__":
    parser = SQLParser()
    sql = "SELECT a, b FROM t WHERE a > 5 AND b < 3 ORDER BY a"
    ast = parser.parse(sql)

    if ast:
        print("Original SQL:", parser.to_sql(ast))
        print("AST:", ast)
