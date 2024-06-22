from abc import ABC
from common.ast_nodes.statements import AttributeNode
from common.token_class import Token
from common.ast_nodes.base import * 


class LetNode(Expr):
    def __init__(self, assignments : list[AttributeNode], body : Expr):
        self.assignments = assignments
        self.body = body

    def accept(self, visitor):
        return visitor.visit_let_node(self)
    
class WhileNode(Expr):
    def __init__(self, condition : Expr, body : Expr):
        self.condition = condition
        self.body = body

    def accept(self, visitor):
        return visitor.visit_while_node(self)
    
class ForNode(Expr):
    def __init__(self, target : Token, iterable : Expr, body : Expr):
        self.target = target
        self.iterable = iterable
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_for_node(self)

class IfNode(Expr):
    def __init__(self, body : list[tuple[Expr, Expr]], elsebody : Expr):
        self.body = body
        self.elsebody = elsebody

    def accept(self, visitor):
        return visitor.visit_if_node(self)

class ExplicitVectorNode(Expr):
    def __init__(self, items : list[Expr]):
        self.items = items
    
    def accept(self, visitor):
        return visitor.visit_explicit_vector_node(self)

class ImplicitVectorNode(Expr):
    def __init__(self, result : Expr, target : Token, iterable : Expr):
        self.result = result
        self.target = target
        self.iterable = iterable
        
    def accept(self, visitor):
        return visitor.visit_implicit_vector_node(self)

class DestructorNode(Expr):
    def __init__(self, id : Token, expr : Expr):
        self.id = id
        self.expr = expr

    def accept(self, visitor):
        return visitor.visit_destructor_node(self)
    
class BlockNode(Expr):
    def __init__(self, exprs : list[Expr]):
        self.exprs = exprs

    def accept(self, visitor):
        return visitor.visit_block_node(self)

class CallNode(Expr):
    def __init__(self, callee : Expr, args : list[Expr]):
        self.callee = callee
        self.args = args

    def accept(self, visitor):
        return visitor.visit_call_node(self)
    
class GetNode(Expr):
    def __init__(self, left : Expr, id : Token):
        self.left = left
        self.id = id

    def accept(self, visitor):
        return visitor.visit_get_node(self)

class SetNode(Expr):
    def __init__(self, left : Expr, id : Token, value : Expr):
        self.left = left
        self.id = id
        self.value = value

    def accept(self, visitor):
        return visitor.visit_set_node(self)


class VectorSetNode(Expr):
    def __init__(self, left : Expr, index : Expr, value : Expr):
        self.left = left
        self.index = index
        self.value = value

    def accept(self, visitor):
        return visitor.visit_vector_set_node(self)

class VectorGetNode(Expr):
    def __init__(self, left : Expr, index : Expr):
        self.left = left
        self.index = index

    def accept(self, visitor):
        return visitor.visit_vector_get_node(self)
    
class NewNode(Expr):
    def __init__(self, id : Token, args : list[Expr]) -> None:
        self.id = id
        self.args = args

    def accept(self, visitor):
        return visitor.visit_new_node(self)

class BinaryNode(Expr, ABC):
    def __init__(self, left : Expr, op : Token , right : Expr):
        self.left = left
        self.op = op 
        self.right = right

    def accept(self, visitor):
        return visitor.visit_binary_node(self)

class LiteralNode(Expr):
    def __init__(self, id : Token):
        self.id = id

    def accept(self, visitor):
        return visitor.visit_literal_node(self)