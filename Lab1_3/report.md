% Лабораторная работа № 1.3 «Объектно-ориентированный
  лексический анализатор»
% 5 марта 2025 г.
% Вениамин Шемякин, ИУ9-62Б

# Цель работы
Целью данной работы является приобретение навыка реализации лексического анализатора на 
объектно-ориентированном языке без применения каких-либо средств автоматизации решения задачи 
лексического анализа.

# Индивидуальный вариант
+ Целые числа: последовательности цифр определенной системы счисления, предваренные соответствующим 
  индикатором, определяющим систему счисления (для десятичных чисел — пустой индикатор, для двоичных 
  чисел — «0b», для восьмеричных чисел — «0t», для шестнадцатеричных чисел — «0x», 
  шестнадцатеричные цифры могут быть записаны в любом регистре).
+ Ключевые слова: «and»,«or» без учёта регистра.
+ Знаки операций: «(»,«)».
+ Идентификаторы: последовательности латинских букв, без учёта регистра.
# Реализация

Файл `main.py`
```python
import sys
from enum import Enum, auto

class Position:
    def __init__(self, text):
        self.text = text
        self.line = 1
        self.pos = 1
        self.index = 0

    def Cp(self):
        if self.index < len(self.text):
            return self.text[self.index]
        return None

    def is_whitespace(self):
        return self.Cp() is not None and self.Cp().isspace()

    def is_letter(self):
        return self.Cp() is not None and self.Cp().isalpha()

    def is_digit(self):
        return self.Cp() is not None and self.Cp().isdigit()

    def is_newline(self):
        return self.Cp() == '\n'

    def next(self):
        if self.Cp() == '\n':
            self.line += 1
            self.pos = 1
        else:
            self.pos += 1
        self.index += 1

    def __str__(self):
        return f"({self.line}, {self.pos})"

class Fragment:
    def __init__(self, starting: Position, following: Position):
        self.starting = starting
        self.following = following

    def __str__(self):
        return f"{self.starting}-{self.following}"

class Message:
    def __init__(self, is_error, text):
        self.is_error = is_error
        self.text = text

class DomainTag(Enum):
    BINARYNUM = auto()
    OCTNUM = auto()
    HEXNUM = auto()
    AND = auto()
    OR = auto()
    LPAREN = auto()
    RPAREN = auto()
    IDENT = auto()
    ERR = auto()
    EOP = auto()
    
class Token:
    def __init__(self, tag: DomainTag, start: Position, follow: Position, image: str):
        self.tag = tag
        self.start = start
        self.follow = follow
        self.image = image

    def __str__(self):
        return f"{tag_to_string(self.tag)} {self.start}-{self.follow}: {self.image}"

class NumberToken(Token):
    def __init__(self, base: int, image: str, start: Position, follow: Position):
        super().__init__("NUMBER", start, follow, image)
        self.value = int(image, base) if base == 10 else int(image[2:], base)

    def __str__(self):
        return f"NUMBER {self.start}-{self.follow}: {self.value}"

class IdentToken(Token):
    def __init__(self, code: int, image: str, start: Position, follow: Position):
        super().__init__("IDENT", start, follow, image)
        self.code = code

    def __str__(self):
        return f"IDENT {self.start}-{self.follow}: {self.image} ({self.code})"

class SpecToken(Token):
    def __init__(self, tag: str, image: str, start: Position, follow: Position):
        super().__init__(tag, start, follow, image)

    def __str__(self):
        return f"{self.tag} {self.start}-{self.follow}: {self.image}"

class EOPToken(Token):
    def __init__(self, start: Position, follow: Position):
        super().__init__("EOP", start, follow, "")

    def __str__(self):
        return f"EOP {self.start}-{self.follow}"

class ErrorToken(Token):
    def __init__(self, start: Position, follow: Position, image: str):
        super().__init__(DomainTag.ERR, start, follow, image)

    def __str__(self):
        return f"ERROR {self.start}-{self.follow}: {self.image}"

tag_to_string = {
    DomainTag.IDENT: "IDENT",
    DomainTag.BINARYNUM: "BINARYNUM",
    DomainTag.OCTNUM: "OCTNUM",
    DomainTag.HEXNUM: "HEXNUM",
    DomainTag.LPAREN: "LPAREN",
    DomainTag.RPAREN: "RPAREN",
    DomainTag.AND: "AND",
    DomainTag.OR: "OR",
    DomainTag.EOP: "EOP",
    DomainTag.ERR: "ERR",
}

class Compiler:
    def __init__(self):
        self.messages = []
        self.name_codes = {}
        self.names = []

    def add_name(self, name):
        if name in self.name_codes:
            return self.name_codes[name]
        code = len(self.names)
        self.names.append(name)
        self.name_codes[name] = code
        return code

    def get_name(self, code):
        return self.names[code]

    def add_message(self, is_error, position: Position, text):
        self.messages.append((is_error, position, text))

    def output_messages(self):
        for is_error, position, text in self.messages:
            print(f"{'Error' if is_error else 'Warning'} {position}: {text}")

class Scanner:
    def __init__(self, compiler: Compiler, program):
        self.compiler = compiler
        self.program = program
        self.position = Position(program)

    def next_token(self):
        while self.position.Cp() is not None:
            while self.position.is_whitespace():
                self.position.next()

            start_pos = Position(self.program)
            start_pos.line = self.position.line
            start_pos.pos = self.position.pos
            start_pos.index = self.position.index

            char = self.position.Cp()
            if char is None:
                self.position.next()
            elif char.isdigit():
                return self.scan_number(start_pos)
            elif char.isalpha():
                return self.scan_identifier(start_pos)
            elif char in {'(', ')'}:
                return self.scan_operator(start_pos)
            else:
                error_pos = Position(self.program)
                error_pos.line = self.position.line
                error_pos.pos = self.position.pos
                error_pos.index = self.position.index

                self.compiler.add_message(True, error_pos, f"Unexpected character: {char}")
                self.skip_until_whitespace()
                continue

        return EOPToken(self.position, self.position)

    def skip_until_whitespace(self):
        while self.position.Cp() is not None and not self.position.is_whitespace():
            self.position.next()

    def scan_number(self, start_pos):
        base = 10
        if self.program[self.position.index:self.position.index+2].lower() == '0b':
            base = 2
            self.position.next()
            self.position.next()
        elif self.program[self.position.index:self.position.index+2].lower() == '0t':
            base = 8
            self.position.next()
            self.position.next()
        elif self.program[self.position.index:self.position.index+2].lower() == '0x':
            base = 16
            self.position.next()
            self.position.next()

        if base != 16:
            while self.position.Cp() is not None and self.position.Cp().isdigit():
                self.position.next()
        else:
            while self.position.Cp() is not None and (self.position.Cp().isdigit() or 
            (self.position.Cp().lower() in ('a', 'b','c','d','e','f'))):
                self.position.next()

        number_text = self.program[start_pos.index:self.position.index]
        return NumberToken(base, number_text, start_pos, self.position)

    def scan_identifier(self, start_pos):
        while self.position.Cp() is not None and self.position.Cp().isalpha():
            self.position.next()

        identifier_text = self.program[start_pos.index:self.position.index]
        if identifier_text.lower() == 'and':
            return SpecToken("AND", identifier_text, start_pos, self.position)
        elif identifier_text.lower() == 'or':
            return SpecToken("OR", identifier_text, start_pos, self.position)
        else:
            code = self.compiler.add_name(identifier_text)
            return IdentToken(code, identifier_text, start_pos, self.position)

    def scan_operator(self, start_pos):
        operator = self.position.Cp()
        self.position.next()
        if operator == '(':
            return SpecToken("LPAREN", "(", start_pos, self.position)
        elif operator == ')':
            return SpecToken("RPAREN", ")", start_pos, self.position)

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <file.txt>")
        return

    file_path = sys.argv[1]

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            program = file.read()
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    compiler = Compiler()
    scanner = Scanner(compiler, program)

    token = scanner.next_token()
    while not isinstance(token, EOPToken):
        print(token)
        token = scanner.next_token()
    print(token)
    print("----------------")
    compiler.output_messages()

if __name__ == "__main__":
    main()
```

