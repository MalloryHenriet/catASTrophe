import subprocess
import time
import os

from config import BUG_TYPES

class QueryRunner:
    def __init__(self, version, sqlite_container_name='sqlite3-container'):
        self.version = version
        self.sqlite_container_name = sqlite_container_name

    def run(self, query, database='/data/test.db'):
        try:
            if not isinstance(query, str):
                raise ValueError("Query must be a string.")

            # Save query to shared folder
            query_path = os.path.join(os.getcwd(), 'shared', "query.sql")
            with open(query_path, "w", encoding="utf-8") as f:
                f.write(query)

            # Pick correct binary based on version
            sqlite_binary = {
                "3.26.0": "/usr/bin/sqlite3-3.26.0",
                "3.39.4": "/usr/bin/sqlite3-3.39.4"
            }.get(self.version)

            if not sqlite_binary:
                raise ValueError(f"Unsupported SQLite version: {self.version}")

            # Run the query
            docker_cmd = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                #f"{sqlite_binary} {database} < /data/query.sql"
                #"/home/test/sqlite && ./sqlite",f" {database} < /data/query.sql"
                "./sqlite3 /data/test.db < /data/query.sql"
            ]

           
            docker_gcov = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                "gcov -r sqlite3-sqlite3.gcda"
            ]
            
            
            print(f"Executing query on SQLite {self.version}...")
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            print("====End query==== ")
            print("result: ", result.stdout)
            print("====End result==== ")

            gcov_result = subprocess.run(docker_gcov, capture_output=True, text=True)
            print("gcov_result: ", gcov_result.stdout)
            print("gcov_result_err: ", gcov_result.stderr)


            
            if result.returncode != 0:
                return "CRASH", result.stderr

            return "LOGIC_BUG" if self.pivot_missing(result.stdout, query) else None, result.stdout

        except Exception as e:
            return "CRASH", str(e)
    
    
    def pivot_missing(self, result_str, pivot):
        return  pivot in result_str
    
# Example usage:
if __name__ == "__main__":
    query_runner = QueryRunner()

    # Ensure the container is running
    query_runner.start_container()

    # Example query
    # query = """
    #     CREATE TABLE IF NOT EXISTS t0 ( c0 INT );
    #     INSERT INTO t0 ( c0 ) VALUES (1);
    #     SELECT * FROM t0 WHERE 1 = 1;
    # """

    # # Run the query on version 3.39.4 container (or another version if needed)
    # result = query_runner.run(query, version="3.39.4")
    # print("Query execution result:", result)
