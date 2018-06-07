#!/usr/bin/env python3
from sys import argv
from parsimonious.grammar import Grammar


my_grammar = Grammar(r"""
    lexicon = entry+
    entry = lexeme sense*

    sense = sense_number? part_of_speech gloss*
    gloss = national_gloss / english_gloss / regional_gloss / unknown_gloss
	unknown_gloss = glo_gloss / glv_gloss

    lexeme =         "\lx"   separator  headword  eol
    sense_number =   "\sn"   separator  number  eol
    part_of_speech = "\ps"   separator  part_of_speech_identifier  eol
    national_gloss = "\gn"  (separator  glossword)?  eol
    english_gloss =  "\ge"  (separator  glossword)?  eol
    regional_gloss = "\gr"  (separator  glossword)?  eol
    glo_gloss =      "\glo" (separator  glossword)?  eol
    glv_gloss =      "\glv" (separator  glossword)?  eol

    part_of_speech_identifier = "adj" / "adv" / "prp" / "n" / "v"
    headword = text
    glossword = text
	separator = space

	eol         = "\n"+
	space		= ~"[ \t]+"
    number      = ~"[0-9]+"
    text        = ~"[^\n]+"i
    """)


script, filename = argv
with open(filename) as file:
    print(my_grammar.parse(file.read()))
