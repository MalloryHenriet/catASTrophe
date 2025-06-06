import shutil
import os

def prepare_workspace(query_id):
    src = f"queries-to-minimize/{query_id}"
    dst = f"queries/{query_id}"
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)