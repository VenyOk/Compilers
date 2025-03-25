%{
    #include <iostream>
    #include <map>
    #include <string>
    #include <vector>
    #include <cstdlib>
    using namespace std;

    // Инициализируем контейнеры с помощью списка инициализации (C++11)
    map<string, int> idents;
    map<int, string> tags = {
        {1, "STRING"},
        {2, "NUMBER"},
        {3, "IDENT"},
        {0, "EOP"}
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

    struct Fragment {
        struct Position starting, following;
    };

    typedef Fragment YYLTYPE;

    void print_fragment(struct Fragment *fragment) {
        print_position(&fragment->starting);
        cout << "-";
        print_position(&fragment->following);
    }

    struct token {
        int int_value;
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

%x WORD1 WORD2

LETTER [a-zA-Z]
DIGIT [0-9]
IDENT {LETTER}({LETTER}|{DIGIT})*{LETTER}
NUMBER (0|(1)+)

%%

[\n\t ]+

{IDENT} {
    yylval->str_value = yytext;         // сохраняем текст идентификатора
    yylval->ident_count = add_ident(yytext);
    return 3;
}

{NUMBER} {
    yylval->int_value = atoi(yytext);
    return 2;
}

\" {
    yylval->str_value = "";
    BEGIN(WORD1);
    continued = 1;
}

@\" {
    yylval->str_value = "";
    BEGIN(WORD2);
    continued = 1;
}

<WORD1>\\n {
    yylval->str_value.append("\n");
    continued = 1;
}
<WORD1>\\t {
    yylval->str_value.append("\t");
    continued = 1;
}
<WORD1>\\\" {
    yylval->str_value.append("\"");
    continued = 1;
}
<WORD2>\"\" {
    yylval->str_value.append("\"");
    continued = 1;
}

<WORD1>\" {
    BEGIN(0);
    return 1;
}

<WORD2>\" {
    BEGIN(0);
    return 1;
}

<WORD1>\n {
    add_error("unknown symbol \\n");
    BEGIN(0);
}

<WORD2>\n {
    yylval->str_value.append("\n");
    continued = 1;
}

<WORD1>. {
    yylval->str_value.append(string(1, yytext[0]));
    continued = 1;
}

<WORD2>. {
    yylval->str_value.append(string(1, yytext[0]));
    continued = 1;
}

<WORD1><<EOF>> {
    add_error("end of program found, expected: \"");
    BEGIN(0);
}

<WORD2><<EOF>> {
    add_error("end of program found, expected: \"");
    BEGIN(0);
}

. {
    add_error("unknown character " + string(yytext));
}
<<EOF>> return 0;
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
        cout << tags[tag] << " ";
        print_fragment(&coords);
        cout << ": ";

        if (tag == 1)
            cout << value.str_value << "\n";
        else if (tag == 2)
            cout << value.int_value << "\n";
        else if (tag == 3)
            cout << value.str_value << "\n";
        else
            cout << "\n";
    } while (tag != 0);

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
