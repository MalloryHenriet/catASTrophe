import argparse

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
    query_id = args.query.strip("/").split("/")[-1]
    prepare_workspace(query_id)
    
    reduce_query(args.query, args.test)