grammar = r"""
    start: instruction+
         | expression                       -> eval_expression    

    instruction: NAME "=" expression        -> assign_var

    expression: term
              | sum
              | or_test

    ?or_test: and_test
            | or_test "or" and_test         -> eval_or_expression 
    ?and_test: not_test 
             | and_test "and" not_test      -> eval_and_test
    
    ?not_test: comparison
             | "not" not_test               -> eval_not

    ?comparison: term "in" term             -> eval_membership_test
               | term _comp_op term         -> eval_equalities_test
               | term  
    
    term: object
        | list
        | string
        | "true"                             -> true
        | "false"                            -> false
        | "null"                             -> null    
        | "None"                             -> null
        | "True"                             -> true
        | "False"                            -> false
        | NAME"["term"]"                     -> access_object
        | atom
    
    list : "[" [term ("," term)*] "]"
    object:"{" [pair ("," pair)*] "}"
    pair : string ":" term
    string : ESCAPED_STRING

    ?sum: product
        | sum "+" product                    -> term_add
        | sum "-" product                    -> term_subtract
    
    ?product: atom
            | product "*" atom               -> term_mul
            | product "/" product            -> term_div
          
    ?atom: NUMBER                            -> number
         | "-" atom                          -> neg
         | "(" sum ")"
         | NAME "(" args ")"                 -> func_call
         | NAME                              -> access_var
         | string
         
    !_comp_op: "<"
             | ">"
             | "=="
             | ">="
             | "<="
             | "<>"       
     
    args: argvalue ("," argvalue)*
    argvalue: expression

    %import common.CNAME -> NAME
    %import common.ESCAPED_STRING
    %import common.STRING_INNER
    %import common.WORD
    %import common.NUMBER
    
    %import common.SIGNED_NUMBER
    %import common.WS
    %ignore WS
"""
