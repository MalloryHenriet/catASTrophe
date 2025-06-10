import os
import subprocess

# Everything should run inside the docker as we imported the sql engines

# returns 0 when bug still happens (valid reduction)
# returns 1 when the bug is gone (wrong reduction)
def execute_query(sql_query, test_script, query_path="query.sql", meta_lines=None):
    with open(query_path, "w") as sql_file:
        if meta_lines:
            sql_file.writelines(meta_lines)
        sql_file.write(sql_query)

    env = os.environ.copy()
    env["TEST_CASE_LOCATION"] = os.path.abspath(query_path)

    try:
        result = subprocess.run(f"./{test_script}", env=env, capture_output=True, text=True)
        return result.returncode
        
    except Exception as e:
        print(f"Execution error : {e}")
        return None