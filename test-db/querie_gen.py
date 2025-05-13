# Generate interesting SQL queries

# Will use the techniques found in the resources of the instructions

# Pivoted Query Synthesis (PQS) : https://www.youtube.com/watch?v=0aeDyXgzo04
# 100 000 queries for each generated database

# Query Partitioning : https://dl.acm.org/doi/10.1145/3428279

# Query Plan Guidance : https://ieeexplore.ieee.org/document/10172874

# Equivalent Expression Transformation : https://www.usenix.org/system/files/osdi24-jiang.pdf

# We are going to use the 2 datasets kpop_idols and kpop_ranking for query generation

import random
from sqlglot import exp, select

operators = ['=', '!=', '<', '>', 'LIKE']

class QueryGenerator:
    def __init__(self):
        pass

    def get_condition(self, value, col):
        print(f"DEBUG: Column={col}, Value={value}, Type={type(value)}")
        column = exp.Column(this=col)
        if value is None:
            if random.choice([True, False]):
                condition = exp.Is(this=column, expression=exp.Null())
            else:
                condition = exp.IsNot(this=column, expression=exp.Null())
        else:
            if isinstance(value, str):
                literal = exp.Literal.string(value)
            elif isinstance(value, (int, float)):
                literal = exp.Literal.number(value)
            else:
                literal = exp.Literal.string(str(value))
            operation = random.choice(operators)
            if operation == '=':
                condition = exp.EQ(this=column, expression=literal)
            elif operation == '!=':
                condition = exp.NEQ(this=column, expression=literal)
            elif operation == '<':
                condition = exp.LT(this=column, expression=literal)
            elif operation == '>':
                condition = exp.GT(this=column, expression=literal)
            elif operation == 'LIKE':
                pattern = f"%{str(value)}%"
                condition = exp.Like(this=column, expression=exp.Literal.string(pattern))
        return condition

    def generate_query_for_pivot(self, pivot, table_name):
        conditions = []
        for col, value in pivot.items():
            condition = self.get_condition(value, col)

            conditions.append(condition)

        expressions = conditions[0]
        for cond in conditions[1:]:
            if random.random() < 0.6:
                expressions = exp.And(this=expressions, expression=cond)
            else:
                expressions = exp.Or(this=expressions, expression=cond)

        query = exp.select("*").from_(table_name).where(expressions)

        if random.random() < 0.6:
            query = query.order_by(exp.Column(this=random.choice(list(pivot.keys()))))

        if random.random() < 0.3:
            query = query.limit(random.randint(1, 10))

        if random.random() < 0.3:
            group_col = random.choice(list(pivot.keys()))
            query = query.group_by(exp.Column(this=group_col))

        if random.random() < 0.3:
            having_cond = self.get_condition(random.choice(list(pivot.values())), random.choice(list(pivot.keys())))
            query = query.having(having_cond)

        if random.random() < 0.2:
            query = select("1 = 1 AND 1 = 0").from_(table_name)

        if random.random() < 0.1:
            # Create syntactically invalid expression
            query = select("COUNT(SELECT * FROM table)")

        if random.random() < 0.1:
            # Add ambiguous alias
            query = select("name AS age", "age").from_(table_name).order_by("age")
        
        return query

    def generate_query(self):
        # TODO: implement
        return random.random()