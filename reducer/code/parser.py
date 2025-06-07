import sqlglot
import sqlparse

class SQLParser:
    def __init__(self, dialect="sqlite"):
        self.dialect = dialect

    # Take a SQL string and return the syntax tree
    def parse(self, sql_lines):
        sql_string = "".join(sql_lines)
        parsed_stmt = []

        for stmt in sqlparse.split(sql_string):
            stmt = stmt.strip()
            if not stmt:
                continue
            try:
                ast = sqlglot.parse_one(stmt, self.dialect)
                parsed_stmt.append(ast)
            except Exception as e:
                print(f"Parsing error: {e}")
        return parsed_stmt
    
    # Take the syntax tree back to SQL string
    def to_sql(self, ast):
        return ";\n".join(expr.sql() for expr in ast if expr is not None) + ";"


if __name__ == "__main__":
    parser = SQLParser()
    sql = "SELECT a, b FROM t WHERE a > 5 AND b < 3 ORDER BY a"
    ast = parser.parse(sql)

    if ast:
        print("Original SQL:", parser.to_sql(ast))
        print("AST:", ast)
