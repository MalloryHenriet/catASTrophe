# Main file
import argparse

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner
from database_gen import DatabaseGenerator

from config import BUG_TYPES, VERSIONS

def main(version):
    query_generator = QueryGenerator()
    recorder = BugRecorder()
    runner = QueryRunner()

    database_generator = DatabaseGenerator()
    database = database_generator.generate_database()

    # PQS Loop
    for _ in range(25):
        pivot = database_generator.choose_pivot()
        print(pivot)
        query = query_generator.generate_query_for_pivot(pivot)
        print(query)
        result = runner.run(query, version, database)
        if result in BUG_TYPES:
            recorder.report_bug(query, version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)