# Тестирование

Входные данные

```
0b1010 0t75 0x1A 211
variableName
(example or anotherExample AND example)
42 123
And or 

@ff   

```

Вывод на `stdout`

```
NUMBER (1, 1)-(1, 7): 10
NUMBER (1, 8)-(1, 12): 61
NUMBER (1, 13)-(1, 17): 26
NUMBER (1, 18)-(1, 21): 211
IDENT (2, 1)-(2, 13): variableName (0)
LPAREN (3, 1)-(3, 2): (
IDENT (3, 2)-(3, 9): example (1)
OR (3, 10)-(3, 12): or
IDENT (3, 13)-(3, 27): anotherExample (2)
AND (3, 28)-(3, 31): AND
IDENT (3, 32)-(3, 39): example (1)
RPAREN (3, 39)-(3, 40): )
NUMBER (4, 1)-(4, 3): 42
NUMBER (4, 4)-(4, 7): 123
AND (5, 1)-(5, 4): And
OR (5, 5)-(5, 7): or
EOP (8, 2)-(8, 2)
----------------
Error (7, 1): Unexpected character: @
```

# Вывод
В ходе данной лабораторной работы я познакомился с реализацией лексического анализатора без 
использования различных средств автоматизации, а также закрепил знания о структуре каждого из объектов 
(компилятора, сканера и т.д.)