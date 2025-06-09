import shutil
import os

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
