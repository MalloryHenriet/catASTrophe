import subprocess
import time
import os

from config import BUG_TYPES

class QueryRunner:
    def __init__(self, sqlite_container_name='sqlite3-container'):
        self.sqlite_container_name = sqlite_container_name

    # def run(self, query, version, database='/data/test.db'):
    #     try:
    #         if not isinstance(query, str):
    #             raise ValueError("Query must be a string.")

    #         # Save query to host-mounted file
    #         query_path = os.path.join(os.getcwd(), "query.sql")
    #         with open(query_path, "w", encoding="utf-8") as f:
    #             f.write(query)
    #         # querytest_path = os.path.join(os.getcwd(), "query.sql")
    #         # with open(querytest_path, "w", encoding="utf-8") as f:
    #         #     f.write(query)

    #         # Run docker with bash -c to do the redirection
    #         # docker_cmd = [
    #         #     "docker", "run", "--platform", "linux/amd64", "--rm",
    #         #     "-v", f"{os.getcwd()}:/data",
    #         #     "theosotr/sqlite3-test",
    #         #     "bash", "-c", f"/home/test/sqlite/sqlite3 /data/test.db < /data/query.sql",#f"/usr/bin/sqlite3-3.26.0 /data/test.db < /data/query.sql"
    #         # ]

    #         docker_cmd = [
    #             "docker", "run", "--platform", "linux/amd64", "--rm",
    #             "-v", f"{os.getcwd()}:/data",
    #             "-w", "/home/test/sqlite",
    #             "theosotr/sqlite3-test",
    #             "bash", "-c", "./sqlite3 /data/test.db < /data/query.sql && sleep 1"
    #         ]


    #         # Optional: List files to check .gcda presence
    #         list_cmd = [
    #             "docker", "run", "--rm", "-v", f"{os.getcwd()}:/data",
    #             "-w", "/home/test/sqlite",
    #             "theosotr/sqlite3-test",
    #             "bash", "-c", "ls -lh *.gcda *.gcno"
    #         ]
    #         listing = subprocess.run(list_cmd, capture_output=True, text=True)
    #         print("Coverage file listing:\n", listing.stdout)



    #         docker_gcov = [
    #             "docker", "run", "--rm", "-v", f"{os.getcwd()}:/data",
    #             "-w", "/home/test/sqlite",
    #             "theosotr/sqlite3-test",
    #             "bash", "-c", "gcov -r sqlite3-sqlite3.gcda"
    #         ]



    #         print("Executing query: ", query)
    #         print("====End query==== ")
    #         result = subprocess.run(docker_cmd, capture_output=True, text=True)
    #         print("result: ", result.stdout)
    #         print("====End result==== ")

    #         gcov_result = subprocess.run(docker_gcov, capture_output=True, text=True)
    #         print("gcov_result: ", gcov_result.stdout)
    #         print("gcov_result_err: ", gcov_result.stderr)

    #         # list_cmd = [
    #         #     "docker", "run", "--rm", "-v", f"{os.getcwd()}:/data",
    #         #     "-w", "/home/test/sqlite",
    #         #     "theosotr/sqlite3-test",
    #         #     "bash", "-c", "ls -lh *.gcda *.gcno"
    #         # ]

    #         # listing = subprocess.run(list_cmd, capture_output=True, text=True)
    #         # print("Coverage file listing:\n", listing.stdout)


    #         if result.returncode != 0:
    #             return "CRASH", result.stderr

    #         return "LOGIC_BUG" if self.pivot_missing(result.stdout) else None, result.stdout

    #     except Exception as e:
    #         return "CRASH", str(e)

    def run(self, query, version, database='/data/test.db'):
        try:
            if not isinstance(query, str):
                raise ValueError("Query must be a string.")

            # Save query to host-mounted file
            query_path = os.path.join(os.getcwd(), 'shared', "query.sql")
            with open(query_path, "w", encoding="utf-8") as f:
                f.write(query)

            output_lines = database.splitlines()
            for i, line in enumerate(output_lines[:100]):  # Limit to first 100 lines
                print("database line :",line)
            # Run query using docker exec inside the running container
            docker_cmd = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                "./sqlite3 /data/test.db < /data/query.sql && sleep 1"
            ]

            print("\nContents of the database:")

            # Query the database to show the tables and their contents
            show_tables_cmd = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                f"./sqlite3 {database} '.tables'"
            ]
            tables_result = subprocess.run(show_tables_cmd, capture_output=True, text=True)
            print("Tables in the database:\n", tables_result.stdout)


            # Optional: List coverage files inside the container
            list_cmd = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                "ls -lh *.gcda *.gcno"
            ]

            listing = subprocess.run(list_cmd, capture_output=True, text=True)
            print("Coverage file listing:\n", listing.stdout)

            # Run gcov in the running container
            docker_gcov = [
                "docker", "exec", "-i",
                self.sqlite_container_name,
                "bash", "-c",
                "gcov -r sqlite3-sqlite3.gcda"
            ]

            print("Executing query: ", query)
            print("====End query==== ")
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            print("result: ", result.stdout)
            print("====End result==== ")

            gcov_result = subprocess.run(docker_gcov, capture_output=True, text=True)
            print("gcov_result: ", gcov_result.stdout)
            print("gcov_result_err: ", gcov_result.stderr)



            if result.returncode != 0:
                return "CRASH", result.stderr

            return "LOGIC_BUG" if self.pivot_missing(result.stdout) else None, result.stdout

        except Exception as e:
            return "CRASH", str(e)



    def pivot_missing(self, result_str):
        return False

    def check_container_status(self):
        """
        Check if the SQLite Docker container is running.
        """
        try:
            # Use Docker command to check if the container is running
            result = subprocess.run(
                ['docker', 'ps', '-q', '-f', f'name={self.sqlite_container_name}'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return result.stdout.decode().strip() != ''
        except subprocess.SubprocessError as e:
            print(f"Error checking container status: {e}")
            return False

    def start_container(self):
        """
        Starts the SQLite container if it's not running.
        """
        if not self.check_container_status():
            print(f"QueryRun: Starting the {self.sqlite_container_name} container...")
            #subprocess.run(['docker', 'compose', 'up', '-d'])
            # Wait a bit for the container to initialize
            time.sleep(5)
        else:
            print(f"Container {self.sqlite_container_name} is already running.")
            
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
