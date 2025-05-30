import argparse

from code.reduce_query import reduce_query

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
    
    reduce_query(args.query, args.test)