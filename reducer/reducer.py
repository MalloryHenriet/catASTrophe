#!/usr/bin/env python3

import argparse
import os

from code.reduce_query import reduce_query
from code.utils import prepare_workspace
import time
from code.utils import count_tokens

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
    #query_dir = os.path.dirname(query_file_path)
    query_id = os.path.basename(query_path)
    prepare_workspace(query_path)

    output_path = f"queries/{query_id}/reduced_test.sql"

    start_time = time.time()
    reduce_query(query_path, args.test, output_path)
    end_time = time.time()
    elapsed_time = end_time - start_time

    # original_tokens = count_tokens(f"{query_path}/original_test.sql")
    # reduced_tokens = count_tokens(output_path)

    original_tokens, original_query = count_tokens(f"{query_path}/original_test.sql", return_query=True)
    reduced_tokens, reduced_query = count_tokens(output_path, return_query=True)

    # Print full queries
    print("\n--- Original Query ---")
    print(original_query)

    print("\n--- Reduced Query ---")
    print(reduced_query)


    
    reduction_pct = ((original_tokens - reduced_tokens) / original_tokens) * 100

    # Print evaluation
    print(f"[Evaluation] Reduction Time: {elapsed_time:.2f} seconds")
    print(f"[Evaluation] Original Tokens: {original_tokens}")
    print(f"[Evaluation] Reduced Tokens: {reduced_tokens}")
    print(f"[Evaluation] Quality of Reduction: {reduction_pct:.2f}%")