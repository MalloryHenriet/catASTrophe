# Main file
import argparse
import subprocess
import os
import shutil

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator
import subprocess

from config import VERSIONS, SQL_CLAUSES
from utils import update_count_clauses, get_freq_clauses, get_expression_depth, get_validity

#COVERAGE_DIR = "/sqlite/sqlite-autoconf-3450100"  # Path to SQLite source in the container (or wherever coverage files are generated)
CONTAINER_NAME = "sqlite3-container"  # Name of the container in your docker-compose.yml
COVERAGE_OUT_DIR = "./coverage_out"  # Local directory where coverage data will be copied



def start_docker_compose():
    try:
        # Run docker-compose up in the background
        print("Starting Docker Compose...")
        result = subprocess.run(['docker', 'compose', 'up', '-d'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Docker Compose started successfully.")
        print(result.stdout.decode())  # Optional: Print the output from the command
    except subprocess.CalledProcessError as e:
        print("Error starting Docker Compose:")
        print(e.stderr.decode())  # Optional: Print the error output
        exit(1)

def extract_coverage():
    """
    Extract .gcda files from the Docker container and run gcov.
    """
    print("[*] Extracting coverage data from Docker container...")

    # Path where the gcda files are located inside the container
    coverage_path_in_container = "/home/test/sqlite/"  # Update with the correct path
    local_coverage_dir = COVERAGE_OUT_DIR  # Local directory where coverage data will be copied

    # Ensure the local coverage directory exists
    if not os.path.exists(local_coverage_dir):
        os.makedirs(local_coverage_dir)

    try:
        # Copy the coverage data files (.gcda) from the container to the host machine
        subprocess.run(
            ["docker", "cp", f"{CONTAINER_NAME}:{coverage_path_in_container}", local_coverage_dir], 
            check=True
        )
        print("[*] Coverage data copied successfully.")

        # Run gcov on the extracted files
        print("[*] Running gcov on the extracted files...")

        for root, dirs, files in os.walk(local_coverage_dir):
            for file in files:
                if file.endswith(".c"):  # Only process C source files
                    full_path = os.path.join(root, file)
                    subprocess.run(["gcov", "-b", "-c", full_path], cwd=root)

        print("[✓] Coverage data generated. Check *.gcov files in the coverage_out folder.")

    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Error while extracting coverage: {e}")


def main(version):
    sql_clauses_count = {clause: [] for clause in SQL_CLAUSES}
    expression_depth = []
    query_validity = []

    start_docker_compose()
    query_generator = QueryGenerator()
    recorder = BugRecorder()
    runner = QueryRunner()

    database_generator = DatabaseGenerator()
    database = database_generator.generate_database()

    # PQS Loop
    for _ in range(10):
        pivot, table_name = database_generator.choose_pivot()
        print(pivot)

        query = query_generator.generate_query_for_pivot(pivot, table_name)
        print(query)

        sql_clauses_count = update_count_clauses(query, sql_clauses_count)
        expression_depth.append(get_expression_depth(query))
        query_validity.append(get_validity(query))

        bug_type, result = runner.run(query.sql(), version, database)
        print(result)
        if bug_type:
            print("I have a bug")
            recorder.report_bug(query.sql(), version, bug_type)


    print(f"Frquency per clauses: {get_freq_clauses(sql_clauses_count)}")
    print(f"Average Expression Depth: {sum(expression_depth) / len(expression_depth)}")
    print(f"Query Validity: {sum(query_validity) / len(query_validity)}")
    extract_coverage()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)