import argparse
import sys
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.printer import TreePrinter
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
type Stack
{
    top = new Node(0);
    count = 0;

    push(n : number) : number => let pushedNode = new Node(n) in 
    {
        pushedNode.addPrevious(self.top);
        self.top.addNext(pushedNode);
        self.top := pushedNode;
        self.count := self.count + 1;
        n;
    };

    pop(n : number) : number => let popped = self.top.getValue() in 
    {
        self.top := self.top.getPrevious();
        self.count := self.count - 1;
        popped;
    };

    peek() : number => self.top.getValue();

    getCount() : number => self.count;
}

type Node(value : number)
{
    value = value;
    previous = self;
    next = self;
    addPrevious(previous : Node) : Node => self.previous := previous;
    addNext(next : Node) : Node => self.next := next;
    getPrevious() : Node => self.previous;
    getNext() : Node => self.next;
    print() : number => print(self.value);
    getValue() : number => self.value;
}

let stack = new Stack() in
{
    stack.push(4);
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
    stack.push(3);
    stack.pop();
    stack.push(2);
    stack.push(5);
    stack.pop();
    stack.pop();
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
    stack.push(10);
    print("Top:" @@ stack.peek());
    print("Count:" @@ stack.getCount());
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
    tokens = hulk_lexer.scanTokens(inputStr)
    parser = Parser()
    parse_tree = parser.parse(tokens)
    ast = parser.toAst(parse_tree)
    environment_builder = EnvironmentBuilder()
    environment = environment_builder.build(ast)
    resolver = Resolver(environment)
    generator = Generator(resolver)
    assembly = generator.generate(ast)

     # Paths of assembly files
    file1 = '.bin/main.asm'
    file2 = '.bin/std.asm'
    file3 = '.bin/stack.asm'

    with open(file1, 'w') as file:
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
        spim.sendline(f'load "{file1}"')
        spim.expect_exact('(spim) ')

        # Load the second file
        spim.sendline(f'load "{file2}"')
        spim.expect_exact('(spim) ')

        # Load the third file
        spim.sendline(f'load "{file3}"')
        spim.expect_exact('(spim) ')

        spim.sendline(f'run')
        spim.sendline(f'ex')
        spim.interact()
        
    except pexpect.exceptions.ExceptionPexpect as e:
        print(f"Error running SPIM: {e}")

if len(sys.argv) == 1:
    lex(inputStr)
    sys.exit(0)
else:    
    # Parse arguments
    args = parser.parse_args()

    # Use the input argument
    # inputStr = sys.stdin.read().strip()

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
        run(inputStr)