from hulk_lexer import *
from hulk_visitor import *
from hulk_parser import *


def solve(inputStr):
    l = Lexer(inputStr, [automataNumber, automataConst])
    l.scanTokens()
    parser = Parser(l.tokens)
    expr = parser.parseExpr()
    printer = AstPrinter()
    if expr is not None:
        print(expr.accept(printer))
    else:
        print("Null")


t = int(input())
while t > 0:
    inp = input()
    solve(inp)
    t -= 1
