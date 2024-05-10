from abc import ABC, abstractmethod

class Statement(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass


class FunctionDeclaration(Statement):
    def __init__(self, name, params, bodyBlock):
        self.name = name
        self.params = params
        self.bodyBlock = bodyBlock
        self.arity = len(params)

    def accept(self, visitor):
        return visitor.visitFunctionDeclaration(self)


class ReturnStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitReturn(self)


class IfStatement(Statement):
    def __init__(self, condition, then, otherwise):
        self.condition = condition
        self.then = then
        self.otherwise = otherwise

    def accept(self, visitor):
        return visitor.visitIf(self)


class ForStatement(Statement):
    def __init__(self, initializer, condition, action, block):
        self.initializer = initializer
        self.condition = condition
        self.action = action
        self.block = block

    def accept(self, visitor):
        return visitor.visitFor(self)


class WhileStatement(Statement):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def accept(self, visitor):
        return visitor.visitWhile(self)


class PrintStatement(Statement):
    def __init__(self, printToken, expr):
        self.printToken = printToken
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitPrint(self)


class DeclarationStatement(Statement):
    def __init__(self, varToken, identifier, expr):
        self.varToken = varToken
        self.identifier = identifier
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitDeclaration(self)


class AssignStatement(Statement):
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitAssignment(self)


class BlockStatement(Statement):
    def __init__(self, statments):
        self.statments = statments

    def accept(self, visitor):
        return visitor.visitBlock(self)


class BreakStatement(Statement):
    def accept(self, visitor):
        return visitor.visitBreak(self)


class ContinueStatement(Statement):
    def accept(self, visitor):
        return visitor.visitContinue(self)