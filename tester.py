from lexer.lexer import *
from parser.visitor import *
from parser.parser import *


def solve(inputStr):
    l = Lexer(inputStr)
    l.scanTokens()
    parser = Parser(l.tokens)
    expr = parser.parseExpr()
    printer = AstPrinter()
    evaluator = AstEvaluator()
    if expr is not None:
        print(expr.accept(printer))
        print(expr.accept(evaluator))
    else:
        print("Null")

while True:
    print(">> ", end = "")  
    inp = input()
    solve(inp)
