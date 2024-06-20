from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, SetNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.parse_nodes.parse_node import ParseNode
from common.parse_nodes.parse_tree import ParseTree
from common.visitors.Printer import AstPrinter
from common.token_class import Token
from parsing.parser_generator_ll.grammar import EOF, EPSILON, Grammar
from parsing.parser_generator_lr.grammarLR1 import GrammarLR1

def gramophoneSyntaxParser( inputTokens : str) -> GrammarLR1:
    non_terminals = []
    terminals = []
    start_symbol = ""
    productions = {}
    
    def add_symbol( symbol : str):
        symbol = symbol.strip()
        if len(symbol)  == 0:
            pass
        elif symbol[0].islower():
            if symbol not in terminals:
                terminals.append(symbol)
        else:
            if symbol not in non_terminals:
                non_terminals.append(symbol)
                productions[symbol] = []
        return symbol


    lines = inputTokens.split("\n")
    for line in lines:
        if len(line) > 0:
            line = line.strip() 
            line = line[:-1]
            parts = line.split("->")
            non_terminal = add_symbol(parts[0])
            if start_symbol == "":
                start_symbol = non_terminal
            productionsLine = parts[1].split("|")
            for prod in productionsLine:
                prod = prod.strip().split(" ")
                prod_to_add = []
                for symbol in prod:
                    symbol = add_symbol(symbol)
                    if len(symbol) > 0:
                        prod_to_add.append(symbol)
                productions[non_terminal].append(prod_to_add)
    print(terminals)
    return GrammarLR1(non_terminals, terminals, start_symbol, productions)


grammar = """
Program -> Decls Expr semicolon.
Decls -> FuncDecl Decls | TypeDecl Decls | ProtocolDecl Decls | .

ProtocolDecl -> protocol id OptExtension lbrace ProtocolElems rbrace.
OptExtension -> extends id | .
ProtocolElems -> MethodSignature ProtocolElems | .
MethodSignature -> id lparen TypedParamList rparen colon id semicolon.
TypedParamList -> id colon id TypedParamTail | .
TypedParamTail -> comma id colon id TypedParamTail | .

TypeDecl -> type id OptParams OptInheritance lbrace TypeElems rbrace .

OptParams -> lparen ParamList rparen | .
OptInheritance -> inherits id OptArgs | .
OptArgs -> lparen ArgList rparen | .

TypeElems -> AttributeDecl TypeElems | MethodDecl TypeElems | .
AttributeDecl -> Assignment  semicolon .
MethodDecl -> id lparen ParamList rparen OptType FuncBody .
ParamList -> id OptType ParamTail | .
ParamTail -> comma id OptType ParamTail | .
FuncBody -> arrow Expr semicolon | BlockExpr semicolon .

Assignment -> id OptType equal Expr .
OptType -> colon id | .

FuncDecl -> function MethodDecl .

Expr -> BlockExpr | IfExpr | WhileExpr | ForExpr | LetExpr | DestrucExpr | VectorExpr | LogicOr.

LetExpr -> let Assignment AssignmentList in Expr .
AssignmentList -> comma Assignment AssignmentList | .

BlockExpr -> lbrace ExprList rbrace .
ExprList -> Expr semicolon ExprTail .
ExprTail -> Expr semicolon ExprTail | .

IfExpr -> if lparen Expr rparen Expr OptElif else Expr .
OptElif -> elif lparen Expr rparen Expr | .

WhileExpr -> while lparen Expr rparen Expr .
ForExpr -> for lparen id in Expr rparen Expr .

DestrucExpr -> Primary destrucOp Expr .

VectorExpr -> lbracket VectorElems rbracket | lbracket Expr doubleOr id in Expr rbracket .
VectorElems -> Expr VectorTail | .
VectorTail -> comma Expr VectorTail | .

LogicOr -> LogicOr or LogicAnd | LogicAnd .
LogicAnd -> LogicAnd and Equality | Equality .
Equality -> Equality doubleEqual Comparison | Equality notEqual Comparison | Comparison .
Comparison -> Comparison greater Str | Comparison greaterEq Str | Comparison less Str | Comparison lessEq Str | Str .
Str -> Str strOp Term | Term .
Term -> Term plus Factor | Term minus Factor | Factor .
Factor -> Factor star Mod | Factor div Mod | Mod .
Mod -> Mod modOp Power | Power .
Power -> Primary powerOp number | Primary .

Primary -> false | true | number | string | self CallList | id CallList | lparen Expr rparen CallList .

CallList -> dot id CallList | lparen ArgList rparen CallList | lbracket Expr rbracket CallList | .
ArgList -> Expr ArgTail | .
ArgTail -> comma Expr ArgTail | .

"""

class Parser:
    def __init__(self):
        self.grammar = gramophoneSyntaxParser(grammar)
        self.parsing_table = self.grammar.build_parsing_table()
        self.parsing_table.attributed_productions = {
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
                self.destruct_Expr
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
                lambda s: LiteralNode(s[1]),
            ],
            'CallList': [
                lambda s: GetNode(s[1], s[3]),
                lambda s: CallNode(s[1], s[3]),
                lambda s: VectorGetNode(s[1], s[3]),
                lambda s: LiteralNode(s[1]),
                lambda s: LiteralNode(s[1]),
                lambda s: s[2],
            ],
            'ArgList': [
                lambda s: [s[1]] + s[2],
                lambda s: []
            ],
            'ArgTail':[
                lambda s: [s[2]] + s[3],
                lambda s: []
            ]
        }

    def destruct_Expr(self, s):
        if isinstance(s[1], LiteralNode) and s[1].id.type == "id":
            return DestructorNode(s[1], s[3])
        if isinstance(s[1], GetNode):
            return SetNode(s[1].left, s[1].token, s[3])
        if isinstance(s[1], VectorGetNode):
            return VectorSetNode(s[1].left, s[1].index, s[3])
        raise Exception("no pincha")

    def parse(self, tokens: list[Token]) -> ParseTree:
        return self.parsing_table.parse(tokens)

    def toAst(self, tree : ParseTree):
        return self.parsing_table.convertAst(tree.root)
    
ps = Parser()

print(ps.grammar.terminals)