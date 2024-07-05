from code_gen.environment import FunctionData
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class TypePicker(Visitor):
    """
    Visit all nodes and set to the resolver / context / environment all the explicit types given by the user. Do not deduce any type, only check for existence, 
    if not type was not declared set to None.
    """
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[str] = []

        self._in_type = False
        self._in_method = False
        self._method_name :  str | None = None
        self._type_name : str = None
        self._stack : list[GetNode] = []

    def pick_types(self, program : ProgramNode) -> list[str]:
        self._pick_types(program)
        return self._errors
    
    def log_error(self, error : str):
        self._errors.append(error)

    def visit_program_node(self, program_node : ProgramNode):
        for decl in program_node.decls:
            self._pick_types(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        
        if not self._in_type:
            self.log_error(f'Attribute {attribute_node.id.lexeme} declaration must be inside a type declaration at line {attribute_node.id.line}')
            self._pick_types(attribute_node.body)
            return None
        
        type_data = self._resolver.resolve_type_data(self._type_name)
        
        if attr_name not in type_data.attributes:
            self.log_error(f"Attribute {attr_name} not in {self._type_name} attributes at line {attribute_node.id.line}")
            return None
        
        if attribute_node.type != None: 
            stated_type = attribute_node.type.lexeme
            if stated_type not in self._resolver.resolve_types():
                self.log_error(f"Type {stated_type} given for attribute {attr_name} in type declaration {self._type_name} does not exist at line {attribute_node.id.line}")
    
    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if func_name in ["print", "error"] and not self._in_type:
            self.log_error(f"Can't declare a method called [print, error] at line {method_node.id.line}")

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        for param, type in method_node.params:
            if type != None and type.lexeme in self._resolver.resolve_types():
                func_data.params[param.lexeme].type = type.lexeme
                continue
            elif type != None:
                self.log_error(f"Parameter Type {type.lexeme} given for param {param.lexeme} at method {method_node.id.lexeme} " + (f"in type declaration {self._type_name}" if self._in_type else "") + f" does not exist at line {method_node.id.line}")
                type.lexeme = "Object"
            else:
                type.lexeme = "Any"
        
    
        declared_type = method_node.type
        self._pick_types(method_node.body)

        if declared_type != None:
            declared_type = declared_type.lexeme
            if declared_type in self._resolver.resolve_types():
                func_data.type = declared_type
            else:
                self.log_error(f"Type {declared_type} given for method {method_node.id.lexeme} " + (f"in type declaration {self._type_name}" if self._in_type else "") + f" does not exist at line {method_node.id.line}")

        self._in_method = False    
        self._method_name = None
        return None
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        if self._type_name in ["error", "Any"]:
            self.log_error(f"Can't declare [error, Any] as typenames")

        for method in type_node.methods:
            self._pick_types(method)

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
            self._pick_types(assig.body)
            if op_type != None and op_type in self._resolver.resolve_types():
                var_data.type = op_type
                continue
            elif op_type != None:
                self.log_error(f"Given tipe for variable {var_name} in let_expression doesn't exist at line {assig.id.line}")
            
            var_data.type = "Any"
        
        self._pick_types(let_node.body)
        self._resolver.next()

    def visit_while_node(self, while_node : WhileNode):
        self._pick_types(while_node.condition) 
        self._pick_types(while_node.body)
    
    def visit_if_node(self, if_node : IfNode):
        self._pick_types(if_node.elsebody)
        for st in if_node.body:
            self._pick_types(st[0])
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            self._pick_types(expr)
        
    def visit_call_node(self, call_node : CallNode):
        self._pick_types(call_node.callee)
        for arg in call_node.args:
            self._pick_types(arg)

    def visit_get_node(self, get_node : GetNode):
        self._pick_types(get_node.left)
    
    def visit_set_node(self, set_node : SetNode):
        self._pick_types(set_node.left)
        self._pick_types(set_node.value)
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        self._pick_types(vector_get_node.index)
        self._pick_types(vector_get_node.left)

    def visit_new_node(self, new_node : NewNode):
        for arg in new_node.args:
            self._pick_types(arg)
    
    def visit_binary_node(self, binary_node : BinaryNode):
        self._pick_types(binary_node.left)
        self._pick_types(binary_node.right)
    
    def visit_unary_node(self, unary_node : UnaryNode):
        self._pick_types(unary_node.expr)
            
    def visit_literal_node(self, literal_node : LiteralNode):
        pass

    def _pick_types(self, node : Statement) -> str:
        return node.accept(self)