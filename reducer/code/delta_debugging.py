def delta_debugging(token_tree, validator):
    n = 2

    while len(token_tree) >= 2:
        chunk_size = len(token_tree) // n
    
        if chunk_size == 0:
            break

        some_progress = False
        
        chunks = []
        # Create the chunks
        for i in range(n):
            start = i * chunk_size
            end = len(token_tree) if i == n - 1 else (i + 1) * chunk_size
            chunks.append(token_tree[start:end])

        # Remove chunk after chunk
        for i in range(n):
            complement = [token for j, chunk in enumerate(chunks) if j != i for token in chunk]
            
            if validator(complement):
                token_tree = complement
                n = max(n - 1, 2)
                some_progress = True
                break

        if not some_progress:
            if n >= len(token_tree):
                break
            n = min(n * 2, len(token_tree))

    return token_tree