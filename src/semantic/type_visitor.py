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
        self._in_method = False
        self._method_name :  str | None = None
        self._type_name : str = None
        self._stack : list[GetNode] = []

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
        
        declared_type = method_node.type.lexeme
        inferred_type = self._check_types(method_node.body)

        if declared_type != None:
            type_data = self._resolver.resolve_type_data(declared_type)
            if inferred_type not in type_data.descendants and inferred_type != declared_type:
                self._errors.append(f'Given type for method {func_name} in {self._type_name} does not conform with its return body')

        self._in_method = False    
        self._method_name = None
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
        self._resolver.next()

        for assig in let_node.assignments:
            var_name = assig.id.lexeme
            op_type = assig.type
            value = assig.body
            value_type = self._check_types(value)
            if op_type == None:
                var_data = self._resolver.resolve_var_data(var_name)
                var_data.type = value_type
            else:
                op_type_data = self._resolver.resolve_type_data(op_type.lexeme)
                if value_type not in op_type_data.descendants and value_type != op_type.lexeme:
                    self._errors("Types dismatch in variable initialization")
        
        f_type = self._check_types(let_node.body)
        self._resolver.next()
        return f_type

    
    def visit_while_node(self, while_node : WhileNode):
        self._check_types(while_node.condition)
        return self.check_types(while_node.body)

    
    def visit_if_node(self, if_node : IfNode):
        initial_type = self._check_types(if_node.elsebody)
        for st in if_node.body:
            self._check_types(st[0])
            type = self.check_types(st[1])
            initial_type = self._resolver.resolve_lowest_common_ancestor(initial_type, type)
        return initial_type
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass

    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        var_data = self._resolver.resolve_var_data(destructor_node.id.lexeme)
        inferred_type = self._check_types(destructor_node.expr)
        if inferred_type not in self._resolver.resolve_type_data(var_data.type).descendants and inferred_type != var_data.type:
            self._errors.append("Type doesn't conform in destructor node")
        return var_data.type

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            type = self._check_types(expr)
        return type
    
    def visit_call_node(self, call_node : CallNode):
        if isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme != "base":
            fn_name = call_node.callee.id.lexeme
            if fn_name not in self._resolver.resolve_functions():
                self._errors.append(f"Function {fn_name} is not defined")
                return "object"
            else:
                # check if number of arguments match
                fn_data = self._resolver.resolve_function_data(fn_name)
                if len(call_node.args) != len(fn_data.params):
                    self._errors.append(f"Function {fn_name} call doesn't match number of arguments")
                    return "object"
                for i, arg in enumerate(call_node.args):
                    inferred_type = self._check_types(arg)
                    param_var_data = fn_data.params[fn_data.params_index[i+1]]

                    fn_name = fn_name + "_" + self._type_name if self._in_type else fn_name

                    if param_var_data.type == None and self._method_name == fn_name:
                        param_var_data.type = inferred_type
                    elif param_var_data.type != None:
                        if inferred_type not in param_var_data.descendants and inferred_type != param_var_data.type:
                            self._errors.append(f"Argument must conform to parameter type")

                return fn_data.type
        elif isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme == "base":
            if not self._in_type:
                self._errors.append("Base outside type declaration")
                return "object"
            type_data = self._resolver.resolve_type_data(self._type_name)
            func_name = self._method_name
            if self._in_type:
                func_name = self._method_name[0 : self._method_name.rfind('_')]

            if type_data.ancestor == 'object':
                self._errors.append("Call to base and not inheriting")
                return "object"
            
            methods = type_data.methods[func_name]

            if len(methods) <= 2:
                self._errors.append("There is no ancestor with given method")
                return "object"

            method_name = methods[1]

            fn_name = method_name
            if fn_name not in self._resolver.resolve_functions():
                self._errors.append(f"Function {fn_name} is not defined")
                return "object"
            else:
                # check if number of arguments match
                fn_data = self._resolver.resolve_function_data(fn_name)
                if len(call_node.args) != len(fn_data.params):
                    self._errors.append(f"Function {fn_name} call doesn't match number of arguments")
                    return "object"
                for i, arg in enumerate(call_node.args):
                    inferred_type = self._check_types(arg)
                    param_var_data = fn_data.params[fn_data.params_index[i+1]]

                    fn_name = fn_name + "_" + self._type_name if self._in_type else fn_name

                    if param_var_data.type == None and self._method_name == fn_name:
                        param_var_data.type = inferred_type
                    elif param_var_data.type != None:
                        if inferred_type not in param_var_data.descendants and inferred_type != param_var_data.type:
                            self._errors.append(f"Argument must conform to parameter type")

                return fn_data.type
            
        elif not isinstance(call_node.callee, LiteralNode) and isinstance(call_node.callee, GetNode):
            fn_name = call_node.callee.id.lexeme
            left_inferred = self._check_types(call_node.callee)
            left_type_data = self._resolver.resolve_type_data(left_inferred)
            if fn_name not in left_type_data.methods:
                self._errors.append(f"{fn_name} is not a method of type {left_inferred}")
                return "object"
            
            fn_name = fn_name + "_" + left_inferred


            if fn_name not in self._resolver.resolve_functions():
                self._errors.append(f"Function {fn_name} is not defined")
                return "object"
            else:
                # check if number of arguments match
                fn_data = self._resolver.resolve_function_data(fn_name)
                if len(call_node.args) != len(fn_data.params):
                    self._errors.append(f"Function {fn_name} call doesn't match number of arguments")
                    return "object"
                for i, arg in enumerate(call_node.args):
                    inferred_type = self._check_types(arg)
                    param_var_data = fn_data.params[fn_data.params_index[i+1]]

                    fn_name = fn_name + "_" + self._type_name if self._in_type else fn_name

                    if param_var_data.type == None and self._method_name == fn_name:
                        param_var_data.type = inferred_type
                    elif param_var_data.type != None:
                        if inferred_type not in param_var_data.descendants and inferred_type != param_var_data.type:
                            self._errors.append(f"Argument must conform to parameter type")

                return fn_data.type

        else:
            self._errors.append("Cannot call methods or functions in that way. Function are not first order types in basic HULK");

    def visit_get_node(self, get_node : GetNode):
        self._stack.append(get_node)
        if len(self._stack) > 2:
            self._errors.append("After self should come at most one attribute")
        elif len(self._stack) == 2 and self._stack[-2].id != "self":
            self._errors.append("After self should come at most one attribute")
        self._stack.pop()
        return self._check_types(get_node.left)
    
    def visit_set_node(self, set_node : SetNode):
        if isinstance(set_node.left, LiteralNode) and set_node.left.id == "self" and self._in_type and self._in_method:
            var_data = self._resolver.resolve_var_data("self")
            if var_data.index != 0:
                self._errors.append("Attributes are private")
            else:
                type_data = self._resolver.resolve_type_data(var_data.type)
                if set_node.id.lexeme not in type_data.attributes:
                    self._errors.append("Attribute doesn't belong to class")
                
                infered_type = self._check_types(set_node.value)

                actual_type = type_data.attributes[set_node.id.lexeme].type 
                
                if actual_type == None:
                    return infered_type
                
                if infered_type not in type_data.descendants or infered_type != actual_type:
                    self._errors.append("Setting to attribute that doesn't conform")
                    return "object"

                return actual_type
                
        else:
            self._errors.append("Attributes are private")
        return "object"

    
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