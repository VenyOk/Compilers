% Лабораторная работа № 0.0. Знакомство с компиляцией программ
% 11 февраля 2025 г.
% Вениамин Шемякин, ИУ9-62Б

# Цель работы
Заполнить первую лабораторную, которая проводится до лекции

# Индивидуальный вариант
Требуется написать (любым способом) парсер FORTH-подобного языка, описанный в индивидуальном варианте. 
Парсер может быть представлен не в виде готовой программы, 
а в виде функции, вызываемой из REPL-среды языка программирования.

Парсер должен строить синтаксическое дерево в виде вложенных массивов (списков)
выбранного языка программирования, слова изображаются строками, числа — числами,
управляющие конструкции (их набор зависит от индивидуального варианта) — вложенными списками.

Синтаксическое дерево должно представлять собой пару из словаря, отображающего имена
на определённые пользователем статьи, и основной программы.
Тела статей и основная программа представляются списками. 
Представление управляющих констркций реконструируется по примеру в индивидуальном варианте.

В случае синтаксических ошибок функция разбора должна возвращать 
#f, None, false, undefined, null, nil и т.д. в зависимости от выбранного языка программирования.

Грамматика:

```
<Program>  ::= <Articles> <Body> .
<Articles> ::= <Article> <Articles> | .
<Article>  ::= define word <Body> end .
<Body>     ::= if <Body> <ElsePart> endif <Body>
             | integer <Body> | word <Body> | .
<ElsePart> ::= else <Body> | .
```

# Реализация
```
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


print(parse(input("Введите строку: ").strip()))
```

# Тестирование
```
Введите строку: define abs dup 0 < if -1 * endif end 10 abs -10 abs
[{'abs': ['dup', 0, '<', ['if', [-1, '*']]]}, [10, 'abs', -10, 'abs']]
Введите строку: 1 2 +
[{}, [1, 2, '+']]
Введите строку: x dup 0 swap if drop -1 endif
[{}, ['x', 'dup', 0, 'swap', ['if', ['drop', -1]]]]
```

# Вывод
В ходе выполнения данной лабораторной работы был реализован парсер FORTH-подобного языка
по заданной грамматике с помощью языка Python, также был получен опыт написания парсеров
на этом языке, поскольку до этого писал парсеры только на scheme, java и julia 
(в ходе курса теории формальных языков).