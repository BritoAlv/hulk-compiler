from lexer.lexer import *
from parser.visitor import *
from parser.parser import *


def solve(inputStr):
    l = Lexer(inputStr)
    l.scanTokens()
    parser = Parser(l.tokens)
    expr = parser.parse()
    printer = AstPrinter()
    evaluator = AstEvaluator()
    print(expr.accept(printer))
    print(expr.accept(evaluator))

while True:
    print(">> ", end = "")  
    inp = input()
    try:
        solve(inp)
    except Exception as e:
        print(e)