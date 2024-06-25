import argparse
import sys
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.printer import TreePrinter
from lexing.lexer.main import *
from parsing.parser.parser import Parser

# Set up argument parsing
parser = argparse.ArgumentParser(description='Hulk Compiler')
parser.add_argument('-l', '--lex', action='store_true', help='Perform lexing')
parser.add_argument('-p', '--parse', action='store_true', help='Perform parsing')
parser.add_argument('-a', '--ast', action='store_true', help='Generate AST')
parser.add_argument("-sa", "--semantic_analysis", action="store_true", help="Perform semantic analysis")
parser.add_argument('-cg', '--codegen', action='store_true', help='Generate code')

defaultHulkProgram = """
        function p(x) => print(x); 42;
        """

inputStr = defaultHulkProgram

def codeGen():
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    ast = parser.toAst(parse_tree)
    environment_builder = EnvironmentBuilder()
    environment = environment_builder.build(ast)
    resolver = Resolver(environment)
    generator = Generator(resolver)
    print("Generated Code:")
    print(generator.generate(ast))
    print("\n")

def lex():
    tokens = hulk_lexer.scanTokens(inputStr)
    print("Tokens:")
    for token in tokens:
        print(token)
    print("\n")

def parse():
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    print("Parse Tree:")
    parse_tree.root.print([0], 0, True)
    print("\n")

def ast():
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    ast = parser.toAst(parse_tree)
    print("AST:")
    print(ast.accept(TreePrinter()))
    print("\n")


if len(sys.argv) == 1:
    ast()
    
# Parse arguments
args = parser.parse_args()

# Use the input argument
inputStr = sys.stdin.read().strip()

if inputStr == None or inputStr == "":
    inputStr = defaultHulkProgram

if args.lex:
    lex()

if args.parse:
    parse()

if args.ast:
    ast()

if args.semantic_analysis:
    print("Not Implemented")

if args.codegen:
    codeGen()
