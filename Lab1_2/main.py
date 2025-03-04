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
