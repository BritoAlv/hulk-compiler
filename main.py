import argparse
from os import mkdir
import pickle
import sys

from code_gen.constructor_builder import ConstructorBuilder
from code_gen.environment import Environment
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.ast_nodes.statements import ProgramNode
from common.parse_nodes.parse_tree import ParseTree
from common.printer import TreePrinter
from common.token_class import Token
from common.ErrorLogger import Error
from lexing.lexer.main import *
from parsing.parser.parser import Parser
from semantic.ast_modifier import VectorModifier
from semantic.tipos import SemanticAnalysis
import re
import pexpect

from semantic.type_any import TypeAny
from semantic.type_deducer import TypeDeducer
from semantic.type_picker import TypePicker
from semantic.semantic_checker import SemanticCheck

# Set up argument parsing
parser = argparse.ArgumentParser(description='Hulk Compiler')
parser.add_argument('-l', '--lex', action='store_true', help='Perform lexing')
parser.add_argument('-p', '--parse', action='store_true', help='Perform parsing')
parser.add_argument('-a', '--ast', action='store_true', help='Generate AST')
parser.add_argument("-sa", "--semantic_analysis", action="store_true", help="Perform semantic analysis")
parser.add_argument('-cg', '--codegen', action='store_true', help='Generate code')
parser.add_argument('-r', '--run', action='store_true', help='Run the compiled assembly')

with open('program.hulk', 'r') as source:
    defaultHulkProgram = source.read()

defaultHulkProgram += """
type C{
    a = self.a;
}
4;
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

def parse(inputStr : str, show = False) -> Parser:
    tokens = lex(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens, inputStr)
    if show:
        print("Parse Tree:")
        parse_tree.root.print([0], 0, True)
        print("\n")
    if parse_tree.root.value == "ERROR":
        sys.exit(1)
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

def semantic_clean_analysis(inputStr : str) -> ProgramNode:
    treeAst = ast(inputStr)
    #sem_an = SemanticAnalysis()
    errors : list[Error] = []     
    #errors += sem_an.run(treeAst)
    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)
    

    # handle constructors and inheritance. 
    # this modifies the Ast.
    constructor_builder = ConstructorBuilder()
    errors += constructor_builder.build(treeAst)

    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)

    # handle vector declarations.
    # this modifies the Ast.
    treeAst = treeAst.accept(VectorModifier())

    return treeAst

def semantic_corrupted_analysis(inputStr : str) -> tuple[ProgramNode, Resolver]:
    ast = semantic_clean_analysis(inputStr)
    environment = Environment()
    environment_builder = EnvironmentBuilder()
    errors = environment_builder.build(environment, ast)
    resolver = Resolver(environment)
    
    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)

    # do some semantich check first.
    semantic_ch = SemanticCheck(resolver)
    errors += semantic_ch.semantic_check(ast)

    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)

    # store in the context all annotated types by the user.
    type_picker = TypePicker(resolver)
    errors += type_picker.pick_types(ast)

    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)

    # deduce types for non-annotated types by the user.
    type_deducer = TypeDeducer(resolver)
    errors += type_deducer.check_types(ast)

    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)

    # check that all symbols are types before sending them to code generation.

    type_any = TypeAny(resolver)
    errors += type_any.check_any(ast)

    if len(errors) > 0:
        for error in errors:
            error.show(inputStr)
        sys.exit(1)
    ast = type_any._program
    return (ast, resolver)

def codeGen(inputStr : str, show = False) -> str:
    tup = semantic_corrupted_analysis(inputStr)
    ast = tup[0]
    resolver = tup[1]
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
    # file4_name = '.bin/vector.asm'

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
    
    # with open('src/code_gen/assembly/vector.asm', 'r') as source:
    #     with open(file4_name, 'w') as target:
    #         target.write(source.read())

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

    # Initialize a list to store output lines
    spim_output = []

    try:
        spim = pexpect.spawn("spim")
        spim.expect_exact('(spim) ')

        spim.sendline(f'load "{file1_name}"')
        spim.expect_exact('(spim) ')

        spim.sendline(f'load "{file2_name}"')
        spim.expect_exact('(spim) ')

        # Load the third file
        spim.sendline(f'load "{file3_name}"')
        spim.expect_exact('(spim) ')

        # # Load the third file
        # spim.sendline(f'load "{file4_name}"')
        # spim.expect_exact('(spim) ')

        # Run the SPIM process and capture its output
        spim.sendline('run')
        spim.expect_exact('(spim) ')
        spim_output.append(spim.before.decode('utf-8'))  # Decode and store the output

        # Continue with the rest of the commands
        spim.sendline('ex')
        #spim.interact()
        
        # Print the captured output
        print(spim_output[0][5:])
        
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
        semantic_corrupted_analysis(inputStr)

    if args.codegen:
        codeGen(inputStr, True)

    if args.run:
        try:
            run(inputStr)
        except:
            sys.exit(1)