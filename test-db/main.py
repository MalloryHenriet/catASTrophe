# import argparse
# import subprocess
# import os
# from querie_gen import QueryGenerator
# from record_bug import BugRecorder
# from querie_run import QueryRunner
# from database_gen import DatabaseGenerator
# from config import VERSIONS, SQL_CLAUSES
# from utils import update_count_clauses, get_freq_clauses, get_expression_depth, get_validity

# def start_docker_compose():
#     try:
#         print("Starting Docker Compose...")
#         result = subprocess.run(['docker-compose', 'up', '-d'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         print("Docker Compose started successfully.")
#         print(result.stdout.decode())
#     except subprocess.CalledProcessError as e:
#         print("Error starting Docker Compose:")
#         print(e.stderr.decode())
#         exit(1)

# def initialize_database_in_container(init_sql_path, db_path='/data/test.db'):
#     print(f"Initializing the database in container using {init_sql_path}...")
#     host_db_path = os.path.join(os.getcwd(), "shared", "test.db")
#     if os.path.exists(host_db_path):
#         print("Removing existing test.db to prevent conflicts...")
#         os.remove(host_db_path)

#     command = [
#         "docker", "exec", "-i", "sqlite3-container",
#         "sqlite3", db_path
#     ]

#     try:
#         with open(init_sql_path, 'r', encoding='utf-8') as f:
#             sql_script = f.read()

#         result = subprocess.run(
#             command, input=sql_script, text=True, capture_output=True, check=True
#         )
#         print("Database initialized successfully.")
#         if result.stdout:
#             print("SQLite output:", result.stdout)

#     except subprocess.CalledProcessError as e:
#         print("Failed to initialize database in container:")
#         print("STDOUT:", e.stdout)
#         print("STDERR:", e.stderr)
#         exit(1)

# def main(version):
#     sql_clauses_count = {clause: [] for clause in SQL_CLAUSES}
#     expression_depth = []
#     query_validity = []

#     start_docker_compose()
#     query_generator = QueryGenerator()
#     recorder = BugRecorder()
#     runner = QueryRunner()
#     database_generator = DatabaseGenerator()
#     database = database_generator.generate_database()

#     initialize_database_in_container(database)

#     for _ in range(3):
#         pivot, table_name = database_generator.choose_pivot()
#         print(pivot)

#         query = query_generator.generate_query_for_pivot(pivot, table_name)

#         sql_clauses_count = update_count_clauses(query, sql_clauses_count)
#         expression_depth.append(get_expression_depth(query))
#         query_validity.append(get_validity(query))

#         bug_type, result = runner.run(query.sql(), version, database)
#         print(result)
#         if bug_type:
#             print("I have a bug")
#             recorder.report_bug(query.sql(), version, bug_type)

#     print(f"Frequency per clauses: {get_freq_clauses(sql_clauses_count)}")
#     print(f"Average Expression Depth: {sum(expression_depth) / len(expression_depth)}")
#     print(f"Query Validity: {sum(query_validity) / len(query_validity)}")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
#     parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
#     args = parser.parse_args()

#     main(args.version)


# # Main file
import argparse

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator
import subprocess
import os

from config import VERSIONS, SQL_CLAUSES
from utils import update_count_clauses, get_freq_clauses, get_expression_depth, get_validity


def start_docker_compose():
    try:
        # Run docker-compose up in the background
        print("Starting Docker Compose...")
        result = subprocess.run(['docker', 'compose', 'up', '-d','--build' ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Docker Compose started successfully.")
        print(result.stdout.decode())  # Optional: Print the output from the command
    except subprocess.CalledProcessError as e:
        print("Error starting Docker Compose:")
        print(e.stderr.decode())  # Optional: Print the error output
        exit(1)


def initialize_database_in_container(version, init_sql_path, db_path='/data/test.db'):
    print(f"Initializing the database in container using {init_sql_path}...")



    # host_db_path = os.path.join(os.getcwd(), "test.db")
    # if os.path.exists(host_db_path):
    #     print("Removing existing test.db to prevent conflicts...")
    #     os.remove(host_db_path)

    db_file = os.path.join(os.getcwd(), 'shared', 'test.db')
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Removed existing test.db")

    # command = [
    #         "docker", "run", "--platform", "linux/amd64", "-i", "--rm",
    #         "-v", f"{os.getcwd()}:/data",
    #         "theosotr/sqlite3-test",
    #         "/home/test/sqlite/sqlite3", db_path
    #     ]
    command = [
        "docker", "exec", "-i", "sqlite3-container",
        "/home/test/sqlite/sqlite3", db_path
    ]

    try:
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        result = subprocess.run(
            command, input=sql_script, text=True, capture_output=True, check=True
        )
        print("Database initialized successfully.")
        if result.stdout:
            print("SQLite output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Failed to initialize database in container:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        exit(1)




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
    initialize_database_in_container(version, database)

    # PQS Loop
    for _ in range(5):
        pivot, table_name = database_generator.choose_pivot()
        print(pivot)

        query = query_generator.generate_query_for_pivot(pivot, table_name)
        #print(query)

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)