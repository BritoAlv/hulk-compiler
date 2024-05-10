from abc import ABC, abstractmethod


class Visitor(ABC):
    @abstractmethod
    def visitLiteral(self, lit):
        pass

    @abstractmethod
    def visitGrouping(self, group):
        pass

    @abstractmethod
    def visitUnary(self, unary):
        pass

    @abstractmethod
    def visitBinary(self, binary):
        pass

    @abstractmethod
    def visitTernary(self, ternary):
        pass

    @abstractmethod
    def visitPrint(self, print):
        pass

    @abstractmethod
    def visitDeclaration(self, decl):
        pass

    @abstractmethod
    def visitVariable(self, var):
        pass

    @abstractmethod
    def visitAssignment(self, assign):
        pass

    @abstractmethod
    def visitBlock(self, block):
        pass

    @abstractmethod
    def visitIf(self, iff):
        pass

    @abstractmethod
    def visitFor(self, forr):
        pass

    @abstractmethod
    def visitWhile(self, whilee):
        pass

    @abstractmethod
    def visitBreak(self, breakk):
        pass

    @abstractmethod
    def visitContinue(self, continuee):
        pass

    @abstractmethod
    def visitCall(self, call):
        pass

    @abstractmethod
    def visitReturn(self, returnn):
        pass

    @abstractmethod
    def visitFunctionDeclaration(self, fnDecl):
        pass