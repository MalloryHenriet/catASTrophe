def delta_debugging(tokens, validator):
    if not validator(tokens):
        print("[Error] Initial input does not trigger bug. Abort.")
        return tokens

    n = 2
    while len(tokens) >= 2:
        chunk_size = len(tokens) // n
        subsets = [tokens[i * chunk_size : (i + 1) * chunk_size] for i in range(n)]
        
        # Try removing each subset
        for i in range(n):
            complement = [t for j, s in enumerate(subsets) if j != i for t in s]
            if validator(complement):
                tokens = complement
                n = max(n - 1, 2)
                break
        else:
            if n >= len(tokens):
                break
            n = min(n * 2, len(tokens))

    return tokens