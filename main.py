from lexer.main import *
from parsing.parser.parser import Parser


inputStr = "print(42);"

tokens = hulk_lexer.scanTokens(inputStr)

parser = Parser()

derivation_tree = parser.parse(tokens)

ast = parser.toAst(derivation_tree)