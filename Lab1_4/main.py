import sys
from enum import Enum, auto

# 0 — буква, 1 — цифра, 2 — 'g', 3 — 'o', 4 — 't',
# 5 — 's', 6 — 'u', 7 — 'b', 8 — '\\', 9 — '(',
# 10 — ')', 11 — пробельный символ, 12 — перевод строки, 13 — прочие)
AUTOMATA = [
    [1,  2,  5,  1,  1,  1,  1,  1,  3, -1, -1, 14, 14, -1],  # 0
    [1,  1,  1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1],  # 1 идентификаторы
    [-1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 2 числа
    [-1, -1, -1, -1, -1, -1, -1, -1,  4, 12, 13, -1, -1, -1],  # 3 начало комментария
    [4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4,  4, -1,  4],  # 4 комментарий (до '\n')
    [1,  1,  1,  6,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1],  # 5 начало goto
    [1,  1,  1,  1,  7,  9,  1,  1, -1, -1, -1, -1, -1, -1],  # 6 обработка goto/gosub
    [1,  1,  1,  8,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1],  # 7 обработка goto/gosub
    [1,  1,  1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1],  # 8 обработка goto/gosub
    [1,  1,  1,  1,  1,  1, 10,  1, -1, -1, -1, -1, -1, -1],  # 9 начало gosub
    [1,  1,  1,  1,  1,  1,  1, 11, -1, -1, -1, -1, -1, -1],  # 10 обработка gosub
    [1,  1,  1,  1,  1,  1,  1,  1, -1, -1, -1, -1, -1, -1],  # 11 обработка gosub
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 12 левая скобка "\("
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],  # 13 правая скобка "\)"
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 14, 14, -1],  # 14 пробелы и конец строки
]

