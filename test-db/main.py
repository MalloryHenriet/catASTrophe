# Main file
import random
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

    pivot = database_generator.choose_pivot()

    for _ in range(100000):
        query = query_generator.generate_query_for_pivot(pivot)
        result = runner.run(query, version, database)
        if result in BUG_TYPES:
            recorder.report_bug(query, version)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)