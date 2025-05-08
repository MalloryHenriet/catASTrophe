# Main file
import argparse

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator
import subprocess

from config import BUG_TYPES, VERSIONS


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


def main(version):
    start_docker_compose()
    query_generator = QueryGenerator()
    recorder = BugRecorder()
    runner = QueryRunner()

    database_generator = DatabaseGenerator()
    database = database_generator.generate_database()

    query_crash = "SELECT * FROM non_existing_table WHERE id = (SELECT * FROM another_table);"
    bug_type, result = runner.run(query_crash, version, database)
    if result:
            recorder.report_bug(query_crash, version)

    # PQS Loop
    for _ in range(25):
        pivot, table_name = database_generator.choose_pivot()
        print(pivot)
        query = query_generator.generate_query_for_pivot(pivot, table_name)
        print(query)
        bug_type, result = runner.run(query, version, database)
        if bug_type:
            recorder.report_bug(query, version, bug_type)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)