# Generate interesting SQL queries

# Will use the techniques found in the resources of the instructions

# Pivoted Query Synthesis (PQS) : https://www.youtube.com/watch?v=0aeDyXgzo04
# 100 000 queries for each generated database

# Query Partitioning : https://dl.acm.org/doi/10.1145/3428279

# Query Plan Guidance : https://ieeexplore.ieee.org/document/10172874

# Equivalent Expression Transformation : https://www.usenix.org/system/files/osdi24-jiang.pdf

# We are going to use the 2 datasets kpop_idols and kpop_ranking for query generation

import random
from sqlglot import exp

class QueryGenerator:
    def __init__(self):
        pass

    def generate_query_for_pivot(self, pivot, table_name):
        conditions = []
        for col, value in pivot.items():
            if value is None:
                conditions.append(exp.Is(this=exp.Column(this=col), expression=exp.Null()))
            else:
                literal = exp.Literal.string(str(value))
                conditions.append(exp.EQ(this=exp.Column(this=col), expression=literal))

        expressions = conditions[0]
        for cond in conditions[1:]:
            expressions = exp.And(this=expressions, expression=cond)

        query = exp.select("*").from_(table_name).where(expressions)
        return query

    def generate_query(self):
        # TODO: implement
        return random.random()