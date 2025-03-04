% Лабораторная работа № 1.2. «Лексический анализатор
  на основе регулярных выражений»
% 26 февраля 2025 г.
% Вениамин Шемякин, ИУ9-62Б

# Цель работы
Целью данной работы является приобретение навыка разработки простейших лексических анализаторов, 
работающих на основе поиска в тексте по образцу, заданному регулярным выражением.

# Индивидуальный вариант
Географические координаты: начинаются с одного из знаков «S», «E», «N», «W», 
после которых располагается целое десятичное число, за которым может следовать либо точка 
и последовательность десятичных цифр, либо знак «D», за которым следует 
необязательная запись угловых минут (число от 0 до 59, за которым пишется апостроф) 
и угловых секунд (число от 0 до 59, за которым следует двойная кавычка).

# Реализация

```python
import re
import sys


class LexerError(Exception):
    pass


class ErrLexerStop(LexerError):
    pass


class ErrValidationFailed(LexerError):
    pass


class Tag:
    ErrTag = "ERR"
    GeoCoordTag = "GEOCOORD"


tag_to_string = {
    Tag.GeoCoordTag: "GEOCOORD",
    Tag.ErrTag: "ERR",
}


class Token:
    def __init__(self, tag, line, pos, val):
        self.tag = tag
        self.line = line
        self.pos = pos
        self.val = val

    def __str__(self):
        return f"{tag_to_string[self.tag]} ({self.line}, {self.pos}): {self.val}"


class Lexer:
    geo_coord_regexp_start = re.compile(
        r'^([NSEW])(\d{1,3})(?:\.(\d+))?(D(?:([0-5]?\d)\')?(?:([0-5]?\d)")?)? ')
    geo_coord_regexp_full = re.compile(
        r'^([NSEW])(\d{1,3})(?:\.(\d+))?(D(?:([0-5]?\d)\')?(?:([0-5]?\d)")?)?$')

    def __init__(self, lines):
        if not lines:
            raise ErrValidationFailed("Validation failed")
        self.lines = lines
        self.current_line = 0
        self.current_pos = 0

    def create_token(self, tag, line, start, end):
        token = Token(tag, self.current_line + 1,
                      self.current_pos + 1, line[start:end])
        self.current_pos += end - start
        self.lines[self.current_line] = line[end:]
        return token

    def create_error_token(self, line):
        token = Token(Tag.ErrTag, self.current_line +
                      1, self.current_pos + 1, "")
        while line and line[0] != ' ':
            line = line[1:]
            self.current_pos += 1
        self.lines[self.current_line] = line
        return token

    def next_token(self):
        while self.current_line < len(self.lines):
            line = self.lines[self.current_line].lstrip()
            if not line:
                self.current_line += 1
                self.current_pos = 0
                continue

            self.lines[self.current_line] = line
            geo_coord_pos = self.geo_coord_regexp_start.search(line)
            if not geo_coord_pos:
                geo_coord_pos = self.geo_coord_regexp_full.search(line)

            if geo_coord_pos:
                return self.create_token(Tag.GeoCoordTag, line, geo_coord_pos.start(), geo_coord_pos.end())
            else:
                return self.create_error_token(line)

        raise ErrLexerStop("Lexer stopped")


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.txt>")
        return

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    lex = Lexer(lines)

    try:
        while True:
            token = lex.next_token()
            if token.tag == Tag.ErrTag:
                print(f"Syntax error at ({token.line}, {token.pos})")
            else:
                print(token)
    except ErrLexerStop:
        pass
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
```

# Тестирование

Входные данные

```
N40.7128D74'00.60"
E135.0D
W10.5D W10.5D
N45D W10.5D
S12.3456D S23.5505D46'37.24"
E180D59'59"
W179.9999D
W179.9999D70'80"
```

Вывод на `stdout` (если необходимо)

```
Syntax error at (1, 1)
GEOCOORD (2, 1): E135.0D
GEOCOORD (3, 1): W10.5D 
GEOCOORD (3, 8): W10.5D
GEOCOORD (4, 1): N45D 
GEOCOORD (4, 6): W10.5D
GEOCOORD (5, 1): S12.3456D 
Syntax error at (5, 11)
GEOCOORD (6, 1): E180D59'59"
GEOCOORD (7, 1): W179.9999D
Syntax error at (8, 1)
```

# Вывод
В ходе данной лабораторной работы я познакомился с разработкой простейших лексических анализаторов,
а также работой с регулярными выражениями в языке Python. Также мне удалось повторить недосредственное
построение регулярных выражений.