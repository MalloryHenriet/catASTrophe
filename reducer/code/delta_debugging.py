#runs delta debugging strategy on the given query and returns the reduced list if valid

from code.parser import SQLParser

def delta_debugging(ast_list, validator):
    #valid = validator(ast_list)
    parser = SQLParser()
    
    print("===Original===: ", parser.to_sql(ast_list))
    n = 2
    while len(ast_list) >= 1:
        chunk_len = len(ast_list) // n
        if chunk_len == 0:
            break

        some_progress = False

        for i in range(n):
            
            trial = ast_list[:i * chunk_len] + ast_list[(i + 1) * chunk_len:]
            query_string = parser.to_sql(trial)
            print("***trial***: ", query_string)
            
            if validator(trial):
                ast_list = trial
                n = max(n - 1, 2)
                some_progress = True
                break

        if not some_progress:
            if n >= len(ast_list):
                break
            n = min(n * 2, len(ast_list))

    print("===Delta=== : ", parser.to_sql(ast_list))
    return ast_list