# Utilities functions
import uuid
import os
import pandas as pd
import random

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
    return f"INSERT INTO {table_name} ({columns}) VALUES\n" + ",\n".join(values) + ";"


def load_csv(csv_name, header, cols):
    df = pd.read_csv(csv_name)
    df_copy = df.copy()
    df_copy.columns = header
    return df_copy[cols]