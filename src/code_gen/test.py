from typing import Literal
from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.ast_nodes.expressions import BinaryNode, CallNode, LetNode, LiteralNode
from common.ast_nodes.statements import MethodNode, ProgramNode
from common.token_class import Token

ast = ProgramNode(
    [MethodNode(Token('id', 'sum'), 
                [(Token('id', 'a'), None), (Token('id', 'b'), None)], 
                BinaryNode(
                   LiteralNode(Token('id', 'a')),
                   Token('plus', '+'),
                   LiteralNode(Token('id', 'b'))
               ),
               Token('id', 'number')), 
    MethodNode(Token('id', 'main'), [], 
               LetNode([
                   (Token('id', 'a'), LiteralNode(Token('number', '500')))
               ], CallNode(LiteralNode(Token('id', 'sum')), [LiteralNode(Token('id', 'a')), LiteralNode(Token('number', '100'))])), 
               Token('id', 'number'))]
)

environment_builder = EnvironmentBuilder()
environment = environment_builder.build(ast)
resolver = Resolver(environment)
generator = Generator(resolver)

print(generator.generate(ast))


