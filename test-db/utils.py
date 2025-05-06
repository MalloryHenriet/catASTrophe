# Utilities functions
import uuid
import os
from sqlglot import exp
from sqlglot.expressions import ColumnDef, Create, Identifier, DataType, Schema, Table

def create_bug_folder():
    folder_name = "bug_" + uuid.uuid4().hex

    folder_path = "./bugs/" + folder_name

    os.makedirs(folder_path)
    
    return folder_path

def write_file(path, filename, content):
    with open(os.path.join(path, filename), "w") as f:
        f.write(content)

def create_table(table_name, columns):
    print(columns)
    columns_defs = [
        exp.ColumnDef(
            this=exp.Identifier(this=col_name),
            kind=exp.DataType(this=col_type)
        )
        for (col_name, col_type) in columns
    ]
    print(columns_defs)
    create = exp.Create(
        this=Table(this=exp.Identifier(this=table_name)), 
        kind="TABLE",
        expression=exp.Schema(expressions=columns_defs)
    ).sql(dialect="sqlite")
    print(create)

    return create