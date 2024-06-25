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
parser.add_argument('-r', '--run', action='store_true', help='Run the compiled assembly')

defaultHulkProgram = """

function parseFactor(cr : int, tokens : Vector){
    let node = LiteralNode(tokens[cr]) in {
        if (cr == len(tokens))
        {
            node;
        }
        else
        {
            let op = tokens[cr], right = parseFactor(cr + 1, tokens) in {
                BinaryNode(node, op, right);
            }
        }
    };
}

protocol Node {
    eval() : Number;
}

type LiteralNode(value : Number) extends Node {
    value = value;
    eval() => value;
}

type BinaryNode(left : Node, op : string, right : Node) {
    left = left;
    op = op;
    right = right;
    function eval() {
        if(op == "+")
        {
            eval(left) + eval(right);
        }
        else if(op == "-")
        {
            eval(left) - eval(right);
        }
        else if(op == "*")
        {
            eval(left) * eval(right);
        }
        else
        {
            eval(left) / eval(right);
        }
    };
}
"""

defaultHulkProgram = """
type range(st:Number, ed:Number, offset : Number) {
    st = st;
    ed = ed;
    current = st - offset;

    next(): Boolean => (self.current := self.current + offset) < ed;
    current(): Number => self.current;
}


function parseTerm(tokens: Vector){
    let node = LiteralNode(tokens[0]), done = false in 
    {
        for( i in range(len(tokens)-1, -1, -1))
        {
            if (!done & (tokens[i] == "+" | tokens[i] == "-"))
            {
                let right = parseFactor(i+1, tokens),
                    op = tokens[i],
                    toks = [tokens[x] || x in range(0, i)], 
                    left = parseTerm(toks),
                    done = true in 
                {
                    node := BinaryNode(left, op, right);
                };
            }
            else
            {
                4;
            };
        };
    };
};

function parseFactor(cr : int, tokens : Vector){
    let node = LiteralNode(tokens[cr]) in {
        if (cr == len(tokens))
        {
            node;
        }
        else
        {
            let op = tokens[cr], right = parseFactor(cr + 1, tokens) in {
                BinaryNode(node, op, right);
            };
        };
    };
};

protocol Node {
    eval() : Number;
}

type LiteralNode(value : Number) {
    value = value;
    eval() => value;
}

type BinaryNode(left : Node, op : string, right : Node) {
    left = left;
    op = op;
    right = right;
    eval() {
        if(op == "+")
        {
            eval(left) + eval(right);
        }
        elif (op == "-")
        {
            eval(left) - eval(right);
        }
        elif (op == "*")
        {
            eval(left) * eval(right);
        }
        else
        {
            eval(left) / eval(right);
        };
    };
}

let node = parseTerm([3, "*", 2, "*", 4, "-", 1, "-", 1]) in print(node.eval());
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

def semanticAnalysis(inputStr : str):
    pass

def run(inputStr : str):
    # run the assembly code somehow
    pass

if len(sys.argv) == 1:
    ast(inputStr)
    print(inputStr)
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