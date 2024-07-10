from code_gen.environment import FunctionData
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class TypeAny(Visitor):
    """
    Check that all symbols have types.
    """
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[str] = []

        self._in_type = False
        self._in_method = False
        self._method_name :  str | None = None
        self._type_name : str = None
        self._stack : list[GetNode] = []
        self._program = None

    def check_any(self, program : ProgramNode) -> list[str]:
        self._check_any(program)
        return self._errors
    
    def log_error(self, error : str):
        self._errors.append(error)

    def visit_program_node(self, program_node : ProgramNode):
        new_program = ProgramNode([])
        for decl in program_node.decls:
            if isinstance(decl, ProtocolNode):
                continue
            self._check_any(decl)
            new_program.decls.append(decl)
        self._program = new_program
        
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme

        type_data = self._resolver.resolve_type_data(self._type_name)
        attr_data = type_data.attributes[attr_name]
        if attr_data.type == "Any": 
            self.log_error(f"Attribute {attr_name} of type {type_data.name} is not typed at line {attribute_node.id.line}")
        elif attr_data.type in self._resolver.resolve_protocols():
            attr_data.type = "Object"
    
    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        for param, type in method_node.params:
            if func_data.params[param.lexeme].type == "Any":
                self.log_error(f"Param {param.lexeme} of Method {func_name} is not typed {param.line}")
            elif func_data.params[param.lexeme].type in self._resolver.resolve_protocols():
                func_data.params[param.lexeme].type = "Object"
                

        declared_type = method_node.type
        self._check_any(method_node.body)

        if func_data.type == "Any":
            self.log_error(f"Method {func_name} is not typed at line {method_node.id.line}")
        elif func_data.type in self._resolver.resolve_protocols():
            func_data.type = "Object"
        self._in_method = False    
        self._method_name = None
        return None
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        for method in type_node.methods:
            self._check_any(method)

        self._in_type = False
        self._type_name = None   

    def visit_signature_node(self, signature_node : SignatureNode):
        pass
    
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    def visit_let_node(self, let_node : LetNode):
        self._resolver.next()

        for assig in let_node.assignments:
            # let assignments should be taken into account.
            var_name = assig.id.lexeme
            var_data = self._resolver.resolve_var_data(var_name)
            op_type = assig.type
            self._check_any(assig.body)
            if var_data.type == "Any":
                self.log_error(f"Variable {var_name} is not typed at line {assig.id.line}")
            elif var_data.type in self._resolver.resolve_protocols():
                var_data.type = "Object"                    
        self._check_any(let_node.body)
        self._resolver.next()

    def visit_while_node(self, while_node : WhileNode):
        self._check_any(while_node.condition) 
        self._check_any(while_node.body)
    
    def visit_if_node(self, if_node : IfNode):
        self._check_any(if_node.elsebody)
        for st in if_node.body:
            self._check_any(st[0])
            self._check_any(st[1])
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        print("No need")
        pass

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        print("No need implicit vector node")
        pass

    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        self._check_any(destructor_node.expr)
        pass

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            self._check_any(expr)
        
    def visit_call_node(self, call_node : CallNode):
        self._check_any(call_node.callee)
        for arg in call_node.args:
            self._check_any(arg)

    def visit_get_node(self, get_node : GetNode):
        self._check_any(get_node.left)
    
    def visit_set_node(self, set_node : SetNode):
        self._check_any(set_node.left)
        self._check_any(set_node.value)
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        print("No need set node vector")
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        self._check_any(vector_get_node.index)
        self._check_any(vector_get_node.left)

    def visit_new_node(self, new_node : NewNode):
        for arg in new_node.args:
            self._check_any(arg)
    
    def visit_binary_node(self, binary_node : BinaryNode):
        self._check_any(binary_node.left)
        self._check_any(binary_node.right)
    
    def visit_unary_node(self, unary_node : UnaryNode):
        self._check_any(unary_node.expr)
            
    def visit_literal_node(self, literal_node : LiteralNode):
        pass

    def _check_any(self, node : Statement) -> str:
        return node.accept(self)