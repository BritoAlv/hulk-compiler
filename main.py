import argparse
from os import mkdir
import sys

from code_gen.constructor_builder import ConstructorBuilder
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.ast_nodes.statements import ProgramNode
from common.parse_nodes.parse_tree import ParseTree
from common.printer import TreePrinter
from common.token_class import Token
from lexing.lexer.main import *
from parsing.parser.parser import Parser
from semantic.tipos import SemanticAnalysis
import re
import pexpect

# Set up argument parsing
parser = argparse.ArgumentParser(description='Hulk Compiler')
parser.add_argument('-l', '--lex', action='store_true', help='Perform lexing')
parser.add_argument('-p', '--parse', action='store_true', help='Perform parsing')
parser.add_argument('-a', '--ast', action='store_true', help='Generate AST')
parser.add_argument("-sa", "--semantic_analysis", action="store_true", help="Perform semantic analysis")
parser.add_argument('-cg', '--codegen', action='store_true', help='Generate code')
parser.add_argument('-r', '--run', action='store_true', help='Run the compiled assembly')

defaultHulkProgram = """
    print(2a);
"""

inputStr = defaultHulkProgram


def lex(inputStr : str, show = False) -> list[Token]:
    tokens = hulk_lexer.scanTokens(inputStr)
    if hulk_lexer.report(inputStr) :
        sys.exit(1)
    if show:
        print("Tokens:")
        for token in tokens:
            print(token)
        print("\n")
    return tokens

def parse(inputStr : str, show = False) -> ParseTree:
    tokens = lex(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    if show:
        print("Parse Tree:")
        parse_tree.root.print([0], 0, True)
        print("\n")
    return parse_tree

def ast(inputStr : str, show = False) -> ProgramNode:
    parse_tree = parse(inputStr)
    parser = Parser()
    ast = parser.toAst(parse_tree)
    if show:
        print("AST:")
        print(ast.accept(TreePrinter()))
        print("\n")
    return ast

def semantic_analysis(inputStr : str) -> ProgramNode:
    treeAst = ast(inputStr)
    sem_an = SemanticAnalysis()
    #sem_an.run(treeAst)
    return treeAst

def codeGen(inputStr : str, show = False) -> str:
    ast = semantic_analysis(inputStr)
    constructor_builder = ConstructorBuilder()
    constructor_builder.build(ast)
    environment_builder = EnvironmentBuilder()
    environment = environment_builder.build(ast)
    resolver = Resolver(environment)
    generator = Generator(resolver)
    if show:
        print("Generated Code:")
        print(generator.generate(ast))
        print("\n")
    return generator.generate(ast)
    
def run(inputStr : str):
    assembly = codeGen(inputStr)

    # Paths of assembly files
    file1_name = '.bin/main.asm'
    file2_name = '.bin/std.asm'
    file3_name = '.bin/stack.asm'

    try:
        mkdir('.bin/')
    except:
        pass

    with open('src/code_gen/assembly/std.asm', 'r') as source:
        with open(file2_name, 'w') as target:
            target.write(source.read())

    with open('src/code_gen/assembly/stack.asm', 'r') as source:
        with open(file3_name, 'w') as target:
            target.write(source.read())

    with open(file1_name, 'w') as file:
        file.write(assembly)

    startup_regex = re.compile(
        r'SPIM Version \d+\.\d+ of \w+ \d+, \d+\r\n'
        r'Copyright \d+-\d+, James R\. Larus\.\r\n'
        r'All Rights Reserved\.\r\n'
        r'See the file README for a full copyright notice\.\r\n'
        r'Loaded: /usr/lib/spim/exceptions\.s\r\n'
        r'\(spim\) '
    )

    try:
        # Start the SPIM process
        spim = pexpect.spawn('spim')

        # Wait for the SPIM prompt
        spim.expect(startup_regex.pattern)

        # Load the first file
        spim.sendline(f'load "{file1_name}"')
        spim.expect_exact('(spim) ')

        # Load the second file
        spim.sendline(f'load "{file2_name}"')
        spim.expect_exact('(spim) ')

        # Load the third file
        spim.sendline(f'load "{file3_name}"')
        spim.expect_exact('(spim) ')

        spim.sendline(f'run')
        spim.sendline(f'ex')
        spim.interact()
        
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"Error running SPIM: {e}")

if len(sys.argv) == 1:
    run(inputStr)
    sys.exit(0)
else:    
    # Parse arguments
    args = parser.parse_args()

    # Use the input argument
    # inputStr = sys.stdin.read().strip()

    if inputStr == None or inputStr == "":
        inputStr = defaultHulkProgram

    if args.lex:
        lex(inputStr, True)

    if args.parse:
        parse(inputStr, True)

    if args.ast:
        ast(inputStr, True)

    if args.semantic_analysis:
        semantic_analysis(inputStr)

    if args.codegen:
        codeGen(inputStr, True)

    if args.run:
        run(inputStr)
