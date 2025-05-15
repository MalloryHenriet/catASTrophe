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
    container_name = "sqlite3-container"

    binary = {
        "3.26.0": "/usr/bin/sqlite3-3.26.0",
        "3.39.4": "/usr/bin/sqlite3-3.39.4"
    }.get(version)

    if not binary:
        raise ValueError(f"Unsupported version: {version}")

    print(f"Initializing the database using {binary}...")

    db_file = os.path.join(os.getcwd(), 'shared', 'test.db')
    if os.path.exists(db_file):
        os.remove(db_file)
        print("Removed existing test.db")

    command = [
        "docker", "exec", "-i", container_name,
        binary,
        #"/home/test/sqlite/sqlite3",
        db_path
    ]

    try:
        with open(init_sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        subprocess.run(
            command, input=sql_script, text=True, capture_output=True, check=True
        )

        print("Database initialized successfully.")
    

    except subprocess.CalledProcessError as e:
        print("Failed to initialize database in container:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        exit(1)
