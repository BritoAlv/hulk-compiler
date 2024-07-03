from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor


class TypeVisitor(Visitor):
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[str] = []

        self._in_type = False
        self._type_name : str = None
        self._stack = []

    def check_types(self, program : ProgramNode) -> list[str]:
        self._check_types(program)
        return self._errors
        

    def visit_program_node(self, program_node : ProgramNode):
        for decl in program_node.decls:
            self._check_types(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        if not self._in_type:
            self._errors.append('Attribute declaration must be inside a type declaration')
            self._check_types(attribute_node.body)
            return None
        
        type_data = self._resolver.resolve_type_data(self._type_name)
        var_data = type_data.attributes[attr_name]

        if attribute_node.type != None: 
            var_data.type = attribute_node.type.lexeme

        inferred_type = self._check_types(attribute_node.body)

        if var_data.type == None:
            var_data.type = inferred_type
        else:
            type_data = self._resolver.resolve_type_data(var_data.type)
            if inferred_type not in type_data.descendants and inferred_type != var_data.type:
                self._errors.append(f'Given type for attribute {attr_name} in {self._type_name} does not conform with its initialization body')
        
        return None

    
    def visit_method_node(self, method_node : MethodNode):
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        for param, type in method_node.params:
            if type != None:
                func_data.params[param.lexeme].type = type.lexeme
        
        declared_type = method_node.type.lexeme
        inferred_type = self._check_types(method_node.body)

        if declared_type != None:
            type_data = self._resolver.resolve_type_data(declared_type)
            if inferred_type not in type_data.descendants and inferred_type != declared_type:
                self._errors.append(f'Given type for method {func_name} in {self._type_name} does not conform with its return body')
        
        return None
        
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        for method in type_node.methods:
            self._check_types(method)

        self._in_type = False
        self._type_name = None   

    
    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    
    def visit_let_node(self, let_node : LetNode):
        pass

    
    def visit_while_node(self, while_node : WhileNode):
        pass

    
    def visit_if_node(self, if_node : IfNode):
        pass

    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        pass

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            type = self._check_types(expr)
        return type

    
    def visit_call_node(self, call_node : CallNode):
        pass

    
    def visit_get_node(self, get_node : GetNode):
        pass

    
    def visit_set_node(self, set_node : SetNode):
        pass

    
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass

    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        if self._check_types(vector_get_node.index) != 'number':
            self._errors.append('Cannot index a vector with a non-numerical type')
        
        inferred_type = self._check_types(vector_get_node.left)

        if not inferred_type.startswith('vector~'):
            self._errors.append('Cannot index a non-vector type')
            return 'object'
        
        return inferred_type.split('~')[1]

    def visit_new_node(self, new_node : NewNode):
        type_name = new_node.id.lexeme
        if type_name not in self._resolver.resolve_types():
            self._errors.append('Cannot instantiate a not declared type')
            return 'object'
        return type_name

    
    def visit_binary_node(self, binary_node : BinaryNode):
        left_inferred_type = self._check_types(binary_node.left)
        op = binary_node.op.type
        if op == 'is' and isinstance(binary_node.right, LiteralNode):
            is_type = binary_node.right.id.lexeme

            if is_type not in self._resolver.resolve_types():
                self._errors.append('Right operand of is must be an existing type')
            else:
                type_data = self._resolver.resolve_type_data(left_inferred_type)
                if is_type not in type_data.descendants:
                    self._errors.append('Left operand type must be a descendant of right operand')

            return 'bool'

        if op == 'as' and isinstance(binary_node.right, LiteralNode):
            as_type = binary_node.right.id.lexeme

            if as_type not in self._resolver.resolve_types():
                self._errors.append('Right operand of is must be an existing type')
            else:
                type_data = self._resolver.resolve_type_data(as_type)
                if left_inferred_type not in type_data.descendants:
                    self._errors.append('Left operand type must be an ancestor of right operand')

            return as_type

        right_inferred_type = self._check_types(binary_node.right)

        match binary_node.op.type:
            case 'plus', 'minus', 'star', 'div', 'powerOp', 'modOp', 'greater', 'less', 'greaterEq', 'lessEq':
                if left_inferred_type != 'number' or right_inferred_type != 'number':
                    self._errors.append('Cannot apply binary operation to non-numerical types')

                if op in ['greater', 'less', 'greaterEq', 'lessEq']:
                    return 'bool'
                
                return 'number'
            case 'and', 'or':
                if left_inferred_type != 'bool' or right_inferred_type != 'bool':
                    self._errors.append('Cannot apply binary operation to non-boolean types')
                return 'bool'
            case 'doubleEqual', 'notEqual':
                return 'bool'
    
    def visit_unary_node(self, unary_node : UnaryNode):
        inferred_type = self._check_types(unary_node.expr)
        if unary_node.op.type == 'not':
            if inferred_type != 'bool':
                self._errors.append('Cannot negate a non-boolean expression')
            return 'bool'
        else:
            if inferred_type != 'number':
                self._errors.append('Cannot negate a non-numerical expression')
            return 'number'
            
    
    def visit_literal_node(self, literal_node : LiteralNode):
        match literal_node.id.type:
            case 'number':
                return 'number'
            case 'string':
                return 'string'
            case 'true', 'false':
                return 'bool'
            case 'null':
                return 'object'
            case 'id':
                try:
                    self._resolver.resolve_var_data(literal_node.id.lexeme).type
                except:
                    self._errors.append(f'Variable {literal_node.id.lexeme} was not declared')

                

    def _check_types(self, node : Statement) -> str:
        return node.accept(self)