# Generate interesting SQL queries

# Will use the techniques found in the resources of the instructions

# Pivoted Query Synthesis (PQS) : https://www.youtube.com/watch?v=0aeDyXgzo04
# 100 000 queries for each generated database

# Query Partitioning : https://dl.acm.org/doi/10.1145/3428279

# Query Plan Guidance : https://ieeexplore.ieee.org/document/10172874

# Equivalent Expression Transformation : https://www.usenix.org/system/files/osdi24-jiang.pdf

# We are going to use the 2 datasets kpop_idols and kpop_ranking for query generation

import random
import math
from sqlglot import exp, select

operators = ['=', '!=', '<', '>', 'LIKE']

class QueryGenerator:
    def __init__(self):
        pass

    def get_condition(self, value, col):
        column = exp.Column(this=col)
        if value is None:
            if random.choice([True, False]):
                condition = exp.Is(this=column, expression=exp.Null())
            else:
                condition = exp.Not(this=exp.Is(this=column, expression=exp.Null()))
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
    
    def generate_where_clause(self, pivot):
        conditions = []
        for col, value in pivot.items():
            if isinstance(value, float) and math.isnan(value):
                value = None
            conditions.append(self.get_condition(value, col))

        if not conditions:
            return exp.TRUE

        expression = conditions[0]
        for cond in conditions[1:]:
            if random.random() < 0.6:
                expression = exp.And(this=expression, expression=cond)
            else:
                expression = exp.Or(this=expression, expression=cond)

        return expression

    def get_random_assignment(self, pivot):
        col = random.choice(list(pivot.keys()))
        value = pivot[col]
        if value is None:
            new_value = exp.Null()
        elif isinstance(value, str):
            new_value = exp.Literal.string(value[::-1])  # Reverse string
        elif isinstance(value, (int, float)):
            new_value = exp.Literal.number(str(value + random.randint(-5, 5)))
        else:
            new_value = exp.Literal.string(str(value))
        
        return exp.EQ(this=exp.Column(this=col), expression=new_value)
    
    def generate_aggregate_query(self, pivot, table_name):
        # Filter numeric columns
        numeric_cols = [col for col, val in pivot.items() if isinstance(val, (int, float)) and not math.isnan(val)]
        if not numeric_cols:
            return self.generate_select(pivot, table_name)  # Fallback

        col = random.choice(numeric_cols)
        col_expr = exp.Column(this=col)
        func = random.choice([exp.Max, exp.Min, exp.Sum, exp.Avg, exp.Count])
        
        # Create aggregate expression
        agg_expr = func(this=col_expr)
        
        query = exp.select(agg_expr).from_(table_name)

        # Optional GROUP BY (on a non-agg column)
        non_agg_cols = [c for c in pivot.keys() if c != col]
        if non_agg_cols and random.random() < 0.5:
            group_col = random.choice(non_agg_cols)
            query = query.group_by(exp.Column(this=group_col))

        # Optional HAVING
        if random.random() < 0.3:
            query = query.having(
                exp.GT(this=agg_expr.copy(), expression=exp.Literal.number(random.randint(1, 100)))
            )

        return query
    
    def generate_select(self, pivot, table_name):
        expressions = self.generate_where_clause(pivot)

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

        # weirdness = random.random()
        # if weirdness < 0.01:
        #     query = select("1 = 1 AND 1 = 0").from_(table_name)
        # elif weirdness < 0.02:
        #     query = select("COUNT(SELECT * FROM table)")
        # elif weirdness < 0.03:
        #     query = select("name AS age", "age").from_(table_name).order_by("age")
        # elif weirdness < 0.04:
        #     query = select().from_(table_name).select(
        #         exp.EQ(this=exp.Column(this="weight"), expression=exp.Literal.number("-9223372036854775809"))
        #     )
        # elif weirdness < 0.05:
        #     query = select().from_(table_name).select(
        #         exp.EQ(this=exp.Column(this="weight"), expression=exp.Literal.number("1E28475"))
        #     )

        return query
    
    def generate_update(self, pivot, table_name):
        assignment = self.get_random_assignment(pivot)        
        where_expr = self.generate_where_clause(pivot)
        if where_expr is None:
            where_expr = exp.TRUE  # Redundant now, but safe
        query = exp.Update().table(table_name).set_(assignment).where(where_expr)
        return query

    def generate_delete(self, pivot, table_name):
        where_expr = self.generate_where_clause(pivot)
        if where_expr is None:
            where_expr = exp.TRUE

        print(f"TAble Name: {table_name}")
        query = exp.delete(table=table_name).where(where_expr)
        return query


    def generate_query_for_pivot(self, pivot, table_name):
        choice = random.random()
        if choice < 0.4:
            return self.generate_select(pivot, table_name)
        elif choice < 0.5:
            return self.generate_aggregate_query(pivot, table_name)
        elif choice < 0.75:
            return self.generate_update(pivot, table_name)
        else:
            return self.generate_delete(pivot, table_name)


    def generate_query(self):
        # TODO: implement
        return random.random()