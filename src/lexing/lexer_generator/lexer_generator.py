from common.parse_nodes.parse_node import ParseNode
from common.token_class import Token
from common.constants import CONCATENATE, UNION
from lexing.lexer_generator.evaluator import Evaluator
from lexing.lexer_generator.finite_automata import DFA
from lexing.lexer_generator.operations import Star
from lexing.lexer_generator.regular_expressions import (
    BinaryExpression,
    LiteralExpression,
    ParenExpression,
    RegularExpression,
    UnaryExpression,
)
from parsing.parser_generator_lr.grammarLR1 import GrammarLR1
from parsing.parser_generator_lr.parsing_table import ParsingTable

class LexerGenerator:
    def __init__(self):
        self.grammar = GrammarLR1(
            "RegularExpressionsGrammar",
            ["A", "B", "C", "D", "Z"],
            ["+", "c", "(", ")", "*", "?"],
            "A",
            {
                "A": [["A", "+", "B"], ["B"]],
                "B": [["B", "C"], ["C"]],
                "C": [["D", "Z"], ["D"]],
                "D": [["c"], ["(", "A", ")"]],
                "Z": [["*"], ["?"]]
            }
        )

        self.table = self.grammar.build_parsing_table()

        self.table.attributed_productions = {
            "A" : [lambda s: BinaryExpression(s[1], UNION, s[3]), 
                   lambda s: s[1]],
            "B" : [lambda s: BinaryExpression(s[1], CONCATENATE, s[2]), lambda s: s[1]],
            "C" : [lambda s: UnaryExpression(s[1], s[2]), 
                   lambda s: s[1]],
            "D" : [lambda s: LiteralExpression(s[1].token.lexeme),
                   lambda s: ParenExpression(s[1].token.lexeme, s[2], s[3].token.lexeme)],
            "Z" : [lambda s: s[1].token.lexeme]
        }

    def ConvertToAST(self, tree: ParseNode) -> RegularExpression:
        return self.table.convertAst(tree)

    def check_regular_operator(self, offset : int, input : str):
        return offset + 1 < len(input) and input[offset] == "\\" and input[offset+1] in ["*", "?", "+", "(", ")"]

    def Compile(self, inputS: str) -> DFA:
        # convert string into tokens.
        tokens = []
        cr = 0
        while cr < len(inputS):
            if self.check_regular_operator(cr, inputS):
                cr += 1
                tokens.append(Token(inputS[cr], inputS[cr], 0, 0))
            else:
                tokens.append(Token("c", inputS[cr], 0, 0))
            cr += 1
        tokens.append(Token("$", "$", 0, 0))
        # pass tokens to the parser to generate derivation tree.
        derivation_tree = self.table.parse(tokens)

        derivation_tree.root.print([0], 0, True)

        # convert tree to abstract syntax tree.
        ast = self.ConvertToAST(derivation_tree.root)
        # pass tree to evaluator.
        ev = Evaluator()
        return ast.accept(ev).ConvertNFA_DFA()