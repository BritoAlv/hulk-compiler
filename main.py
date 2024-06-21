from lexing.lexer.main import *
from parsing.parser.parser import Parser

inputStr = "print(42);"

tokens = hulk_lexer.scanTokens(inputStr)

parser = Parser()

tree = parser.parse(tokens)

tree.root.print([0], 0, True)
