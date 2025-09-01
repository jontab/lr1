def generate_unique_symbol(base: str, pool: set[str]) -> str:
    s = base
    i = 0
    while s in pool:
        i = i + 1
        s = f"{base}{i}"
    return s
