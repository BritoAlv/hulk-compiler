from common.ast_nodes.expressions import Expr


class Literal(Expr):
    def __init__(self, token):
        self.literal = token

    def accept(self, visitor):
        return visitor.visitLiteral(self)

class BinaryExpr(Expr):
    def __init__(self, left, op, right):
        self.left = left
        self.operator = op
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinary(self)