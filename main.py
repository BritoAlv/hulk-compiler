import argparse
import sys
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.printer import TreePrinter
from lexing.lexer.main import *
from parsing.parser.parser import Parser
from semantic.tipos import SemanticAnalysis

# Set up argument parsing
parser = argparse.ArgumentParser(description='Hulk Compiler')
parser.add_argument('-l', '--lex', action='store_true', help='Perform lexing')
parser.add_argument('-p', '--parse', action='store_true', help='Perform parsing')
parser.add_argument('-a', '--ast', action='store_true', help='Generate AST')
parser.add_argument("-sa", "--semantic_analysis", action="store_true", help="Perform semantic analysis")
parser.add_argument('-cg', '--codegen', action='store_true', help='Generate code')
parser.add_argument('-r', '--run', action='store_true', help='Run the compiled assembly')

defaultHulkProgram = """
        protocol Node {
            eval(node: number, valor: number) : number;
        }
        type Perro(color : string, edad: number)
        {
            color = color;
            edad = edad;
            comer = 13;
            Ladrar(a: number) : Vector => [12];
            Ladrar(a: number, b : string, ba : number) : Vector => [12];
        }
        function h(num: number) : number =>
            43;  
        let a = [1,2,3], b = 3, c = new Perro("ds", 3) in 
            {
              b:= 3; 
              a := c.Ladrar(1);       
            };
        """

inputStr = defaultHulkProgram

def codeGen(inputStr : str):
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

def lex(inputStr : str):
    tokens = hulk_lexer.scanTokens(inputStr)
    print("Tokens:")
    for token in tokens:
        print(token)
    print("\n")

def parse(inputStr : str):
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    print("Parse Tree:")
    parse_tree.root.print([0], 0, True)
    print("\n")

def ast(inputStr : str):
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    ast = parser.toAst(parse_tree)
    print("AST:")
    print(ast.accept(TreePrinter()))
    print("\n")

def semantic_analysis(inputStr : str):
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    ast = parser.toAst(parse_tree)
    
    sem_an = SemanticAnalysis()
    sem_an.run(ast)

def run(inputStr : str):
    # run the assembly code somehow
    pass

if len(sys.argv) == 1:
    ast(inputStr)
    print(inputStr)
    semantic_analysis(inputStr)
    sys.exit(0)
    
# Parse arguments
args = parser.parse_args()

# Use the input argument
inputStr = sys.stdin.read().strip()

if inputStr == None or inputStr == "":
    inputStr = defaultHulkProgram

if args.lex:
    lex(inputStr)

if args.parse:
    parse(inputStr)

if args.ast:
    ast(inputStr)

if args.semantic_analysis:
    semanticAnalysis(inputStr)

if args.codegen:
    codeGen(inputStr)

if args.run:
    pass