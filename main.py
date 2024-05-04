import argparse
from pathlib import Path
from lexer.lexer import *
from visitors.visitor import *
from parser.parser import *

def solve(inputStr):
    l = Lexer(inputStr)
    l.scanTokens()
    parser = Parser(l.tokens)
    program = parser.parseProgram()
    evaluator = AstEvaluator()
    for statment in program:
        printer = TreePrinter() 
        print(statment.accept(printer))
        statment.accept(evaluator)

def main():
    # Create the parser
    parser = argparse.ArgumentParser(description='Process a file path.')
    
    # Add the arguments
    parser.add_argument('file_path', type=Path, help='Path to the file')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Check if the file exists
    if args.file_path.exists():
        try:
            with open(args.file_path, "r") as f:
                cont = f.read()
                solve(cont)
                f.close()
        except Exception as e:
            print(e)    
    else:
        print(f'File does not exist: {args.file_path}')

if __name__ == '__main__':
    main() 