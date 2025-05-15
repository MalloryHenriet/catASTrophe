import subprocess
import time
import os

from config import BUG_TYPES
from utils import generate_predicate, extract_predicate_from_ast



class QueryRunner:
    def __init__(self, version, use_gcov=False, sqlite_container_name='sqlite3-container'):
        self.version = version
        self.sqlite_container_name = sqlite_container_name
        self.use_gcov = use_gcov



    def run(self, query, database='/data/test.db'):
        try:
            if not isinstance(query, str):
                raise ValueError("Query must be a string.")

            query_path = os.path.join(os.getcwd(), 'shared', "query.sql")
            with open(query_path, "w", encoding="utf-8") as f:
                f.write(query)

        
            sqlite_binary = {
                "3.26.0": "/usr/bin/sqlite3-3.26.0",
                "3.39.4": "/usr/bin/sqlite3-3.39.4"
            }.get(self.version)

            if not sqlite_binary:
                raise ValueError(f"Unsupported SQLite version: {self.version}")
            
            if self.use_gcov:
            
                docker_cmd = [
                    "docker", "exec", "-i",
                    self.sqlite_container_name,
                    "bash", "-c",
                    "./sqlite3 /data/test.db < /data/query.sql"
                ]

                docker_gcov = [
                    "docker", "exec", "-i",
                    self.sqlite_container_name,
                    "bash", "-c",
                    "gcov -r sqlite3-sqlite3.gcda"
                ]
                
                gcov_result = subprocess.run(docker_gcov, capture_output=True, text=True)
                print("gcov_result: ", gcov_result.stdout)
                print("gcov_result_err: ", gcov_result.stderr)

            else:

                docker_cmd = [
                    "docker", "exec", "-i",
                    self.sqlite_container_name,
                    "bash", "-c",
                    f"{sqlite_binary} {database} < /data/query.sql"
                ]

           
            
            print(f"Executing query on SQLite {self.version}...")
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            print("====End query==== ")
            print("result: ", result.stdout)
            print("====End result==== ")

        
            
            if result.returncode != 0:
                return BUG_TYPES['crash'], result.stderr

            return BUG_TYPES['logic'] if self.pivot_missing(result.stdout, query) else None, result.stdout

        except Exception as e:
            return BUG_TYPES['crash'], str(e)
    
    
    def pivot_missing(self, result_str, pivot):
        return  pivot in result_str
    
    def run_partitioning(self, query, original_result, database='/data/test.db'):
        predicate = extract_predicate_from_ast(query) or generate_predicate(query)
        if predicate == None:
            return True
        
        subquery_sql = f"({query.sql()})"

        true_query = f"SELECT * FROM {subquery_sql} AS sub WHERE {predicate}"
        false_query = f"SELECT * FROM {subquery_sql} AS sub WHERE NOT ({predicate})"
        null_query = f"SELECT * FROM {subquery_sql} AS sub WHERE {predicate} IS NULL"

        print("Query Partitioning")
        print(true_query)
        print(false_query)
        print(null_query)

        true_result = self.run(true_query, database=database)[1]
        false_result = self.run(false_query, database=database)[1]
        null_result = self.run(null_query, database=database)[1]        

        combined_result = true_result + false_result + null_result
        return sorted(combined_result) == sorted(original_result)
    