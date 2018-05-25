from parglare import Grammar, GLRParser


def test_wrong_shift_to_state_bug():
    grammar = """
    Program: "begin"
             statements=Statements
             ProgramEnd EOF;
    Statements: Statements1 {nops} | EMPTY;
    Statements1: Statements1 Statement | Statement;
    ProgramEnd: End;
    Statement: End "transaction" | "command";
    End: "end";
    """

    g = Grammar.from_string(grammar, ignore_case=True)
    parser = GLRParser(g, build_tree=True, prefer_shifts=True,
                       debug=True, debug_colors=True)

    parser.parse("""
    begin
        command
        end transaction
        command
        end transaction
        command
    end
    """)
