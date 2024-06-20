from common.parse_nodes.parse_node import ParseNode
from common.token_class import Token
from lexing.lexer_generator.const import CONCATENATE, UNION
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
from parsing.parser_generator import *
from parsing.parser_generator.grammar import EOF, EPSILON, Grammar
from lexing.lexer_generator import const
"""
Goal of this is :

    given a regular expression in a string return an abstract syntax tree so that the evaluator can create the automatas.
    use parser generator to parse gramatic, and then apply algorithm to convert
    from parser derivation tree to abstract syntax tree. Once done 

Regular Expressions follows this grammar:

A => B X
X => +A | epsilon
B => C Y
Y => B | epsilon
C => cZ | (A)Z
Z => * | ? | epsilon 
"""


class LexerGenerator:
    def __init__(self):
        self.grammar = Grammar(
            ["A", "B", "C", "X", "Y", "Z"],
            ["+", EPSILON, "c", "(", ")", "*", "?"],
            "A",
            {
                "A": [["B", "X"]],
                "X": [["+", "A"], [EPSILON]],
                "B": [["C", "Y"]],
                "Y": [["B"], [EPSILON]],
                "C": [["c", "Z"], ["(", "A", ")", "Z"]],
                "Z": [["*"], ["?"], [EPSILON]],
            },
        )

    def ConvertToAST(self, tree: ParseNode) -> RegularExpression:
        if tree.value == "A":
            rExp = self.ConvertToAST(tree.children[0])
            if tree.children[1].children[0].value == EPSILON:
                return rExp
            else:
                lExp = self.ConvertToAST(tree.children[1].children[1])
                return BinaryExpression(rExp, UNION, lExp)
        elif tree.value == "B":
            rExp = self.ConvertToAST(tree.children[0])
            if tree.children[1].children[0].value == EPSILON:
                return rExp
            else:
                lExp = self.ConvertToAST(tree.children[1].children[0])
                return BinaryExpression(rExp, CONCATENATE, lExp)
        elif tree.value == "C":
            rExp = LiteralExpression("1")
            if tree.children[0].value == "c":
                rExp = LiteralExpression(tree.children[0].token.lexeme) # temporal fix to a bug.
            elif tree.children[0].value == "(":
                rExp = ParenExpression("(", self.ConvertToAST(tree.children[1]), ")")
            else:
                raise Exception("Wrong Logic")
            if tree.children[-1].children[0].value != EPSILON:
                return UnaryExpression(rExp, tree.children[-1].children[0].value)
            else:
                return rExp
        return LiteralExpression("1")

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
        tokens.append(Token(EOF, "\0", 0, 0))
        for tok in tokens:
            print(tok.type, tok.lexeme)
        # pass tokens to the parser to generate derivation tree.
        derivation_tree = self.grammar.parse(tokens)
        # convert tree to abstract syntax tree.
        ast = self.ConvertToAST(derivation_tree.root)
        # pass tree to evaluator.
        ev = Evaluator()
        return ast.accept(ev).ConvertNFA_DFA()