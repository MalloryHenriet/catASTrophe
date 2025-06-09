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

def get_used_table_column_names(stmts, parser):
    used_tables = set()
    used_columns = set()
    for stmt in stmts:
        tokens = parser.flatten_tokens(stmt)
        for i, tok in enumerate(tokens):
            t = str(tok).lower().strip('"`[]')

            if not t.isidentifier():
                continue

            # Simple heuristic: name after FROM or JOIN = table
            if i > 0 and str(tokens[i-1]).upper() in {"FROM", "JOIN"}:
                used_tables.add(t)
            elif "." in t:
                tbl, col = t.split(".", 1)
                used_tables.add(tbl)
                used_columns.add(col)
            else:
                used_columns.add(t)
    return used_tables, used_columns

def extract_object_name(tokens, prefix):
    try:
        idx = tokens.index(prefix.split()[-1]) + 1  # "TABLE" → next token is name
        return tokens[idx]
    except:
        return None

def drop_shadowed_statements(statements, parser):
    object_defs = {}
    to_remove = set()

    for i, stmt in enumerate(statements):
        stmt_str = parser.to_sql([stmt]).strip().upper()
        tokens = parser.flatten_tokens(stmt)
        token_texts = [str(tok).lower() for tok in tokens]

        for prefix in ["CREATE TABLE", "CREATE VIEW", "CREATE INDEX"]:
            if stmt_str.startswith(prefix):
                name = extract_object_name(token_texts, prefix)
                if name is None:
                    continue

                if name in object_defs:
                    last_idx = object_defs[name]
                    in_between = statements[last_idx + 1:i]

                    # If object not used between last and current redefinition, drop it
                    used_tables, _ = get_used_table_column_names(in_between, parser)
                    if name not in used_tables:
                        to_remove.add(last_idx)

                object_defs[name] = i

    return [stmt for i, stmt in enumerate(statements) if i not in to_remove]