%{
    #include <iostream>
    #include <map>
    #include <string>
    #include <vector>
    #include <cstdlib>
    using namespace std;

    enum class Tag {
        STRING,
        NUMBER,
        IDENT,
        EOP,
    };

    map<string, int> idents;
    map<Tag, string> tags = {
        {Tag::STRING, "STRING"},
        {Tag::NUMBER, "NUMBER"},
        {Tag::IDENT, "IDENT"},
        {Tag::EOP, "EOP"}
    };
    vector<string> errors;

    struct Position {
        int line,
            pos,
            index;
    };

    void print_position(struct Position *position) {
        cout << "(" << position->line << ", " << position->pos << ")";
    }

    ostream& operator<<(ostream &out, const struct Position &position) {
        return out << "(" << position.line << ", " << position.pos << ")";
    }

    struct Fragment {
        struct Position starting, following;
    };

    typedef Fragment YYLTYPE;

    void print_fragment(struct Fragment *fragment) {
        cout << fragment->starting << "-" << fragment->following;
    }

    struct token {
        long long int_value;
        string str_value;
        int ident_count;

        token() {
            int_value = 0;
            str_value = "";
            ident_count = 0;
        }
    };

    int add_ident(string id) {
        auto it = idents.find(id);
        if (it != idents.end()) {
            return it->second;
        }
        int k = idents.size();
        idents[id] = k;
        return k;
    }

    typedef struct token YYSTYPE;

    int continued;
    struct Position current;
    #define YY_USER_ACTION {             \
           int i;                         \
           if (!continued)                \
               yylloc->starting = current;    \
           continued = 0;                 \
                                          \
           for (i = 0; i < yyleng; i++) {  \
               if (yytext[i] == '\n') {    \
                   current.line++;         \
                   current.pos = 1;        \
               } else {                    \
                   current.pos++;          \
               }                           \
               current.index++;            \
           }                               \
           yylloc->following = current;    \
       }
    
    void init_scanner(char *program) {
        continued = 0;
        current.line = 1;
        current.pos = 1;
        current.index = 0;
        yy_scan_string(program);
    }

    void add_error(string text) {
        errors.push_back("Error (" + to_string(current.line) + ", " + to_string(current.pos) + "): " + text);
    }
%}

%option noyywrap bison-bridge bison-locations

%x REGULAR LITERAL

LETTER [a-zA-Z]
DIGIT [0-9]
IDENT {LETTER}({LETTER}|{DIGIT})*
NUMBER (0|(1)+)

%%

[\n\t ]+

{IDENT} {
    yylval->str_value = yytext;
    yylval->ident_count = add_ident(yytext);
    return static_cast<int>(Tag::IDENT);
}

{NUMBER} {
    yylval->int_value = yytext[0] == '0' ? 0 : yyleng;
    return static_cast<int>(Tag::NUMBER);
}

\" {
    yylval->str_value = "";
    BEGIN(REGULAR);
    continued = 1;
}

@\" {
    yylval->str_value = "";
    BEGIN(LITERAL);
    continued = 1;
}

<REGULAR>\\n {
    yylval->str_value.append("\n");
    continued = 1;
}
<REGULAR>\\t {
    yylval->str_value.append("\t");
    continued = 1;
}
<REGULAR>\\\" {
    yylval->str_value.append("\"");
    continued = 1;
}
<LITERAL>\"\" {
    yylval->str_value.append("\"");
    continued = 1;
}

<REGULAR,LITERAL>\" {
    BEGIN(0);
    return static_cast<int>(Tag::STRING);
}

<REGULAR>\n {
    add_error("bad symbol \\n");
    BEGIN(0);
}

<LITERAL>\n {
    yylval->str_value.append("\n");
    continued = 1;
}

<REGULAR,LITERAL>. {
    yylval->str_value.append(string(1, yytext[0]));
    continued = 1;
}

<REGULAR,LITERAL><<EOF>> {
    add_error("end of program found, expected: \"");
    BEGIN(0);
}

. {
    add_error("unknown character " + string(yytext));
}
<<EOF>> return static_cast<int>(Tag::EOP);
%%

int main() {
    YYSTYPE value;
    YYLTYPE coords;
    int tag;

    FILE *input = fopen("test.txt", "r");
    if (!input) {
        cerr << "Cannot open file test.txt" << "\n";
        return 1;
    }
    fseek(input, 0, SEEK_END);
    long size = ftell(input);
    rewind(input);
    char *buf = (char*)malloc(sizeof(char) * (size + 1));
    fread(buf, sizeof(char), size, input);
    buf[size] = '\0';
    fclose(input);

    init_scanner(buf);

    do {
        tag = yylex(&value, &coords);
        cout << tags[static_cast<Tag>(tag)] << " ";
        print_fragment(&coords);
        cout << ": ";

        if (static_cast<Tag>(tag) == Tag::STRING)
            cout << value.str_value << "\n";
        else if (static_cast<Tag>(tag) == Tag::NUMBER)
            cout << value.int_value << "\n";
        else if (static_cast<Tag>(tag) == Tag::IDENT)
            cout << value.str_value << "\n";
        else
            cout << "\n";
    } while (static_cast<Tag>(tag) != Tag::EOP);

    cout << "\nIdents:\n";
    for (auto &id : idents) {
        cout << id.second << ": " << id.first << "\n";
    }

    cout << "\nErrors:\n";
    for (auto &e : errors) {
        cout << e << "\n";
    }
    free(buf);
    return 0;
}
