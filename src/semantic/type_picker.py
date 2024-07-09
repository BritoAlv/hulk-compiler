from code_gen.environment import FunctionData
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class TypePicker(Visitor):
    """
    Set Types for the given symbols in the Program.
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

        type_data = self._resolver.resolve_type_data(self._type_name)
        
        if attribute_node.type != None: 
            stated_type = attribute_node.type.lexeme
            type_data.attributes[attr_name].type = stated_type
        else:
            type_data.attributes[attr_name].type = "Any"
    
    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        for param, type in method_node.params:
            if type != None:
                func_data.params[param.lexeme].type = type.lexeme
                continue
            else:
                func_data.params[param.lexeme].type = "Any"

        declared_type = method_node.type
        self._pick_types(method_node.body)

        if declared_type != None:
            declared_type = declared_type.lexeme
            func_data.type = declared_type
        else:
            func_data.type = "Any"

        self._in_method = False    
        self._method_name = None
        return None
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        for method in type_node.methods:
            self._pick_types(method)

        self._in_type = False
        self._type_name = None   

    def visit_signature_node(self, signature_node : SignatureNode):
        print("No need")
        pass
    
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        print("No need")
        pass

    def visit_let_node(self, let_node : LetNode):
        self._resolver.next()

        for assig in let_node.assignments:
            # let assignments should be taken into account.
            var_name = assig.id.lexeme
            var_data = self._resolver.resolve_var_data(var_name)
            op_type = assig.type
            self._pick_types(assig.body)
            if op_type != None:
                var_data.type = op_type.lexeme
            else:
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
            self._pick_types(st[1])
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        print("No need")
        pass

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        print("No need implicit vector node")
        pass

    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        self._pick_types(destructor_node.expr)
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
        print("No need set node vector")
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