from common.token_class import Token
from common.ast_nodes.base import * 

class ProgramNode(Statement):
    def __init__(self, decls : list[Statement]):
        self.decls = decls

    def accept(self, visitor):
        return visitor.visit_program_node(self)

class AttributeNode(Statement):
    def __init__(self, id : Token, body : Expr, type : Token | None = None):
        self.id = id
        self.body = body    
        self.type = None
    
    def accept(self, visitor):
        return visitor.visit_attribute_node(self)

class MethodNode(Statement):
    def __init__(self, id : Token, params : list[tuple[Token, Token | None]], body : Expr, type : Token | None = None):
        self.id = id
        self.params = params
        self.body = body
        self.type = type

    def accept(self, visitor):
        return visitor.visit_method_node(self)

class TypeNode(Statement):
    def __init__(self, 
                 id : Token, 
                 params : list[tuple[Token, Token]],
                 attributes : list[AttributeNode],
                 methods : list[MethodNode], 
                 ancestor_id : Token | None, 
                 ancestor_args : list[Expr] | None = None):
        self.id = id
        self.params = params
        self.attributes = attributes,
        self.methods = methods,
        self.ancestor_id = ancestor_id,
        self.ancestor_args = ancestor_args

    def accept(self, visitor):
        return visitor.visit_type_node(self)

class SignatureNode(Statement):
    def __init__(self,
                id : Token,
                params : list[tuple[Token, Token]], 
                type : Token):
        self.id = id
        self.params = params
        self.type = type

    def accept(self, visitor):
        return visitor.visit_signature_node(self)

class ProtocolNode(Statement):
    def __init__(self, 
                 id : Token, 
                 signatures : list[SignatureNode],
                 ancestor_node : Token | None = None):
        self.id = id
        self.signatures = signatures
        self.ancestor_node = ancestor_node

    def accept(self, visitor):
        return visitor.visit_protocol_node(self)