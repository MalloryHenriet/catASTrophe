# Main file
import random

from querie_gen import QueryGenerator
from record_bug import BugRecorder
from querie_run import QueryRunner

from config import BUG_TYPES, VERSIONS

def main():
    version = random.choice(VERSIONS)
    generator = QueryGenerator()
    recorder = BugRecorder()
    runner = QueryRunner()
    query = generator.generate_query()
    result = runner.run(query, version)
    if result in BUG_TYPES:
        recorder.report_bug(query, version)

if __name__ == "__main__":
    main()