from code.parser import SQLParser

def delta_debugging(token_tree, validator):
    parser = SQLParser()
    
    n = 2
    while len(token_tree) >= 1:
        chunk_len = len(token_tree) // n
        if chunk_len == 0:
            break

        some_progress = False

        for i in range(n):
            
            trial = token_tree[:i * chunk_len] + token_tree[(i + 1) * chunk_len:]
            
            if validator(trial):
                token_tree = trial
                n = max(n - 1, 2)
                some_progress = True
                break

        if not some_progress:
            if n >= len(token_tree):
                break
            n = min(n * 2, len(token_tree))

    return token_tree