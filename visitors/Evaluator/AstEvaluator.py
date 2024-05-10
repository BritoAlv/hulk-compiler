from lexer.tokenType import TokenType
from parser.statments import BreakStatement, ContinueStatement, ReturnStatement
from visitors.Evaluator.Callable import FunctionCallable
from visitors.Evaluator.environment import Environment
from visitors.visitor import Visitor

class AstEvaluator(Visitor):
    def __init__(self, variables):
        self.environment = Environment()
        self.locals = variables

    def set_environment(self, environment):
        self.environment = environment

    def push_environment(self):
        self.environment = Environment(self.environment)

    def pop_environment(self):
        self.environment = self.environment.get_distance(1)

    def visitBlockEnvironment(self, block):
        for stat in block.statments:
            stat.accept(self)

    def visitFunctionDeclaration(self, fn_decl):
        callableFunction = FunctionCallable(fn_decl, self.environment)
        self.environment.define(self.locals[fn_decl], fn_decl.name, callableFunction)

    def visitCall(self, call):
        fn = call.callee.accept(self)
        try:
            if isinstance(fn, FunctionCallable):
                args_ev = []
                for arg1 in call.arguments:
                    args_ev.append(arg1.accept(self))
                if len(args_ev) != fn.fnDecl.arity:
                    raise Exception("Call to function but not with the same number of arguments")
                prev = self.environment
                self.set_environment(fn.environment)
                self.push_environment()
                for i in range(0, len(args_ev)):
                    self.environment.define(0, fn.fnDecl.params[i].lexeme, args_ev[i])
                result = None
                try:
                    self.visitBlockEnvironment(fn.fnDecl.bodyBlock)
                except Exception as e:
                    if len(e.args) > 0 and isinstance(e.args[0], ReturnStatement):
                        result = (None if e.args[0] is None else e.args[0].expr.accept(self))
                    else:
                        raise e
                self.pop_environment()
                self.set_environment(prev)
                return result
            else:
                raise Exception("Trying to call something that is not a function")
        except Exception as e:
            raise e

    def visitReturn(self, returnn):
        raise Exception(returnn)

    def visitBreak(self, breakk):
        raise Exception(breakk)

    def visitContinue(self, continuee):
        raise Exception(continuee)

    def visitFor(self, forr):
        self.push_environment()
        if forr.initializer is not None:
            forr.initializer.accept(self)

        while (forr.condition is None) or forr.condition.accept(self):
            try:
                self.visitBlockEnvironment(forr.block)
            except Exception as e:
                if len(e.args) == 0:
                    raise e
                elif isinstance(e.args[0], BreakStatement):
                    break
                elif not isinstance(e.args[0], ContinueStatement):
                    raise e
            if forr.action is not None:
                forr.action.accept(self)
        self.pop_environment()

    def visitWhile(self, whilee):
        condition = whilee.condition.accept(self)
        while condition:
            try:
                whilee.block.accept(self)
            except Exception as e:
                if len(e.args) == 0:
                    raise e
                elif isinstance(e.args[0], BreakStatement):
                    break
                elif not isinstance(e.args[0], ContinueStatement):
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
        self.push_environment()
        self.visitBlockEnvironment(block)
        self.pop_environment()

    def visitDeclaration(self, decl):
        iden = decl.identifier.lexeme
        value = decl.expr.accept(self)
        self.environment.define(self.locals[decl], iden, value)

    def visitVariable(self, var):
        d = self.locals[var]
        return self.environment.get(d, var.id.lexeme)

    def visitLiteral(self, lit):
        return lit.literal.literal

    def visitGrouping(self, group):
        return group.inside.accept(self)

    def visitAssignment(self, assign):
        value = assign.expr.accept(self)
        return self.environment.set(self.locals[assign], assign.identifier.id.lexeme, value)

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
                return left ** right
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