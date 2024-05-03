from lexer.automata import automataConst, automataNumber
from lexer.hulk_lexer import *
from parser.hulk_parser import Parser
from parser.hulk_visitor import AstEvaluator, AstPrinter



def solve(inputStr):
    l = Lexer(inputStr, [automataNumber, automataConst])
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


t = int(input())
while t > 0:
    inp = input()
    solve(inp)
    t -= 1
