from ast import While
import common
from common.ast_nodes.expressions import BinaryNode, BlockNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, SetNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.regular_expressions import BinaryExpr, Literal
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
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

def destruct_Expr(s):
    if isinstance(s[1], LiteralNode) and s[1].id.type == "id":
        return DestructorNode(s[1], s[3])
    if isinstance(s[1], GetNode):
        return SetNode(s[1].left, s[1].token, s[3])
    if isinstance(s[1], VectorGetNode):
        return VectorSetNode(s[1].left, s[1].index, s[3])
    raise Exception("no pincha")

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
            "Program": [lambda s: ProgramNode(s[1], s[2])],
            "Decls": [
                lambda s: [s[1]] + s[2],
                lambda s: [s[1]] + s[2],
                lambda s: [s[1]] + s[2],
                lambda s: []
            ],
            "ProtocolDecls": [
                lambda s: ProtocolNode(s[2], s[5], s[3])
            ],
            "OptExtension": [
                lambda s: s[2],
                lambda s: None
            ],
            "ProtocolElems": [
                lambda s: [s[1]] + s[2],
                lambda s: []
            ],
            "MethodSignature": [
                lambda s: SignatureNode(s[1], s[3], s[6])
            ],
            "TypedParamList": [
                lambda s: [(s[1], s[3])] + s[4],
                lambda s: []
            ],
            "TypedParamTail": [
                lambda s: [(s[2], s[4])] + s[5],
                lambda s: []
            ],
            "TypeDecl": [
                lambda s: TypeNode(s[2], s[3], s[6][0], s[6][1], s[4][0], s[4][1])
            ],
            "OptParams": [
                lambda s: s[2],
                lambda s: []
            ],
            "OptInheritance": [
                lambda s: (s[2], s[3]),
                lambda s: (None, None)
            ],
            "OptArgs": [
                lambda s: s[2],
                lambda s: None
            ],
            "TypeElems": [
                lambda s: ([s[1]] + [x for x in s[2][0]], s[2][1]),
                lambda s: (s[2][0], [s[1]] + [x for x in s[2][1]]),
                lambda s: ([], [])
            ],
            "AttributeDecl": [
                lambda s: s[1]
            ],
            "MethodDecl": [
                lambda s: MethodNode(s[1], s[3], s[6], s[5])
            ],
            "ParamList": [
                lambda s: [(s[1], s[2])] + s[3],
                lambda s: []
            ],
            "ParamTail": [
                lambda s: [(s[2], s[3])] + s[4],
                lambda s: []
            ],
            "FuncBody": [
                lambda s: s[2],
                lambda s: s[1]
            ],
            "Assignment": [
                lambda s: AttributeNode(s[1], s[4], s[2])
            ],
            "OptType": [
                lambda s: s[2],
                lambda s: None
            ],
            "FuncDecl": [
                lambda s: s[2]
            ],
            "Expr": [
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
                lambda s: s[1],
            ],
            "LetExpr": [
                lambda s: LetNode([s[2]] + s[3], s[5])
            ],
            "AssignmentList": [
                lambda s: [s[2]] + s[3],
                lambda s: []
            ],
            "BlockExpr": [
                lambda s: BlockNode(s[2])
            ],
            "ExprList": [
                lambda s: [s[1]] + s[3],
            ],
            "ExprTail": [
                lambda s: [s[1]] + s[3],
                lambda s: []
            ],
            "IfExpr": [
                lambda s: IfNode( [(s[3], s[5])] + s[6] , s[8])
            ],
            "OptElif": [
                lambda s: [(s[3], s[5])] + s[6],
                lambda s: []
            ],
            "WhileExpr": [
                lambda s: WhileNode(s[3], s[5])
            ],
            "ForExpr": [
                lambda s: ForNode(s[3], s[5], s[7])
            ],
            "DestrucExpr": [
                destruct_Expr
            ],
            "VectorExpr": [
                lambda s: ExplicitVectorNode(s[2]),
                lambda s: ImplicitVectorNode(s[2], s[4], s[6])
            ],
            "VectorElems": [
                lambda s: [s[1]] + s[2],
                lambda s: []
            ],
            "VectorTail": [
                lambda s: [s[2]] + s[3],
                lambda s: []
            ],
            "As": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "LogicOr": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "LogicAnd": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Equality": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Comparison": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Is": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Str": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "StrOp": [
                lambda s: s[1],
                lambda s: s[1]
            ],
            "Term": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Factor": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Mod": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Power": [
                lambda s: BinaryNode(s[1], s[2], s[3]),
                lambda s: s[1]
            ],
            "Primary": [
                lambda s: LiteralNode(s[1]),
                lambda s: LiteralNode(s[1]),
                lambda s: LiteralNode(s[1]),
                lambda s: LiteralNode(s[1]),
            ]
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

    def convertAst(self, tree: ParseNode):
        attributes = self.attributed_productions[tree.value][self.get_index(tree)]
        body = tree.children

        s = []

        for i in range(0, len(attributes) + 1):
            s.append(None)


        for i, symbol in enumerate(body, 1):
            if symbol.value in self.grammar.terminals:
                token = symbol.token
                s[i] = token
                continue
            s[i] = self.convertAst(body[i - 1])

        return attributes[0](s)

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