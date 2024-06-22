from code_gen.environment_builder import EnvironmentBuilder
from code_gen.generator import Generator
from code_gen.resolver import Resolver
from common.ast_nodes.expressions import BinaryNode, CallNode, DestructorNode, IfNode, LetNode, LiteralNode, WhileNode
from common.ast_nodes.statements import MethodNode, ProgramNode
from common.token_class import Token

ast = ProgramNode(
    [MethodNode(Token('id', 'factorial'), 
                [(Token('id', 'n'), None)], 
                IfNode([
                    (BinaryNode(
                        LiteralNode(Token('id', 'n')),
                        Token('less', '<'),
                        LiteralNode(Token('number', '1'))
                    ), 
                    LiteralNode(Token('number', '1')))
                ], 
                BinaryNode(
                    LiteralNode(Token('id', 'n')),
                    Token('star', '*'),
                    CallNode(
                        LiteralNode(Token('id', 'factorial')),
                        [
                            BinaryNode(
                                LiteralNode(Token('id', 'n')),
                                Token('minus', '-'),
                                LiteralNode(Token('number', '1'))
                            )
                        ]
                    )
                )),
               Token('id', 'number')), 
    MethodNode(Token('id', 'main'), [], 
               CallNode(LiteralNode(Token('id', 'factorial')), [
                   LiteralNode(Token('number', '7'))
               ]), 
               Token('id', 'number'))]
)


ast = ProgramNode(
    [MethodNode(Token('id', 'fibonacci'), 
                [(Token('id', 'n'), None)], 
                IfNode([
                    (BinaryNode(
                        LiteralNode(Token('id', 'n')),
                        Token('less', '<'),
                        LiteralNode(Token('number', '2'))
                    ), 
                    LiteralNode(Token('number', '1')))
                ], 
                BinaryNode(
                    CallNode(
                        LiteralNode(Token('id', 'fibonacci')),
                        [
                            BinaryNode(
                                LiteralNode(Token('id', 'n')),
                                Token('minus', '-'),
                                LiteralNode(Token('number', '1'))
                            )
                        ]
                    ),
                    Token('plus', '+'),
                    CallNode(
                        LiteralNode(Token('id', 'fibonacci')),
                        [
                            BinaryNode(
                                LiteralNode(Token('id', 'n')),
                                Token('minus', '-'),
                                LiteralNode(Token('number', '2'))
                            )
                        ]
                    )
                )),
               Token('id', 'number')), 
    MethodNode(Token('id', 'main'), [], 
               CallNode(LiteralNode(Token('id', 'fibonacci')), [
                   LiteralNode(Token('number', '6'))
               ]), 
               Token('id', 'number'))]
)

ast = ProgramNode(
    [MethodNode(Token('id', 'loop'), [
        (Token('id', 'n'), None)
    ],
        WhileNode(
                   BinaryNode(LiteralNode(Token('id', 'n')), 
                              Token('less', '<'),
                              LiteralNode(Token('number', '10'))),
                   DestructorNode(Token('id', 'n'), BinaryNode(
                       LiteralNode(Token('id', 'n')),
                       Token('plus', '+'),
                       LiteralNode(Token('number', '1'))
                   ))
               ),
               Token('id', 'number')),
      MethodNode(Token('id', 'main'), [], 
               CallNode(LiteralNode(Token('id', 'loop')), [
                   LiteralNode(Token('number', '1'))
               ]),
               Token('id', 'number'))]
)

environment_builder = EnvironmentBuilder()
environment = environment_builder.build(ast)
resolver = Resolver(environment)
generator = Generator(resolver)

print(generator.generate(ast))


