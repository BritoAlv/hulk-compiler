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

defaultHulkProgram = """
function log(x, y) => x + y;
function rand() => 0.6;
function tan(x: Number): Number => sin(x) / cos(x);
function cot(x) => 1 / tan(x);
function operate(x, y) {
    print(x + y);
    print(x - y);
    print(x * y);
    print(x / y);
}
function fib(n) => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);
function fact(x) => let f = 1 in for (i in range(1, x+1)) f := f * i;
function gcd(a, b) => while (a > 0)
        let m = a % b in {
            b := a;
            a := m;
        };
protocol Hashable {
    hash(): Number;
}
protocol Equatable extends Hashable {
    equals(other: Object): Boolean;
}
protocol Iterable {
    next() : Boolean;
    current() : Object;
}
type Range2(min:Number, max:Number) {
    min = min;
    max = max;
    current = min - 1;

    next(): Boolean => (self.current := self.current + 1) < self.max;
    current(): Number => self.current;
}
type Point(x,y) {
    x = x;
    y = y;
    hash() => self.x + self.y ;

    getX() => self.x;
    getY() => self.y;

    setX(x) => self.x := x;
    setY(y) => self.y := y;
}
type PolarPoint(phi, rho) inherits Point(rho * sin(phi), rho * cos(phi)) {
    rho() => sqrt(self.getX() ^ 2 + self.getY() ^ 2);
}
type Knight inherits Person {
    name() => "Sir" @@ base();
}
type Person(firstname : String, lastname : String) {
    firstname = firstname;
    lastname = lastname;

    name() => self.firstname @@ self.lastname;
    hash() : Number {
        5;
    }
}
type Superman {
}
type Bird {
}
type Plane {
}
type A {
    hello() => print("A");
}

type B inherits A {
    hello() => print("B");
}

type C inherits A {
    hello() => print("C");
}

{
    42;
    print(42);
    print((((1 + 2) ^ 3) * 4) / 5);
    print("Hello World");
    print("The message is \\"Hello World\\"");
    print("The meaning of life is " @ 42);
    print(sin(2 * PI) ^ 2 + cos(3 * PI / log(4, 64)));
    {
        print(42);
        print(sin(PI/2));
        print("Hello World");
    }


    print(tan(PI) ** 2 + cot(PI) ** 2);

    let msg = "Hello World" in print(msg);
    let number = 42, text = "The meaning of life is" in
        print(text @ number);
    let number = 42 in
        let text = "The meaning of life is" in
            print(text @ number);
    let number = 42 in (
        let text = "The meaning of life is" in (
                print(text @ number)
            )
        );
    let a = 6, b = a * 7 in print(b);
    let a = 6 in
        let b = a * 7 in
            print(b);
    let a = 5, b = 10, c = 20 in {
        print(a+b);
        print(b*c);
        print(c/a);
    };
    let a = (let b = 6 in b * 7) in print(a);
    print(let b = 6 in b * 7);
    let a = 20 in {
        let a = 42 in print(a);
        print(a);
    };
    let a = 7, a = 7 * 6 in print(a);
    let a = 7 in
        let a = 7 * 6 in
            print(a);
    let a = 0 in {
        print("a" @@ a);
        a := 1;
        print("a" @@ a);
    };
    let a = 0 in
        let b = a := 1 in {
            print(a);
            print(b);
        };
    let a = 42 in if (a % 2 == 0) print("Even") else print("odd");
    let a = 42 in print(if (a % 2 == 0) "even" else "odd");
    let a = 42 in
        if (a % 2 == 0) {
            print(a);
            print("Even");
        }
        else print("Odd");
    let a = 42, mod = a % 3 in # error
        print(
            if (mod == 0) "Magic"
            elif (mod % 3 == 1) "Woke"
            else "Dumb"
        );
    let a = 10 in while (a >= 0) {
        print(a);
        a := a - 1;
    };

    for (x in range(0, 10)) print(x);
    let iterable = range(0, 10) in
        while (iterable.next())
            let x = iterable.current() in
                print(x);

    let pt = new Point(0, 0) in # error
        print("x: " @ pt.getX() @ "; y: " @ pt.getY());
    let pt = new Point(3,4) in
        print("x: " @ pt.getX() @ "; y: " @ pt.getY());
    let pt = new PolarPoint(3,4) in
        print("rho: " @ pt.rho());

    let p = new Knight("Phil", "Collins") in
        print(p.name());
    let p: Person = new Knight("Phil", "Collins") in print(p.name());
    let x: Number = 42 in print(x);

    let x = new Superman() in
        print(
            if (x is Bird) "It's bird!"
            elif (x is Plane) "It's a plane!"
            else "No, it's Superman!"
        );
    let x = 42 in print(x);
    let total = ({ print("Total"); 5; }) + 6 in print(total);
    let x : A = if (rand() < 0.5) new B() else new C() in
        if (x is B)
            let y : B = x as B in {
                y.hello();
            }
        else {
            print("x cannot be downcasted to B");
        };

    let numbers = [1,2,3,4,5,6,7,8,9] in
        for (x in numbers)
            print(x);
    let numbers = [1,2,3,4,5,6,7,8,9] in print(numbers[7]);
    let squares = [(x as Number)^2 || x in range(1,10)] in print(squares);
    let squares = [(x as Number)^2 || x in range(1,10)] in for (x in squares) print(x);
    #let x : Hashable = new Person("A", "B") in print(x.hash());
    let x : Hashable = new Point(0,0) in print(x.hash());

}


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
    sem_an = SemanticAnalysis()
    errors : list[Error] = []     
    errors += sem_an.runVariable(treeAst)
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
    
    # environment = Environment()
    with open('hulk.pkl', 'rb') as file:
        environment = pickle.load(file)

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

    # environment._functions.pop('main')
    # with open('hulk.pkl', "wb") as file:
    #         pickle.dump(environment, file)

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
    file4_name = '.bin/hulk.asm'

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
    
    with open('src/code_gen/assembly/hulk.asm', 'r') as source:
        with open(file4_name, 'w') as target:
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

        # Load the third file
        spim.sendline(f'load "{file4_name}"')
        spim.expect_exact('(spim) ')

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
    inputStr = sys.stdin.read().strip()

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