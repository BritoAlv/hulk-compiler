from lexer.lexer import Lexer
from parser.parser import Parser
from visitors.visitor import AstEvaluator, AstPrinter


def solve(inputStr):
    l = Lexer(inputStr)
    l.scanTokens()
    parser = Parser(l.tokens)
    expr = parser.parse()
    printer = AstPrinter()
    evaluator = AstEvaluator()
    print(inputStr, end = " ")
    print(expr.accept(printer), end = " ")
    print(expr.accept(evaluator), end = " ")
    print()

t = int(input())
while t > 0:
    inp = input()
    try:
        solve(inp)
    except Exception as e:
        print(inp, end = " ")
        print(e)
    t-= 1