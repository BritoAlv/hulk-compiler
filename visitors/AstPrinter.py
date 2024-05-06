from visitors.visitor import Visitor


class TreePrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.current = ""

    def do_space(self):
        a = ""
        for i in range(0, self.indent):
            a += "    "
        return a + "└── "

    def visitFunctionDeclaration(self, fnDecl):
        self.current += self.do_space() + "define : " + fnDecl.name + "\n"
        self.indent += 1
        self.current += self.do_space() + "params :" + "\n"
        self.indent += 1
        for param in fnDecl.params:
            self.current += self.do_space() + " " + param.lexeme + "\n"
        self.indent -= 1
        self.current += self.do_space() + "body : " + "\n"
        self.indent += 1
        fnDecl.bodyBlock.accept(self)
        self.indent -= 1
        self.indent -= 1
        return self.current

    def visitCall(self, call):
        self.current += self.do_space() + "call to " + "\n"
        self.indent += 1
        call.callee.accept(self)
        self.indent += 1
        for arg in call.arguments:
            arg.accept(self)
        self.indent -= 1
        self.indent -= 1
        return self.current


    def visitReturn(self, returnn):
        self.current += self.do_space() + "return" + "\n"
        self.indent += 1
        returnn.expr.accept(self)
        self.indent -= 1
        return self.current

    def visitBreak(self, breakk):
        self.current += self.do_space() + "break" + "\n"
        return self.current

    def visitContinue(self, continuee):
        self.current += self.do_space() + "continue" + "\n"
        return self.current

    def visitWhile(self, whilee):
        self.current += self.do_space() + "while" + "\n"
        self.indent += 1

        self.current += self.do_space() + "Condition" + "\n"
        self.indent += 1
        whilee.condition.accept(self)
        self.indent -= 1

        self.current += self.do_space() + "Do" + "\n"
        self.indent += 1
        whilee.block.accept(self)
        self.indent -= 1

        self.indent -= 1
        return self.current

    def visitFor(self, forr):
        self.current += self.do_space() + "For" + "\n"
        self.indent += 1

        if forr.initializer is not None:
            self.current += self.do_space() + "Initializer" + "\n"
            self.indent += 1
            forr.initializer.accept(self)
            self.indent -= 1

        if forr.condition is not None:
            self.current += self.do_space() + "Condition" + "\n"
            self.indent += 1
            forr.condition.accept(self)
            self.indent -= 1

        if forr.action is not None:
            self.current += self.do_space() + "Action" + "\n"
            self.indent += 1
            forr.action.accept(self)
            self.indent -= 1

        if forr.block is not None:
            self.current += self.do_space() + "Block" + "\n"
            self.indent += 1
            forr.block.accept(self)
            self.indent -= 1

        self.indent -= 1
        return self.current

    def visitIf(self, iff):
        self.current += self.do_space() + "If" + "\n"
        self.indent += 1

        self.current += self.do_space() + "Condition" + "\n"
        self.indent += 1
        iff.condition.accept(self)
        self.indent -= 1

        self.current += self.do_space() + "Then" + "\n"
        self.indent += 1
        iff.then.accept(self)
        self.indent -= 1

        if iff.otherwise is not None:
            self.current += self.do_space() + "Else" + "\n"
            self.indent += 1
            iff.otherwise.accept(self)
            self.indent -= 1

        self.indent -= 1
        return self.current

    def visitBlock(self, block):
        self.current += self.do_space() + "Block" + "\n"
        self.indent += 1
        for stat in block.statments:
            stat.accept(self)
        self.indent -= 1
        return self.current

    def visitLiteral(self, lit):
        self.current += self.do_space() + lit.literal.lexeme + "\n"
        return self.current

    def visitVariable(self, var):
        self.current += self.do_space() + var.id.lexeme + "\n"
        return self.current

    def visitAssignment(self, assign):
        self.current += self.do_space() + "Assign" + "\n"
        self.indent += 1
        assign.identifier.accept(self)
        assign.expr.accept(self)
        return self.current

    def visitGrouping(self, group):
        self.current += self.do_space() + "(" + "\n"
        self.indent += 1
        group.inside.accept(self)
        self.indent -= 1
        self.current += self.do_space() + ")" + "\n"
        return self.current

    def visitUnary(self, unary):
        self.current += self.do_space() + unary.operator.lexeme + "\n"
        self.indent += 1
        unary.exp.accept(self)
        self.indent -= 1
        return self.current

    def visitBinary(self, binary):
        self.current += self.do_space() + binary.operator.lexeme + "\n"
        self.indent += 1
        binary.left.accept(self)
        binary.right.accept(self)
        self.indent -= 1
        return self.current

    def visitTernary(self, ternary):
        self.current += self.do_space() + ternary.op1.lexeme + "\n"
        self.indent += 1
        ternary.left.accept(self)
        self.indent -= 1
        self.current += self.do_space() + ternary.op2.lexeme + "\n"
        self.indent += 1
        ternary.middle.accept(self)
        ternary.right.accept(self)
        self.indent -= 1
        return self.current

    def visitPrint(self, printt):
        self.current += self.do_space() + "print" + "\n"
        self.indent += 1
        printt.expr.accept(self)
        self.indent -= 1
        return self.current

    def visitDeclaration(self, decl):
        self.current += self.do_space() + "var " + decl.identifier.lexeme + "\n"
        self.indent += 1
        decl.expr.accept(self)
        self.indent -= 1
        return self.current