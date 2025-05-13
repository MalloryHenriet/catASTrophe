# docker_utils.py

import subprocess
import os

def start_docker_compose():
    try:
        print("Starting Docker Compose...")
        result = subprocess.run(
            ['docker', 'compose', 'up', '-d', '--build'],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        print("Docker Compose started successfully.")
        print(result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error starting Docker Compose:")
        print(e.stderr.decode())
        exit(1)

def initialize_database_in_container(version, init_sql_path, db_path='/data/test.db'):
    print(f"Initializing the database in container using {init_sql_path}...")

    db_file = os.path.join(os.getcwd(), 'shared', 'test.db')
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Removed existing test.db")

    command = [
        "docker", "exec", "-i", "sqlite3-container",
        "/home/test/sqlite/sqlite3", db_path
    ]

    try:
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        print("command : ", command)

        result = subprocess.run(
            command, input=sql_script, text=True, capture_output=True, check=True
        )

        print("Database initialized successfully.")
        if result.stdout:
            print("SQLite output:", result.stdout)

    except subprocess.CalledProcessError as e:
        print("Failed to initialize database in container:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        exit(1)
