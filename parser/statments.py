from abc import ABC, abstractmethod

class Statment(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

class IfStatment(Statment):
    def __init__(self, condition, then, otherwise):
        self.condition = condition
        self.then = then
        self.otherwise = otherwise

    def accept(self, visitor):
        return visitor.visitIf(self)
    
class ForStatment(Statment):
    def __init__(self, initializer, condition, action, block):
        self.initializer = initializer
        self.condition = condition
        self.action = action
        self.block = block

    def accept(self, visitor):
        return visitor.visitFor(self)
    
class WhileStatment(Statment):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

    def accept(self, visitor):
        return visitor.visitWhile(self)


class PrintStatment(Statment):
    def __init__(self, printToken, expr):
        self.printToken = printToken
        self.expr = expr
    
    def accept(self, visitor):
        return visitor.visitPrint(self)
    
class DeclarationStatment(Statment):
    def __init__(self, varToken, identifier, expr):
        self.varToken = varToken
        self.identifier = identifier
        self.expr = expr
    
    def accept(self, visitor):
        return visitor.visitDeclaration(self)
    
class AssignStatment(Statment):
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr

    def accept(self, visitor):
        return visitor.visitAssignment(self)
    
class BlockStatment(Statment):
    def __init__(self, statments):
        self.statments = statments
    
    def accept(self, visitor):
        return visitor.visitBlock(self)