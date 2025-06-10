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
    alias_to_table = {}

    for stmt in stmts:
        tokens = parser.flatten_tokens(stmt)
        token_strs = [str(tok).lower().strip('"`[]') for tok in tokens]

        i = 0
        while i < len(token_strs):
            tok = token_strs[i]

            # ✅ Mark INSERT target table as used (semantic root cause in your case)
            if tok == "insert" and i + 2 < len(token_strs) and token_strs[i + 1] == "into":
                insert_target = token_strs[i + 2]
                used_tables.add(insert_target)
                i += 3
                continue

            # Alias FROM x AS y
            if i + 2 < len(token_strs) and token_strs[i + 1] == "as":
                table, _, alias = token_strs[i:i + 3]
                alias_to_table[alias] = table
                i += 3
                continue

            # Alias.column
            if i + 2 < len(token_strs) and token_strs[i + 1] == ".":
                alias, _, col = token_strs[i:i + 3]
                table = alias_to_table.get(alias, alias)
                used_tables.add(table)
                used_columns.add(col)
                i += 3
                continue

            # FROM/JOIN table
            if i > 0 and token_strs[i - 1] in {"from", "join"}:
                used_tables.add(tok)

            elif tok.isidentifier():
                used_columns.add(tok)

            i += 1

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

def drop_unused_insert_statements(required_stmts, reduced_token_tree, parser, validator):
    used_tables, used_columns = get_used_table_column_names(reduced_token_tree, parser)
    final_required = []

    inserts_by_table = {}

    for stmt in required_stmts:
        sql = parser.to_sql([stmt]).strip().upper()
        if sql.startswith("INSERT INTO"):
            stmt_tokens = parser.flatten_tokens(stmt)
            token_texts = [str(tok).lower() for tok in stmt_tokens]

            # Try to extract target table after "INTO"
            try:
                idx = token_texts.index("into")
                target_table = token_texts[idx + 1]
                inserts_by_table.setdefault(target_table, []).append(stmt)
            except (ValueError, IndexError):
                final_required.append(stmt)
        else:
            final_required.append(stmt)

    # Filter inserts by table usage
    for table, stmts in inserts_by_table.items():
        for insert_stmt in stmts:
            test_required = [s for s in final_required if s != insert_stmt]
            if not validator(test_required + reduced_token_tree):
                final_required.append(insert_stmt)


    if not validator(final_required + reduced_token_tree):
        raise RuntimeError("Bug lost after removing unused insert filtering")

    return final_required
