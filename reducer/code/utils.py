import shutil
import os
import sqlparse

def prepare_workspace(query_path):
    src = os.path.abspath(query_path)
    query_id = os.path.basename(src)

    # Set destination inside /queries
    base_dir = os.path.dirname(os.path.dirname(__file__))
    dst = os.path.join(base_dir, "queries", query_id)

    if not os.path.exists(src):
        raise FileNotFoundError(f"Source path not found: {src}")

    if os.path.exists(dst):
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

def get_used_table_column_names(statements, parser, define_mode=False):
    """
    Returns (tables, columns) used or defined in the given statements.
    If define_mode is True, returns what is defined (e.g., CREATE TABLE).
    Otherwise, returns what is referenced (e.g., SELECT ... FROM ...).
    """
    tables = set()
    columns = set()
    for stmt in statements:
        tokens = parser.flatten_tokens(stmt)
        for tok in tokens:
            tok_str = str(tok).lower()
            if define_mode:
                if "create table" in tok_str or "create view" in tok_str or "create index" in tok_str:
                    tables.add(tok_str)
                if "(" in tok_str and ")" in tok_str:
                    columns.update(tok_str.replace("(", "").replace(")", "").split(","))
            else:
                if "." in tok_str:
                    t, c = tok_str.split(".", 1)
                    tables.add(t)
                    columns.add(c)
                elif tok_str.isidentifier():
                    columns.add(tok_str)
    return tables, columns