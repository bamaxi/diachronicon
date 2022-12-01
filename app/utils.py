def read_lines(path, mode='r', encoding='utf-8'):
    with open(path, mode, encoding=encoding) as f:
        return [line.strip() for line in f.read().split('\n')]