from lexer.lexer import *
from visitors.visitor import *
from parser.parser import *

def solve(inputStr):
    l = Lexer(inputStr)
    l.scanTokens()
    parser = Parser(l.tokens)
    program = parser.parseProgram()
    printer = TreePrinter() 
    evaluator = AstEvaluator()
    for statment in program:
        print(statment.accept(printer))
        statment.accept(evaluator)

while True:
    print(">> ", end = "")  
    inp = input()
    try:
        with open(inp, "r") as f:
            cont = f.read()
            solve(cont)
            f.close()
    except Exception as e:
        print(e)