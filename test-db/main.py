# Main file
import random
import argparse

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner

from config import BUG_TYPES, VERSIONS

def main(version):
    generator = QueryGenerator()
    recorder = BugRecorder()
    runner = QueryRunner()
    query = generator.generate_query()
    result = runner.run(query, version)
    if result in BUG_TYPES:
        recorder.report_bug(query, version)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process runs from a specified folder.")
    parser.add_argument("-v", "--version", default=VERSIONS, help="Version of the SQL engine to test. If not set, both versions are tested.")
    args = parser.parse_args()

    main(args.version)