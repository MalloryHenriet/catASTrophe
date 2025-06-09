from code.parser import SQLParser
from code.simplifier import SQLSimplifier
from code.executor import execute_query
from code.delta_debugging import delta_debugging
from code.utils import get_used_table_column_names, drop_shadowed_statements, drop_unused_insert_statements

REQUIRED_PREFIXES = (
    "CREATE TABLE", "INSERT INTO", "CREATE INDEX", "CREATE VIEW",
    "CREATE TRIGGER", "SET ", "PRAGMA", "ANALYZE", "VACUUM", "CREATE TEMP"
)

def must_keep(statement_str: str) -> bool:
    upper = statement_str.upper().strip()
    return any(upper.startswith(prefix) for prefix in REQUIRED_PREFIXES)

def reduce_query(query_path, test_script, output_path):
    with open(f"{query_path}/original_test.sql", "r") as original_query:
        query_string = original_query.readlines()

    # Parse the query to an AST
    parser = SQLParser()
    token_tree = parser.parse(query_string)
    token_tree_size = sum(len(parser.flatten_tokens(tree)) for tree in token_tree)

    if not token_tree:
        print("No valid statement to reduce")
        return query_string
    
    required_stmts = []
    reducible_stmts = []
    for stmt in token_tree:
        stmt_str = parser.to_sql([stmt]).strip()
        if must_keep(stmt_str):
            required_stmts.append(stmt)
        else:
            reducible_stmts.append(stmt)

    # Validator function
    def validator(expr):
        full_program = required_stmts + expr
        query_string = parser.to_sql(full_program)
        result = execute_query(query_string, test_script, output_path)

        return result == 0
    
    assert validator(reducible_stmts), "Original reducible portion does not trigger the bug."

    # Update Token tree with delta debugging technique
    reduced_token_tree = delta_debugging(reducible_stmts, validator)

    # Second validator function
    def full_control_validator(expr):
        query_string = parser.to_sql(expr)
        result = execute_query(query_string, test_script, output_path)

        return result == 0

    # Hunt required_stmts that are useless
    # ----
    # First, the statements that are not referenced later
    used_tables, used_columns = get_used_table_column_names(reduced_token_tree, parser)

    semantically_used = []
    for stmt in required_stmts:
        stmt_tokens = parser.flatten_tokens(stmt)
        token_texts = {str(tok).lower() for tok in stmt_tokens}

        # Check semantic hints
        likely_unused = not any(
            name in token_texts for name in used_tables.union(used_columns)
        )

        # Validate before dropping
        test_program = semantically_used + reduced_token_tree
        if likely_unused and full_control_validator(test_program):
            continue
        elif not full_control_validator(test_program):
            semantically_used.append(stmt)
        else:
            semantically_used.append(stmt)
    
    if not full_control_validator(semantically_used + reduced_token_tree):
        raise RuntimeError("Bug lost after semantic filtering")
    
    # ----
    # Second, the statements that are verified to be useless
    validated_required = []
    for stmt in semantically_used:
        candidate_required = [s for s in required_stmts if s != stmt]
        if full_control_validator(reduced_token_tree + candidate_required):
            continue
        validated_required.append(stmt)

    if not full_control_validator(validated_required + reduced_token_tree):
        raise RuntimeError("Bug lost after validator-based filtering")
    
    # ----
    # Third, the INSERT that are useless
    used_tables, used_columns = get_used_table_column_names(reduced_token_tree, parser)
    final_required = drop_unused_insert_statements(validated_required, reduced_token_tree, parser, full_control_validator)

    final_tokens = final_required + reduced_token_tree
    final_tokens = drop_shadowed_statements(final_tokens, parser)
    if not full_control_validator(final_tokens):
        raise RuntimeError("Bug lost after shadowed definition cleanup")
    
    # Step: Simplify final token tree
    simplifier = SQLSimplifier(parser, full_control_validator)
    final_tokens = simplifier.simplify(final_tokens)

    # Final validation
    if not full_control_validator(final_tokens):
        raise RuntimeError("Bug lost after simplification pass")

    minimized = parser.to_sql(final_tokens)
    minimzed_token_size = sum(len(parser.flatten_tokens(tree)) for tree in final_tokens)

    if minimized is None:
        return query_string, token_tree_size, minimzed_token_size
    
    with open(output_path, "w") as out:
        out.write(minimized)
    
    return minimized, token_tree_size, minimzed_token_size