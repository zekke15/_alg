def my_map(fn, seq):
    if not seq:
        return []
    return [fn(seq[0])] + my_map(fn, seq[1:])

def my_filter(fn, seq):
    if not seq:
        return []
    head, tail = seq[0], my_filter(fn, seq[1:])
    return [head] + tail if fn(head) else tail

def my_reduce(fn, seq, initializer=None):
    if not seq:
        return initializer
    if initializer is None:
        return my_reduce(fn, seq[1:], seq[0])
    return my_reduce(fn, seq[1:], fn(initializer, seq[0]))