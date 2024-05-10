from re import I
from visitors.visitor import Visitor


class IndentManager:
    def __init__(self, printer):
        self.printer = printer

    def __enter__(self):
        self.printer.indent += 1

    def __exit__(self, type, value, traceback):
        self.printer.indent -= 1


class TreePrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.current = ""

    def do_space(self):
        a = ""
        for i in range(0, self.indent):
            a += "    "
        return a + "└── "

    def add_word(self, word):
        self.current += self.do_space() + word + "\n"

    def visitFunctionDeclaration(self, fnDecl):
        self.add_word("define")
        with IndentManager(self):
            self.add_word("params :")

        with IndentManager(self):
            for param in fnDecl.params:
                self.add_word(" " + param.lexeme)

        with IndentManager(self):
            self.add_word("body : ")
            with IndentManager(self):
                fnDecl.bodyBlock.accept(self)

        return self.current

    def visitCall(self, call):
        self.add_word("call to ")
        with IndentManager(self):
            call.callee.accept(self)
            with IndentManager(self):
                for arg in call.arguments:
                    arg.accept(self)
        return self.current

    def visitReturn(self, returnn):
        self.add_word("return")
        with IndentManager(self):
            if returnn.expr != None:
                returnn.expr.accept(self)
        return self.current

    def visitBreak(self, breakk):
        self.add_word("break")
        return self.current

    def visitContinue(self, continuee):
        self.add_word("continue")
        return self.current

    def visitWhile(self, whilee):
        self.add_word("while")
        with IndentManager(self):
            self.add_word("Condition")
            with IndentManager(self):
                whilee.condition.accept(self)
            self.add_word("Do")
            with IndentManager(self):
                whilee.block.accept(self)
        return self.current

    def visitFor(self, forr):
        self.add_word("For")
        with IndentManager(self):
            if forr.initializer is not None:
                self.add_word("Initializer")
                with IndentManager(self):
                    forr.initializer.accept(self)

            if forr.condition is not None:
                self.add_word("Condition")
                with IndentManager(self):
                    forr.condition.accept(self)

            if forr.action is not None:
                self.add_word("Action")
                with IndentManager(self):
                    forr.action.accept(self)

            if forr.block is not None:
                self.add_word("Block")
                with IndentManager(self):
                    forr.block.accept(self)
        return self.current

    def visitIf(self, iff):
        self.add_word("If")
        with IndentManager(self):

            self.add_word("Condition")
            with IndentManager(self):
                iff.condition.accept(self)

            self.add_word("Then")
            with IndentManager(self):
                iff.then.accept(self)

            if iff.otherwise is not None:
                self.add_word("Else")
                with IndentManager(self):
                    iff.otherwise.accept(self)

        self.indent -= 1
        return self.current

    def visitBlock(self, block):
        self.add_word("Block")
        with IndentManager(self):
            self.add_word("{")
            for stat in block.statments:
                stat.accept(self)
            self.add_word("}")
        return self.current

    def visitLiteral(self, lit):
        self.add_word(lit.literal.lexeme)
        return self.current

    def visitVariable(self, var):
        self.add_word(var.id.lexeme)
        return self.current

    def visitAssignment(self, assign):
        self.add_word("Assign")
        with IndentManager(self):
            assign.identifier.accept(self)
            assign.expr.accept(self)
        return self.current

    def visitGrouping(self, group):
        self.add_word("(")
        with IndentManager(self):
            group.inside.accept(self)
        self.add_word(")")
        return self.current

    def visitUnary(self, unary):
        self.add_word(unary.operator.lexeme)
        with IndentManager(self):
            unary.exp.accept(self)
        return self.current

    def visitBinary(self, binary):
        self.add_word(binary.operator.lexeme)
        with IndentManager(self):
            binary.left.accept(self)
            binary.right.accept(self)
        return self.current

    def visitTernary(self, ternary):
        self.add_word(ternary.op1.lexeme)
        with IndentManager(self):
            ternary.left.accept(self)
        self.add_word(ternary.op2.lexeme)
        with IndentManager(self):
            ternary.middle.accept(self)
            ternary.right.accept(self)
        return self.current

    def visitPrint(self, printt):
        self.add_word("print")
        with IndentManager(self):
            printt.expr.accept(self)
        return self.current

    def visitDeclaration(self, decl):
        self.add_word("var " + decl.identifier.lexeme)
        with IndentManager(self):
            decl.expr.accept(self)
        return self.current