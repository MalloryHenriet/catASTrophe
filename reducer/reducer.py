import argparse
import os

from code.reduce_query import reduce_query
from code.utils import prepare_workspace

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reduce bug-triggering SQL queries")
    parser.add_argument(
        "--query",
        help="The query to minimize"
    )
    parser.add_argument(
        "--test",
        help="Arbitrary shell script that checks whether the mininmzed query is still valid"
    )
    args = parser.parse_args()

    # Get the query_id, copy the content of queries-to-minimze/query_id to queries/query_id
    query_path = args.query
    query_id = os.path.basename(query_path)
    prepare_workspace(query_path)

    output_path = f"queries/{query_id}/reduced_test.sql"
    reduce_query(query_path, args.test, output_path)