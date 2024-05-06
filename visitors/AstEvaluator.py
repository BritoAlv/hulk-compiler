from lexer.tokenType import TokenType
from parser.environment import Environment
from parser.statments import BreakStatment, ContinueStatment, FunctionDeclaration, ReturnStatment
from visitors.visitor import Visitor


class AstEvaluator(Visitor):
    def __init__(self):
        self.environment = Environment()

    def visitFunctionDeclaration(self, fnDecl):
        self.environment.define(fnDecl.name, fnDecl)

    def visitCall(self, call):
        fn = self.environment.get(call.callee.lexeme)
        try:
            if isinstance(fn, FunctionDeclaration):
                args_ev = []
                for arg1 in call.arguments:
                    args_ev.append(arg1.accept(self))
                if len(args_ev) != fn.arity:
                    raise Exception("Call to function but not with the same number of arguments")
                
                self.environment = Environment(self.environment)
                for i in range(0, len(args_ev)):
                    self.environment.define(fn.params[i].lexeme , args_ev[i])
                result = None
                try:
                    self.visitBlock(fn.bodyBlock)
                except Exception as e:
                    if len(e.args) > 0 and isinstance(e.args[0], ReturnStatment):
                        result = e.args[1].result
                self.environment = self.environment.enclosing
                return result       
            else:
                raise Exception("Trying to call something that is not a function")
        except:
            raise Exception("No identifier for this function")

    def visitReturn(self, returnn):
        raise Exception(returnn, returnn.expr.accept(self))
    
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
