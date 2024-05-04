from abc import ABC, abstractmethod

class Statment(ABC):
    @abstractmethod
    def accept(self, visitor):
        pass

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