FINAL = [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

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
    IDENT       = 1
    NUMBER      = 2
    GOTO        = 8
    COMMENT     = 4
    IDENT1      = 5
    IDENT2      = 6
    IDENT3      = 7
    IDENT4      = 9
    IDENT5      = 10
    GOSUB       = 11
    LPAREN      = 12
    RPAREN      = 13
    ERR         = 3
    EOP         = 9 
    WHITESPACE  = 14

class Token:
    def __init__(self, tag: DomainTag, start: Position, follow: Position):
        self.tag = tag
        self.start = start
        self.follow = follow

    def __str__(self):
        return f"{tag_to_string.get(self.tag, self.tag.name)} {self.start}-{self.follow}"

class NumberToken(Token):
    def __init__(self, image: str, start: Position, follow: Position):
        super().__init__(DomainTag.NUMBER, start, follow)
        self.image = image
        self.value = int(image)

    def __str__(self):
        return f"NUMBER {self.start}-{self.follow}: {self.image}"

class IdentToken(Token):
    def __init__(self, image: str, code: int, start: Position, follow: Position):
        super().__init__(DomainTag.IDENT, start, follow)
        self.image = image
        self.code = code

    def __str__(self):
        return f"IDENT {self.start}-{self.follow}: {self.image}"

class SpecToken(Token):
    def __init__(self, tag: DomainTag, start: Position, follow: Position):
        super().__init__(tag, start, follow)

    def __str__(self):
        return f"{tag_to_string.get(self.tag, self.tag.name)} {self.start}-{self.follow}"

class CommentToken(Token):
    def __init__(self, start: Position, follow: Position, image):
        super().__init__(DomainTag.COMMENT, start, follow)
        self.image = image

    def __str__(self):
        return f"COMMENT {self.start}-{self.follow}: {self.image}"

class EOPToken(Token):
    def __init__(self, start: Position, follow: Position):
        super().__init__(DomainTag.EOP, start, follow)

    def __str__(self):
        return f"EOP {self.start}-{self.follow}"

class ErrorToken(Token):
    def __init__(self, start: Position, follow: Position):
        super().__init__(DomainTag.ERR, start, follow)

    def __str__(self):
        return f"ERROR {self.start}-{self.follow}"

tag_to_string = {
    DomainTag.IDENT: "IDENT",
    DomainTag.NUMBER: "NUMBER",
    DomainTag.GOTO: "GOTO",
    DomainTag.GOSUB: "GOSUB",
    DomainTag.LPAREN: "LPAREN",
    DomainTag.RPAREN: "RPAREN",
    DomainTag.COMMENT: "COMMENT",
    DomainTag.EOP: "EOP",
    DomainTag.ERR: "ERR",
}

class Automata:
    def __init__(self, automat, final):
        self.automat = automat
        self.final = final

    def next(self, position: Position, state: int) -> int:
        s = position.Cp()
        if s is None:
            return -1
        if s == 'g':
            return self.automat[state][2]
        if s == 'o':
            return self.automat[state][3]
        if s == 't':
            return self.automat[state][4]
        if s == 's':
            return self.automat[state][5]
        if s == 'u':
            return self.automat[state][6]
        if s == 'b':
            return self.automat[state][7]
        if s.isalpha():
            return self.automat[state][0]
        if s.isdigit():
            return self.automat[state][1]
        if s == '\\':
            return self.automat[state][8]
        if s == '(':
            return self.automat[state][9]
        if s == ')':
            return self.automat[state][10]
        if s == '\n':
            return self.automat[state][12]
        if s.isspace():
            return self.automat[state][11]
        return self.automat[state][13]

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

    def get_idents(self):
        print("IDENTS")
        for i, nm in enumerate(self.names):
            print(f"{i}: {nm}")

class Scanner:
    def __init__(self, compiler: Compiler, program: str):
        self.compiler = compiler
        self.program = program
        self.position = Position(program)
        self.automata = Automata(AUTOMATA, FINAL)

    def next_token(self):
        while True:
            if self.position.Cp() is None:
                return EOPToken(self.position, self.position)

            start_pos = Position(self.position.text)
            start_pos.line = self.position.line
            start_pos.pos  = self.position.pos
            start_pos.index = self.position.index

            current_state = 0
            last_final = -1
            last_pos = None

            while True:
                nxt = self.automata.next(self.position, current_state)
                if nxt == -1:
                    break
                current_state = nxt
                self.position.next()

                if current_state in self.automata.final:
                    last_final = current_state
                    last_pos = Position(self.position.text)
                    last_pos.line = self.position.line
                    last_pos.pos  = self.position.pos
                    last_pos.index = self.position.index

            if last_final == -1:
                if self.position.Cp() is not None:
                    self.position.next()
                return ErrorToken(start_pos, self.position)

            recognized_text = self.program[start_pos.index:last_pos.index]
            if last_final == 14:
                continue

            return self.ret_token(last_final, start_pos, last_pos, recognized_text)

    def ret_token(self, st: int, start: Position, end: Position, word: str):
        tag = DomainTag(st)

        if tag in [DomainTag.IDENT, DomainTag.IDENT1, DomainTag.IDENT2,
                   DomainTag.IDENT3, DomainTag.IDENT4, DomainTag.IDENT5]:
            code = self.compiler.add_name(word)
            return IdentToken(word, code, start, end)

        if tag == DomainTag.NUMBER:
            return NumberToken(word, start, end)

        if tag == DomainTag.COMMENT:
            return CommentToken(start, end, word[2:])

        if tag == DomainTag.GOTO:
            return SpecToken(DomainTag.GOTO, start, end)

        if tag == DomainTag.GOSUB:
            return SpecToken(DomainTag.GOSUB, start, end)

        if tag == DomainTag.LPAREN:
            return SpecToken(DomainTag.LPAREN, start, end)

        if tag == DomainTag.RPAREN:
            return SpecToken(DomainTag.RPAREN, start, end)

        return ErrorToken(start, end)

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
    compiler.get_idents()
    compiler.output_messages()

if __name__ == "__main__":
    main()
