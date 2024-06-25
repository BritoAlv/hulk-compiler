from ast import Return
from requests import ReadTimeout
from common.ast_nodes.expressions import (
    BinaryNode,
    BlockNode,
    CallNode,
    DestructorNode,
    ExplicitVectorNode,
    ForNode,
    GetNode,
    IfNode,
    ImplicitVectorNode,
    LetNode,
    LiteralNode,
    NewNode,
    SetNode,
    VectorGetNode,
    VectorSetNode,
    WhileNode,
)
from common.ast_nodes.statements import (
    AttributeNode,
    MethodNode,
    ProgramNode,
    ProtocolNode,
    SignatureNode,
    TypeNode,
)
from common.parse_nodes.parse_node import ParseNode
from common.parse_nodes.parse_tree import ParseTree
from common.token_class import Token
from parsing.parser_generator_lr.parsing_table import ParsingTable


class Parser:
    def __init__(self):
        """
        Use the Notebook to build the grammar if is modified (by now).
        """
        self.parsing_table = ParsingTable.load_parsing_table("hulk_grammar")
        self.parsing_table.attributed_productions = {
            "Program": [
                lambda s: ProgramNode(
                        s[1] + [MethodNode(Token('id', 'main'), [], s[2], Token('id', 'void'))])],
            "Decls": [
                lambda s: [s[1]] + s[2],
                lambda s: [s[1]] + s[2],
                lambda s: [s[1]] + s[2],
                lambda s: [],
            ],
            "ProtocolDecl": [lambda s: ProtocolNode(s[2].token, s[5], s[3].token if s[3] != None else s[3])],
            "OptExtension": [lambda s: s[2], lambda s: None],
            "ProtocolElems": [lambda s: [s[1]] + s[2], lambda s: []],
            "MethodSignature": [lambda s: SignatureNode(s[1], [(x.token, y.token) for (x, y) in s[3]], s[6])],
            "TypedParamList": [lambda s: [(s[1], s[3])] + s[4], lambda s: []],
            "TypedParamTail": [lambda s: [(s[2], s[4])] + s[5], lambda s: []],
            "TypeDecl": [
                # lambda s: TypeNode(s[2].token, 
                # [(x.token, y.token if y != None else y) for (x, y) in s[3]], s[6][0], s[6][1], s[4][0].token if s[4][0] != None else s[4][0],  s[4][1]),
                lambda s: TypeNode(s[2].token, 
                                   [(node.id, node.type) for node in s[6][0]],
                                   [MethodNode(Token('id', f'build'), 
                                              [(x.token, y.token if y != None else y) for (x, y) in s[3]],
                                              BlockNode(
                                                ([CallNode(
                                                     LiteralNode(
                                                         Token('id', f'build_{s[4][0].token.lexeme}')), 
                                                         s[4][1]
                                                         )] 
                                                    if s[4][0] != None else []) 
                                                + s[6][0] + [LiteralNode(Token('id', 'self'))]), 
                                                    Token('id', s[2].token.lexeme))] 
                                    + s[6][1],
                                    s[4][0].token if s[4][0] != None else s[4][0])
            ],
            "OptParams": [lambda s: s[2], lambda s: []],
            "OptInheritance": [lambda s: (s[2], s[3]), lambda s: (None, None)],
            "OptArgs": [lambda s: s[2], lambda s: None],
            "TypeElems": [
                lambda s: ([s[1]] + [x for x in s[2][0]], s[2][1]),
                lambda s: (s[2][0], [s[1]] + [x for x in s[2][1]]),
                lambda s: ([], []),
            ],
            "AttributeDecl": [lambda s: s[1]],
            "MethodDecl": [
                lambda s: MethodNode(
                    s[1].token,
                    [(x.token, y.token if y != None else y) for (x, y) in s[3]],
                    s[6],
                    s[5].token if s[5] != None else s[5],
                )
            ],
            "ParamList": [lambda s: [(s[1], s[2])] + s[3], lambda s: []],
            "ParamTail": [lambda s: [(s[2], s[3])] + s[4], lambda s: []],
            "FuncBody": [lambda s: s[2], lambda s: s[1]],
            "Assignment": [
                lambda s: AttributeNode(
                    s[1].token, s[4], s[2].token if s[2] != None else s[2]
                )
            ],
            "OptType": [lambda s: s[2], lambda s: None],
            "FuncDecl": [lambda s: s[2]],
            "Expr": [
                lambda s: s[1],
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
            "AssignmentList": [lambda s: [s[2]] + s[3], lambda s: []],
            "BlockExpr": [lambda s: BlockNode(s[2])],
            "ExprList": [
                lambda s: [s[1]] + s[3],
            ],
            "ExprTail": [lambda s: [s[1]] + s[3], lambda s: []],
            "IfExpr": [lambda s: IfNode([(s[3], s[5])] + s[6], s[8])],
            "OptElif": [lambda s: [(s[3], s[5])] + s[6], lambda s: []],
            "WhileExpr": [lambda s: WhileNode(s[3], s[5])],
            "ForExpr": [lambda s: ForNode(s[3].token, s[5], s[7])],
            "DestrucExpr": [self.destruct_Expr],
            "VectorExpr": [
                lambda s: ExplicitVectorNode(s[2]),
                lambda s: ImplicitVectorNode(s[2], s[4].token, s[6]),
            ],
            "VectorElems": [lambda s: [s[1]] + s[2], lambda s: []],
            "VectorTail": [lambda s: [s[2]] + s[3], lambda s: []],
            'NewExpr': [self.new_expr],
            "As": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "LogicOr": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "LogicAnd": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "Equality": [
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: s[1],
            ],
            "Comparison": [
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: s[1],
            ],
            "Is": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "Str": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "StrOp": [lambda s: s[1], lambda s: s[1]],
            "Term": [
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: s[1],
            ],
            "Factor": [
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: BinaryNode(s[1], s[2].token, s[3]),
                lambda s: s[1],
            ],
            "Mod": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "Power": [lambda s: BinaryNode(s[1], s[2].token, s[3]), lambda s: s[1]],
            "Primary": [
                lambda s: LiteralNode(s[1].token),
                lambda s: LiteralNode(s[1].token),
                lambda s: LiteralNode(s[1].token),
                lambda s: LiteralNode(s[1].token),
                lambda s: s[1],
            ],
            "CallList": [
                lambda s: GetNode(s[1], s[3].token),
                lambda s: CallNode(s[1], s[3]),
                lambda s: VectorGetNode(s[1], s[3]),
                lambda s: LiteralNode(s[1].token),
                lambda s: LiteralNode(s[1].token),
                lambda s: s[2],
            ],
            "ArgList": [lambda s: [s[1]] + s[2], lambda s: []],
            "ArgTail": [lambda s: [s[2]] + s[3], lambda s: []],
        }

    def destruct_Expr(self, s):

        if isinstance(s[1], LiteralNode) and s[1].id.type == "id":
            return DestructorNode(s[1].id, s[3])
        if isinstance(s[1], GetNode):
            return SetNode(s[1].left, s[1].id, s[3])
        if isinstance(s[1], VectorGetNode):
            return VectorSetNode(s[1].left, s[1].index, s[3])
        raise Exception("no pincha")
    
    def new_expr(self, s):
        call_node = s[2]
        if isinstance(call_node, CallNode) and isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme != 'self':
            return NewNode(call_node.callee.id, call_node.args)
        raise Exception("New-Expression must be a constructor call")

    def parse(self, tokens: list[Token]) -> ParseTree:
        return self.parsing_table.parse(tokens)

    def toAst(self, tree: ParseTree):
        return self.parsing_table.convertAst(tree.root)