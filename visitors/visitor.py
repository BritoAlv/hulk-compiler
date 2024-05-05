from abc import ABC, abstractmethod
from lexer.lexer import TokenType
from parser.environment import Environment
from parser.statments import BreakStatment, ContinueStatment

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


class TreePrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.current = ""

    def do_space(self):
        a = ""
        for i in range(0, self.indent):
            a += "    "
        return a + "└── "

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


class AstEvaluator(Visitor):
    def __init__(self):
        self.environment = Environment()

    def visitBreak(self, breakk):
        raise Exception(breakk)
    
    def visitContinue(self, continuee):
        raise Exception(continuee)

    def visitFor(self, forr):
        self.environment = Environment(self.environment)
        if forr.initializer is not None:
            forr.initializer.accept(self)

        while (forr.condition is None) or forr.condition.accept(self):
            try:
                forr.block.accept(self)
            except Exception as e:
                if len(e.args) == 0:
                    raise e
                elif isinstance(e.args[0], BreakStatment):
                    break
                elif not isinstance(e.args[0], ContinueStatment):
                    raise e
            if forr.action is not None:
                forr.action.accept(self)
        self.environment = self.environment.enclosing

    def visitWhile(self, whilee):
        condition = whilee.condition.accept(self)
        while condition:
            try:
                whilee.block.accept(self)
            except Exception as e:
                if len(e.args) == 0:
                    raise e
                elif isinstance(e.args[0], BreakStatment):
                    break
                elif not isinstance(e.args[0], ContinueStatment):
                    raise e
            condition = whilee.condition.accept(self)

    def visitIf(self, iff):
        condition = iff.condition.accept(self)
        if condition:
            iff.then.accept(self)
        elif iff.otherwise is not None:
            iff.otherwise.accept(self)

    def visitPrint(self, printt):
        value = printt.expr.accept(self)
        print(value)

    def visitBlock(self, block):
        self.environment = Environment(self.environment)
        for stat in block.statments:
            stat.accept(self)
        self.environment = self.environment.enclosing

    def visitDeclaration(self, decl):
        iden = decl.identifier.lexeme
        value = decl.expr.accept(self)
        self.environment.define(iden, value)

    def visitVariable(self, var):
        return self.environment.get(var.id.lexeme)

    def visitLiteral(self, lit):
        return lit.literal.literal

    def visitGrouping(self, group):
        return group.inside.accept(self)

    def visitAssignment(self, assign):
        value = assign.expr.accept(self)
        return self.environment.set(assign.identifier.id.lexeme, value)

    def visitUnary(self, unary):
        value = unary.exp.accept(self)
        match unary.operator.tokenType:
            case TokenType.MINUS:
                return -value
            case TokenType.NOT:
                if value == 0:
                    return 1
                else:
                    return 0
            case _:
                raise Exception("How evaluates unary operator: ")

    def visitTernary(self, ternary):
        if (
            ternary.op1.tokenType == TokenType.TERNARY_COND
            and ternary.op2.tokenType == TokenType.TERNARY_SEP
        ):
            if ternary.left.accept(self) != 0:
                return ternary.middle.accept(self)
            else:
                return ternary.right.accept(self)
        else:
            raise Exception("This ternary combination is not implemented")

    def visitBinary(self, binary):
        left = binary.left.accept(self)
        right = binary.right.accept(self)
        match binary.operator.tokenType:
            case TokenType.PLUS:
                return left + right
            case TokenType.MINUS:
                return left - right
            case TokenType.MULT:
                return left * right
            case TokenType.DIV:
                return left // right
            case TokenType.EXP:
                return left**right
            case TokenType.XOR:
                return left ^ right
            case TokenType.AND:
                return left and right
            case TokenType.OR:
                return left or right
            case TokenType.NAND:
                return not (left and right)
            case TokenType.GREATER:
                if left > right:
                    return 1
                return 0
            case TokenType.GREATER_EQUAL:
                if left >= right:
                    return 1
                return 0
            case TokenType.LESS:
                if left < right:
                    return 1
                return 0
            case TokenType.LESS_EQUAL:
                if left <= right:
                    return 1
                return 0
            case TokenType.EQUAL:
                if left == right:
                    return 1
                return 0
            case TokenType.NOT_EQUAL:
                if left != right:
                    return 1
                return 0

            case TokenType.SHIFT_LEFT:
                return left << right

            case TokenType.SHIFT_RIGHT:
                return left >> right

            case _:
                raise Exception(
                    "How evaluates binary operator: "
                    + binary.operator.tokentype.toString(False)
                )
