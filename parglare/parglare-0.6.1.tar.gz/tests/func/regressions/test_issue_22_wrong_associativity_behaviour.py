from parglare import Grammar, Parser

grammar = '''
STMT : STMT "+" STMT {left, 1}
     | STMT "-" STMT {left, 1}
     | STMT "*" STMT {left, 2}
     | STMT "/" STMT {left, 2}
     | "(" STMT ")" | NUMBER;
NUMBER: /\d+(.\d+)?/;

// Should be
STMT {left}: STMT ADDOP STMT {1}
           | STMT MULOP STMT {2}
STMT: "(" STMT ")" | NUMBER;
ADDOP {1}: "+" | "-";
MULOP {2}: "*" | "/";
NUMBER: /\d+(.\d+)?/;

'''


def todo_test_associativity():
    """
    See https://github.com/igordejanovic/parglare/issues/22
    """
    g = Grammar.from_string(grammar)
    parser = Parser(g, prefer_shifts=False, debug=True, debug_colors=True)

    result = parser.parse('1 - 2 / (3 - 1 + 5 - 6 - 8 + 8 * 2 - 5)')
    import pudb;pudb.set_trace()
