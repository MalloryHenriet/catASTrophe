
# Main file
import argparse
import time

from docker_utils import start_docker_compose, initialize_database_in_container

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator

from config import VERSIONS, SQL_CLAUSES, BUG_TYPES
from utils import update_count_clauses, get_freq_clauses, get_expression_depth, get_validity, is_ignorable_error

def main(versions, test_flag, runs):
    sql_clauses_count = {clause: [] for clause in SQL_CLAUSES}
    expression_depth = []
    query_validity = []

    if not test_flag:
        start_docker_compose()

    query_generator = QueryGenerator()
    recorder = BugRecorder()
    database_generator = DatabaseGenerator()
    database = database_generator.generate_database()

    results = {}
    total_queries = 0
    start_time = time.time()
    #execution_times = []

    # Generate one query at a time and run it across all versions
    for _ in range(runs):
        pivot, table_name = database_generator.choose_pivot()

        print(f"Using pivot: {pivot}")
        query = query_generator.generate_query_for_pivot(pivot, table_name)
        print(f"Query : {query.sql()}")

        # Stats
        sql_clauses_count = update_count_clauses(query, sql_clauses_count)
        expression_depth.append(get_expression_depth(query))
        query_validity.append(get_validity(query))

        query_sql = query.sql()

        if not test_flag:
            for version in versions:
                initialize_database_in_container(version, database)
                runner = QueryRunner(version)
                #start_time = time.time()
                bug_type, result = runner.run(query_sql)
                #end_time = time.time()
                #execution_times.append(end_time - start_time)

                print(f"--- SQLite {version} Output ---")
                #print(result)
                results[version] = result

                

                
                # if output_3260 != output_3394:
                #     return "LOGIC_BUG", (output_3260, output_3394)

                

                if bug_type:
                    if is_ignorable_error(result) :
                        print("⚠️ Skipping ignorable error GROUP BY before HAVING or column:nan.")
                        continue
                    else:
                        print("Bug detected!")
                        print("HERE 1")
                        recorder.report_bug(query_sql, version, bug_type, stderr_output=result)
                else:
                    partitioning = runner.run_partitioning(query, result, database)
                    if not partitioning:
                        print("HERE 2")
                        #recorder.report_bug(query_sql, version, BUG_TYPES['crash'])

            total_queries += 1
            print("Current iteration: ", total_queries)


            # Compare outputs
            v0, v1 = versions
            if results[v0] != results[v1]:
                print("HERE 3")
                recorder.report_bug(query_sql, v0+v1, BUG_TYPES['logic'], stderr_output=results[v0])
                print(f"\n❗ Output mismatch between {v0} and {v1}")
                print(f"{v0}:\n{results[v0]}")
                print(f"{v1}:\n{results[v1]}")
            else:
                print(f"✅ Output is consistent across {v0} and {v1}")

    elapsed_time = time.time() - start_time
    queries_per_minute = (total_queries / elapsed_time) * 60

    # Final stats
    print(f"\nPerformance: {queries_per_minute:.2f} queries/min")
    print(f"\nFrequency per clauses: {get_freq_clauses(sql_clauses_count)}")
    print(f"Average Expression Depth: {sum(expression_depth) / len(expression_depth)}")
    print(f"Query Validity: {sum(query_validity) / len(query_validity)}")
    #avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
    #print(f"✅ Average Execution Time per Query: {avg_time:.4f} seconds")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run queries against multiple SQLite versions.")
    parser.add_argument(
        "-v", "--version", nargs="*", default=VERSIONS,
        help="List of SQLite versions to test, e.g., -v 3.26.0 3.39.4"
    )
    parser.add_argument("-t", "--test", default=False, help="Print the queries but do not run on docker, use -t True")
    parser.add_argument("-r", "--runs", type=int, default=100, help="Provide the number of runs you want, e.g. -r 100000")
    args = parser.parse_args()
    main(args.version, args.test, args.runs)
