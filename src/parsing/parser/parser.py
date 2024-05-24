import common
from common.ast_nodes.expressions import BinaryExpr, Literal
from common.parse_nodes.parse_node import ParseNode
from common.parse_nodes.parse_tree import ParseTree
from common.visitors.Printer import AstPrinter
from common.token_class import Token
from parsing.parser_generator.grammar import EOF, EPSILON, Grammar


"""

E -> T X
X -> + T X | epsilon
T -> F Y
Y -> * F Y | epsilon
F -> l | (E)


"""


class Parser:
    def __init__(self):
        self.current = 0
        self.grammar = Grammar(
            ["E", "X", "Y", "T", "F"],
            ["+", "*", "(", ")", "l", EPSILON],
            "E",
            {
                "E": [["T", "X"]],
                "X": [["+", "T", "X"], [EPSILON]],
                "T": [["F", "Y"]],
                "Y": [["*", "F", "Y"], [EPSILON]],
                "F": [["l"], ["(", "E", ")"]],
            },
        )

        self.attributed_productions = {
            "E": [[lambda h, s: s[2], None, lambda h, s: s[1]]],
            "X": [
                [
                    lambda h, s: BinaryExpr(h[0], s[1], s[3]),
                    None,
                    None,
                    lambda h, s: s[2], lambda h, s: h[0],
                ],
                [lambda h, s : h[0]],
            ],
            "T": [[lambda h, s: s[2], None, lambda h, s: s[1]]],
            "Y": [
                [
                    lambda h, s: BinaryExpr(h[0], s[1], s[3]),
                    None,
                    None,
                    lambda h, s: s[2], lambda h, s: h[0],
                ],
                [lambda h, s : h[0]],
            ],
            "F": [
                [lambda h, s: Literal(s[1]), None],
                [lambda h, s: lambda h, s: s[2], None, None, None],
            ],
        }

    def get_index(self, tree: ParseNode):
        value = tree.value
        for i in range(0, len(self.grammar.productions[value])):
            flag = True
            for j in range(0, len(tree.children)):
                if (
                    j >= len(self.grammar.productions[value][i])
                    or tree.children[j].value != self.grammar.productions[value][i][j]
                ):
                    flag = False
            if flag:
                return i

    def convertAst(self, tree: ParseNode, inherited_value=None):
        attributes = self.attributed_productions[tree.value][self.get_index(tree)]
        body = tree.children

        h = []
        s = []

        for i in range(0, len(attributes) + 1):
            h.append(None)
            s.append(None)

        h[0] = inherited_value

        for i, symbol in enumerate(body, 1):
            if symbol.value in self.grammar.terminals:
                token = symbol.token
                s[i] = token
                continue
            if attributes[i] != None:
                h[i] = attributes[i](h, s)
            s[i] = self.convertAst(body[i - 1], h[i])

        return attributes[0](h, s)

    def parse(self, tokens: list[Token]) -> ParseTree:
        return self.grammar.parse(tokens)


parser = Parser()

tree = parser.parse(
    [
        Token("l", "2", 0, 0),
        Token("+", "+", 0, 0),
        Token("l", "2", 0, 0),
        Token(EOF, "", 0, 0),
    ]
)

ast_tree = parser.convertAst(tree.root)

printer = AstPrinter.TreePrinter()
print(ast_tree.accept(printer))