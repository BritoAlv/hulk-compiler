from visitors.visitor import Visitor

class AstResolver(Visitor):
    def __init__(self):
        self.scopes = [{}]
        self.locals = {}

    def visitLiteral(self, literall):
        return
    
    def visitGrouping(self, group):
        group.expr.accept(self)

    def visitPrint(self, printt):
        printt.expr.accept(self)

    def visitIf(self, iff):
        iff.condition.accept(self)
        iff.then.accept(self)
        if iff.otherwise is not None:
            iff.otherwise.accept(self)


    def visitReturn(self, ret):
        if ret.expr is not None:
            ret.expr.accept(self)

    def visitUnary(self, unary):
        unary.exp.accept(self)

    def visitWhile(self, whilee):
        whilee.condition.accept(self)
        whilee.block.accpet(self)

    def visitTernary(self, ternary):
        ternary.left.accept(self)
        ternary.middle.accept(self)
        ternary.right.accept(self)

    def declare(self, name):
        act = self.scopes[-1]
        act[name] = False

    def define(self, name):
        act = self.scopes[-1]
        act[name] = True

    def beginScope(self):
        self.scopes.append({})

    def endScope(self):
        self.scopes.pop()

    def resolveProgram(self, program):
        for stat in program:
            stat.accept(self)
        return self.locals
    
    def visitBlockEnv(self, block):
        for stat in block.statments:
            stat.accept(self)

    def visitFor(self, forr):
        self.beginScope()
        if forr.initializer is not None:
            forr.initializer.accept(self)

        if forr.condition is not None:
            forr.condition.accept(self)
        
        if forr.action is not None:
            forr.action.accept(self)

        self.visitBlockEnv(forr.block)
        
        self.endScope()

    def visitContinue(self, continuee):
        return 
    

    def visitBinary(self, binary):
        binary.left.accept(self)
        binary.right.accept(self)
    
    def visitBreak(self, breakk):
        return 
    
    def visitCall(self, call):
        call.callee.accept(self)
        for ex in call.arguments:
            ex.accept(self)

    def visitFunctionDeclaration(self, fnDecl):
        self.declare(fnDecl.name)
        self.define(fnDecl.name)

        self.beginScope()
        for tok in fnDecl.params:
            self.declare(tok.lexeme)
            self.define(tok.lexeme)
        self.visitBlockEnv(fnDecl.bodyBlock)
        self.endScope()
        self.resolveLocal(fnDecl, fnDecl.name)

    def visitAssignment(self, assign):
        assign.expr.accept(self)
        self.resolveLocal(assign, assign.identifier.id.lexeme)

    def visitBlock(self, block):
        self.beginScope()
        self.visitBlockEnv(block)
        self.endScope()

    def visitDeclaration(self, decl):
        self.declare(decl.identifier.lexeme)
        if decl.expr is not None:
            decl.expr.accept(self)
        self.define(decl.identifier.lexeme)
        self.resolveLocal(decl, decl.identifier.lexeme)

    def visitVariable(self, var):
        self.resolveLocal(var, var.id.lexeme)

    def resolveLocal(self, expr, name):
        for i in range(len(self.scopes)-1, -1, -1):
            if name in self.scopes[i]:
                self.resolve(expr, len(self.scopes) -1 -i)
                break

    def resolve(self, expr, depth):
        self.locals[expr] = depth