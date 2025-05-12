import subprocess
import time
import os

from config import BUG_TYPES

class QueryRunner:
    def __init__(self, sqlite_container_name='sqlite3-container'):
        # The SQLite container name (you can modify if needed)
        self.sqlite_container_name = sqlite_container_name

    def run(self, query, version, database='/sqlite/test.db'):
        """
        Runs the given query on the SQLite engine inside a Docker container.

        :param query: The SQL query to run.
        :param version: The SQLite version to use (to choose the container).
        :param database: The SQLite database file to connect to (default: /sqlite/test.db).
        :return: The result of the query or error message.
        """
        try:
            if not isinstance(query, str):
                raise ValueError("Query must be a string, but got type: {}".format(type(query)))

            # Define the Docker command to run the SQLite query inside the container
            command = [
                "docker", "run", "-i", "--rm", "-v", f"{os.getcwd()}:/data", 
                "theosotr/sqlite3-test", f"/usr/bin/sqlite3-3.26.0", "/data/test.db"
            ]
            
            print("Executing query:\n", query)
            
            result = subprocess.run(
                command, input=query, text=True, capture_output=True, check=True
            )

            print("Query Result:", result.stdout)
            print("====End of Query Result====")

            if result.returncode != 0:
                return BUG_TYPES[0], result.stderr
            
            return BUG_TYPES[1] if self.pivot_missing(result.stdout) else None, result.stdout

        except Exception as e:
            return BUG_TYPES[0], str(e)

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
            print(f"Starting the {self.sqlite_container_name} container...")
            subprocess.run(['docker', 'compose', 'up', '-d'])
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
    query = """
        CREATE TABLE IF NOT EXISTS t0 ( c0 INT );
        INSERT INTO t0 ( c0 ) VALUES (1);
        SELECT * FROM t0 WHERE 1 = 1;
    """

    # Run the query on version 3.39.4 container (or another version if needed)
    result = query_runner.run(query, version="3.39.4")
    print("Query execution result:", result)


# # Run the intersting queries with the engine

# import sqlite3
# import subprocess
# import time
# import os

# class QueryRunner:
#     def __init__(self, sqlite_container_name='sqlite3-container'):
#         # The SQLite container name (you can modify if needed)
#         self.sqlite_container_name = sqlite_container_name

#     def run(self, query, version, database='/sqlite/test.db'):
#         """
#         Runs the given query on the SQLite engine.

#         :param query: The SQL query to run.
#         :param version: The SQLite version to use (to choose the container).
#         :param database: The SQLite database file to connect to (default: /sqlite/test.db).
#         :return: The result of the query or error message.
#         """
#         try:
#             # Establishing the connection
#             print(f"Connecting to SQLite database at {database} using version {version}...")
            
#             # If we're running this inside a Docker container, connect to the SQLite instance in the container
#             conn = sqlite3.connect(database)
#             cursor = conn.cursor()

#             # Running the provided query
#             print(f"Running query: {query}")
#             cursor.execute(query)

#             # Commit if necessary (e.g., for INSERT, UPDATE, DELETE)
#             conn.commit()

#             # Fetching the result if it's a SELECT query
#             if query.strip().lower().startswith("select"):
#                 result = cursor.fetchall()
#                 print("Query Result:", result)
#             else:
#                 result = "Query executed successfully."

#             # Closing the connection
#             cursor.close()
#             conn.close()
            
#             return result

#         except sqlite3.Error as e:
#             print(f"SQLite error: {e}")
#             return f"Error executing query: {e}"

#         except Exception as e:
#             print(f"Error: {e}")
#             return f"An unexpected error occurred: {e}"

#     def check_container_status(self):
#         """
#         Check if the SQLite Docker container is running.
#         """
#         try:
#             # Use Docker command to check if the container is running
#             result = subprocess.run(
#                 ['docker', 'ps', '-q', '-f', f'name={self.sqlite_container_name}'],
#                 stdout=subprocess.PIPE,
#                 stderr=subprocess.PIPE
#             )
#             return result.stdout.decode().strip() != ''
#         except subprocess.SubprocessError as e:
#             print(f"Error checking container status: {e}")
#             return False

#     def start_container(self):
#         """
#         Starts the SQLite container if it's not running.
#         """
#         if not self.check_container_status():
#             print(f"Starting the {self.sqlite_container_name} container...")
#             subprocess.run(['docker', 'compose', 'up', '-d'])
#             # Wait a bit for the container to initialize
#             time.sleep(5)
#         else:
#             print(f"Container {self.sqlite_container_name} is already running.")
            
# # Example usage:
# if __name__ == "__main__":
#     query_runner = QueryRunner()

#     # Ensure the container is running
#     query_runner.start_container()

#     # Example query
#     query = """
#         CREATE TABLE IF NOT EXISTS t0 ( c0 INT );
#         INSERT INTO t0 ( c0 ) VALUES (1);
#         SELECT * FROM t0 WHERE 1 = 1;
#     """

#     # Run the query on version 3.39.4 container (or another version if needed)
#     result = query_runner.run(query, version="3.39.4")
#     print("Query execution result:", result)