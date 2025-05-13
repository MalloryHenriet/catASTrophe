# import subprocess
# import time
# import os

# class DockerManager:
#     def __init__(self, project_dir, container_name='sqlite3-container', db_file='/sqlite/test.db'):
#         self.project_dir = project_dir  # Directory where docker-compose.yml is located
#         self.container_name = container_name
#         self.db_file = db_file

#     def _run_command(self, command):
#         """Runs a shell command and returns the output."""
#         try:
#             result = subprocess.run(command, capture_output=True, text=True, check=True)
#             return result.stdout
#         except subprocess.CalledProcessError as e:
#             print(f"Error: {e}")
#             return None

#     def start_container(self):
#         """Starts the container using Docker Compose."""
#         print("Starting the Docker container using docker-compose...")
#         command = ["docker-compose", "-f", os.path.join(self.project_dir, 'docker-compose.yml'), "up", "-d"]
#         return self._run_command(command)

#     def stop_container(self):
#         """Stops the container using Docker Compose."""
#         print("Stopping the Docker container...")
#         command = ["docker-compose", "-f", os.path.join(self.project_dir, 'docker-compose.yml'), "down"]
#         return self._run_command(command)

#     def is_container_running(self):
#         """Check if the container is running."""
#         command = ["docker", "ps", "-q", "-f", f"name={self.container_name}"]
#         result = self._run_command(command)
#         return bool(result.strip())

#     def execute_sqlite_query(self, query):
#         """Executes an SQLite query inside the container."""
#         if not self.is_container_running():
#             print(f"Error: Container {self.container_name} is not running.")
#             return None
        
#         command = [
#             "docker", "exec", "-i", self.container_name,
#             "sqlite3", self.db_file, query
#         ]
#         return self._run_command(command)

#     def create_database(self):
#         """Creates a database inside the container."""
#         print("Creating a new SQLite database...")
#         query = "CREATE TABLE IF NOT EXISTS my_table (id INTEGER PRIMARY KEY, name TEXT);"
#         return self.execute_sqlite_query(query)

#     def insert_sample_data(self):
#         """Inserts sample data into the SQLite database."""
#         print("Inserting sample data into the database...")
#         query = "INSERT INTO my_table (name) VALUES ('Alice'), ('Bob'), ('Charlie');"
#         return self.execute_sqlite_query(query)

#     def query_sample_data(self):
#         """Queries sample data from the SQLite database."""
#         print("Querying sample data from the database...")
#         query = "SELECT * FROM my_table;"
#         return self.execute_sqlite_query(query)

# if __name__ == "__main__":
#     # Define the project directory (where docker-compose.yml is located)
#     project_dir = "/test-db"  # Change this to your project directory path

#     # Initialize DockerManager
#     docker_manager = DockerManager(project_dir)

#     # Start container
#     docker_manager.start_container()
#     time.sleep(5)  # Wait for the container to fully start

#     # Create database and insert sample data
#     docker_manager.create_database()
#     docker_manager.insert_sample_data()

#     # Query data from the database
#     output = docker_manager.query_sample_data()
#     print(f"Query output:\n{output}")

#     # Stop the container
#     docker_manager.stop_container()


# =========
# import docker

# # Find python Docker SDK here : https://docker-py.readthedocs.io/en/stable/containers.html
# client = docker.from_env()

# ======
# import docker

# # Find python Docker SDK here : https://docker-py.readthedocs.io/en/stable/containers.html
# client = docker.from_env()