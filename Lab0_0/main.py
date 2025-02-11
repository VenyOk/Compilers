def parse(program):
    tokens = program.split()
    i = 0

    def parse_articles():
        nonlocal i
        articles = {}
        while i < len(tokens):
            if tokens[i] == 'define':
                i += 1
                if i >= len(tokens):
                    return None
                word = tokens[i]
                i += 1
                body = parse_body()
                if body is None:
                    return None
                if i >= len(tokens) or tokens[i] != 'end':
                    return None
                i += 1
                articles[word] = body
            else:
                break
        return articles

    def parse_body():
        nonlocal i
        body = []
        while i < len(tokens):
            if tokens[i] == 'if':
                i += 1
                if_body = parse_body()
                if if_body is None:
                    return None
                else_part = parse_else_part()
                if else_part is None:
                    return None
                if i >= len(tokens) or tokens[i] != 'endif':
                    return None
                i += 1
                body.append(['if', if_body] + else_part)
            elif tokens[i] == 'else':
                return body
            elif tokens[i] == 'endif':
                return body
            elif tokens[i] == 'end':
                return body
            elif tokens[i].isdigit() or (tokens[i][0] == '-' and tokens[i][1:].isdigit()):
                body.append(int(tokens[i]))
                i += 1
            else:
                body.append(tokens[i])
                i += 1
        return body

    def parse_else_part():
        nonlocal i
        if i < len(tokens) and tokens[i] == 'else':
            i += 1
            else_body = parse_body()
            if else_body is None:
                return None
            return ['else', else_body]
        return []

    articles = parse_articles()
    if articles is None:
        return None

    body = parse_body()
    if body is None:
        return None

    return [articles, body]


"""print(parse("define abs dup 0 < if -1 * endif end 10 abs -10 abs"))
print(parse("1 2 +"))
print(parse("x dup 0 swap if drop -1 endif"))
print(parse("x dup 0 swap if drop -1 else swap 1 + endif"))
print(parse("define word w1 w2 w3"))"""
while True:
    print(parse(input("Введите строку: ").strip()))
