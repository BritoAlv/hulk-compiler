from code_gen.environment_builder import EnvironmentBuilder
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from lexing.lexer.main import *
from parsing.parser.parser import Parser

inputStr = '''
function fib(n : number) : number => if (n == 0 | n == 1) 1 else fib(n-1) + fib(n-2);

print(fib(6));
'''
tokens = hulk_lexer.scanTokens(inputStr)
parser = Parser()
parse_tree = parser.parse(tokens)
ast = parser.toAst(parse_tree)

environment_builder = EnvironmentBuilder()
environment = environment_builder.build(ast)
resolver = Resolver(environment)
generator = Generator(resolver)
print(generator.generate(ast))