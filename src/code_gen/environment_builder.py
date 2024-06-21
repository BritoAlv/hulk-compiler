
from hmac import new
from code_gen.environment import Context, Environment
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, Statement, TypeNode
from common.visitor import Visitor


class EnvironmentBuilder(Visitor):
    def __init__(self) -> None:
        self._environment : Environment = None
        self._context : Context = None
        self._params : dict[str, str] = None
        self._var_index : int = 0
        self._func_name : str

    def build(self, program: ProgramNode) -> Environment:
        self._environment = Environment()
        self._build(program)
        return self._environment

    def visit_program_node(self, program_node: ProgramNode):
        for decl in program_node.decls:
            self._build(decl)
    
    def visit_method_node(self, method_node: MethodNode):
        func_name = method_node.id.lexeme

        # Create function context
        self._var_index = 0 # Reset var_index
        self._environment.add(func_name)
        self._context = self._environment.get_context(func_name)
        self._params = self._environment.get_params(func_name)
        self._func_name = func_name

        # Link parameters to argument registers and to stack (if more than 4 parameters)
        i = 0
        for param in method_node.params:
            param_name = param[0].lexeme

            if param_name in self._params:
                    raise Exception("Params must be named differently")
            
            self._params[param_name] = self._var_index
            self._var_index += 1

            i += 1
                
        self._build(method_node.body)
        self._environment.add_variables(func_name, self._var_index)

    # TODO: Fix this
    def visit_let_node(self, let_node: LetNode):
        old_context = self._create_context()

        for var, value in let_node.assignments:
            var_name = var.lexeme
            if var_name in self._context.variables:
                raise Exception("Cannot declare the same variable twice in the same scope")
            elif var_name in self._params:
                raise Exception("Variable is already used as a parameter name")
            
            self._context.variables[var_name] = self._var_index
            self._var_index += 1
            self._build(value)

        self._build(let_node.body)
        
        self._context = old_context

    def visit_block_node(self, block_node: BlockNode):
        old_context = self._create_context()

        for expr in block_node.exprs:
            self._build(expr)

        self._context = old_context     

    def visit_destructor_node(self, destructor_node: DestructorNode):
        self._build(destructor_node.expr)

    def visit_binary_node(self, binary_node: BinaryNode):
        left_expr = binary_node.left
        right_expr = binary_node.right

        self._build(left_expr)
        self._build(right_expr)        

    def visit_call_node(self, call_node: CallNode):
        self._build(call_node.callee)
        
        for expr in call_node.args:
            self._build(expr)

    def visit_type_node(self, type_node: TypeNode):
        pass

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        pass

    def visit_signature_node(self, signature_node: SignatureNode):
        pass
    
    def visit_if_node(self, if_node: IfNode):
        pass

    def visit_while_node(self, while_node: WhileNode):
        pass

    def visit_for_node(self, for_node: ForNode):
        pass

    def visit_new_node(self, new_node: NewNode):
        pass
    
    def visit_get_node(self, get_node: GetNode):
        pass

    def visit_set_node(self, set_node: SetNode):
        pass

    def visit_explicit_vector_node(self, explicit_vector_node: ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node: ImplicitVectorNode):
        pass

    def visit_vector_get_node(self, vector_get_node: VectorGetNode):
        pass

    def visit_vector_set_node(self, vector_set_node: VectorSetNode):
        pass

    def visit_literal_node(self, literal_node: LiteralNode):
        pass

    def _build(self, stmt : Statement):
        return stmt.accept(self)
    
    def _create_context(self):
        old_context = self._context

        if old_context == None:
            self._context = Context()
            self._environment.add_context(self._func_name, self._context)
        else:
            new_context = Context()
            new_context.parent = old_context
            old_context.children.append(new_context)
            self._context = new_context

        return old_context