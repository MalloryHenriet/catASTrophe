# Utilities functions
import uuid
import os
import random
import pandas as pd
import numpy as np
from sqlglot import exp
from sqlglot.expressions import Expression

from config import SQL_CLAUSES

def create_bug_folder():
    folder_name = "bug_" + uuid.uuid4().hex

    folder_path = "./bugs/" + folder_name

    os.makedirs(folder_path)
    
    return folder_path


def write_file(path, filename, content):
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)


def create_table(table_name, columns):
    column_defs = ', '.join([f'"{col_name}" {col_type}' for col_name, col_type in columns])
    statement = f"CREATE TABLE {table_name} ({column_defs});"
    return statement

def generate_insert(table_name, df):
    if df.empty:
        return ""
    
    n_rows = random.randint(1, len(df))

    # Sample random rows
    sampled_df = df.sample(n=n_rows)

    # Format rows into SQL
    def sql_literal(value):
        if pd.isna(value):
            return "NULL"
        if isinstance(value, str):
            escaped = value.replace("'", "''")  # escape single quotes for SQL
            return f"'{escaped}'"
        return str(value)

    values = []
    for _, row in sampled_df.iterrows():
        row_values = ", ".join(sql_literal(val) for val in row)
        values.append(f"({row_values})")

    columns = ", ".join(df.columns)
    return sampled_df, f"INSERT INTO {table_name} ({columns}) VALUES\n" + ",\n".join(values) + ";"


def load_csv(csv_name, header, cols):
    df = pd.read_csv(csv_name, na_values=["", "NULL"])
    df.columns = header
    for col in ["Height", "Weight"]:
        if col in df.columns:
            df[col] = df[col].replace(0, pd.NA)
    return df[cols]

def update_count_clauses(query, count):
    counts = {clause: 0 for clause in SQL_CLAUSES}

    for node in query.walk():
        if isinstance(node, exp.Select):
            counts['SELECT'] += 1
        elif isinstance(node, exp.From):
            counts['FROM'] += 1
        elif isinstance(node, exp.Where):
            counts['WHERE'] += 1
        elif isinstance(node, exp.Join):
            counts['JOIN'] += 1
        elif isinstance(node, exp.Group):
            counts['GROUP BY'] += 1
        elif isinstance(node, exp.Order):
            counts['ORDER BY'] += 1
        elif isinstance(node, exp.Having):
            counts['HAVING'] += 1
        elif isinstance(node, exp.Limit):
            counts['LIMIT'] += 1

    for clause, num in counts.items():
        count[clause].append(num)
    return count

def get_freq_clauses(count):
    freqs = {k: float(np.mean(v)) for k, v in count.items()}
    return freqs

def get_expression_depth(query):
    if not isinstance(query, Expression) or not query.args:
        return 1
    return 1 + max((get_expression_depth(child) for child in query.args.values() if isinstance(child, Expression)), default=0)

def get_validity(query):
    is_valid = 1
    return 1 if is_valid else 0