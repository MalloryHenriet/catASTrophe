
# Main file
import argparse

from docker_utils import start_docker_compose, initialize_database_in_container

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator

from config import VERSIONS, SQL_CLAUSES
from utils import update_count_clauses, get_freq_clauses, get_expression_depth, get_validity



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
#     initialize_database_in_container(version, database)

#     # PQS Loop
#     for _ in range(5):
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


#     print(f"Frquency per clauses: {get_freq_clauses(sql_clauses_count)}")
#     print(f"Average Expression Depth: {sum(expression_depth) / len(expression_depth)}")
#     print(f"Query Validity: {sum(query_validity) / len(query_validity)}")

def main(versions):
    sql_clauses_count = {clause: [] for clause in SQL_CLAUSES}
    expression_depth = []
    query_validity = []

    start_docker_compose()
    query_generator = QueryGenerator()
    recorder = BugRecorder()
    database_generator = DatabaseGenerator()
    database = database_generator.generate_database()

    results = {}

    # Generate one query at a time and run it across all versions
    for _ in range(5):
        pivot, table_name = database_generator.choose_pivot()
        print(f"Using pivot: {pivot}")
        query = query_generator.generate_query_for_pivot(pivot, table_name)

        # Stats
        sql_clauses_count = update_count_clauses(query, sql_clauses_count)
        expression_depth.append(get_expression_depth(query))
        query_validity.append(get_validity(query))

        query_sql = query.sql()

        for version in versions:
            initialize_database_in_container(version, database)
            runner = QueryRunner(version)
            bug_type, result = runner.run(query_sql)

            print(f"--- SQLite {version} Output ---")
            print(result)
            results[version] = result

            if bug_type:
                print("Bug detected!")
                recorder.report_bug(query_sql, version, bug_type)

        # Compare outputs
        v0, v1 = versions
        if results[v0] != results[v1]:
            print(f"\n❗ Output mismatch between {v0} and {v1}")
            print(f"{v0}:\n{results[v0]}")
            print(f"{v1}:\n{results[v1]}")
        else:
            print(f"✅ Output is consistent across {v0} and {v1}")

    # Final stats
    print(f"\nFrequency per clauses: {get_freq_clauses(sql_clauses_count)}")
    print(f"Average Expression Depth: {sum(expression_depth) / len(expression_depth)}")
    print(f"Query Validity: {sum(query_validity) / len(query_validity)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run queries against multiple SQLite versions.")
    parser.add_argument(
        "-v", "--version", nargs="*", default=VERSIONS,
        help="List of SQLite versions to test, e.g., -v 3.26.0 3.39.4"
    )
    args = parser.parse_args()
    main(args.version)
