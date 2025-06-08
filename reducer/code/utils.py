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


def count_tokens(sql_file_path, return_query=False):

    with open(sql_file_path, 'r') as f:
        query = f.read()
    parsed = sqlparse.parse(query)
    if not parsed:
        return (0, query) if return_query else 0
    tokens = [t for t in parsed[0].flatten() if not t.is_whitespace]
    print("count_tokens: ", tokens)
    return (len(tokens), query) if return_query else len(tokens)

