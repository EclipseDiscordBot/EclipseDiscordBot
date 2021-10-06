def chunk_based_on_size(lst, n):
    for x in range(0, len(lst), n):
        each_chunk = lst[x: n + x]

        if len(each_chunk) < n:
            each_chunk = each_chunk + [None for y in range(n - len(each_chunk))]
        yield each_chunk
