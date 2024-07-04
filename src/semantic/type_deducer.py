from regex import P
from code_gen.environment import FunctionData
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class TypeDeducer(Visitor):
    """
    Deduce types of the program:
        if type is already stated by the user then check that deduced type by context conforms with stated type.
        if type is not given by the user then deduced type should be able to ensure all the operations requested for it in the context.  
    """
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
    
    def log_error(self, error : str):
        self._errors.append(error)

    def visit_program_node(self, program_node : ProgramNode): 
        for decl in program_node.decls:
            self._check_types(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        if not self._in_type:
            self.log_error(f'Attribute {attribute_node.id.lexeme} declaration must be inside a type declaration at line {attribute_node.id.line}')
            self._check_types(attribute_node.body)
            return None
        
        type_data = self._resolver.resolve_type_data(self._type_name)
        
        if attr_name not in type_data.attributes:
            self.log_error(f"Attribute {attr_name} not in {self._type_name} attributes at line {attribute_node.id.line}")
            return None
        
        var_data = type_data.attributes[attr_name]

        inferred_type = self._check_types(attribute_node.body)

        if var_data.type == None:
            var_data.type = inferred_type
        else:
            type_data = self._resolver.resolve_type_data(var_data.type)
            if inferred_type not in type_data.descendants and inferred_type != var_data.type:
                self.log_error(f'Given type for attribute {attr_name} in {self._type_name} does not conform with its initialization body at line {attribute_node.id.line}')
        
        return None

    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        declared_type = method_node.type.lexeme
        inferred_type = self._check_types(method_node.body)

        if declared_type != None:
            type_data = self._resolver.resolve_type_data(declared_type)
            if inferred_type not in type_data.descendants and inferred_type != declared_type:
                self.log_error(f'Given type for method {func_name} in {self._type_name} does not conform with its return body at line {method_node.id.line}')
        else:
            func_data.type = inferred_type

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
            # let assignments should be taken into account.
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
                    self.log_error(f"Type {value_type} does not conform with {op_type.lexeme} in Let Expression near line {assig.id.line}")
        
        f_type = self._check_types(let_node.body)
        self._resolver.next()
        return f_type

    def visit_while_node(self, while_node : WhileNode):
        if self._check_types(while_node.condition) != 'bool':
            self.log_error(f'While condition must evaluate to a boolean')
        return self._check_types(while_node.body)
    
    def visit_if_node(self, if_node : IfNode):
        initial_type = self._check_types(if_node.elsebody)
        for st in if_node.body:
            if self._check_types(st[0]) != 'bool':
                self.log_error(f"Conditions of if / elif must evaluate to a boolean")
            type = self._check_types(st[1])
            initial_type = self._resolver.resolve_lowest_common_ancestor(initial_type, type)
        return initial_type
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        pass
    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        pass

    def visit_destructor_node(self, destructor_node : DestructorNode):
        var_name = destructor_node.id.lexeme
        try:
            var_data = self._resolver.resolve_var_data(var_name)
            inferred_type = self._check_types(destructor_node.expr)
            if inferred_type not in self._resolver.resolve_type_data(var_data.type).descendants and inferred_type != var_data.type:
                self.log_error(f"Infered type {inferred_type} doens't conform with {var_data.type} when using destruct at line {destructor_node.id.line}")
            return var_data.type
        except:
            self.log_error(f"Trying to destruct a not unitialized variable at line {destructor_node.id.line}" )
            return 'object'

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            type = self._check_types(expr)
        return type
    
    def _check_call_arguments_static(self, call_node : CallNode, fn_data : FunctionData):
        fn_name = call_node.callee.id.lexeme
        if len(call_node.args) != len(fn_data.params):
            self.log_error(f"Function {fn_name} call at line {call_node.callee.id.line} doesn't match number of arguments, should be {len(fn_data.params)}")
        for i, arg in enumerate(call_node.args):
            inferred_type = self._check_types(arg)
            index = i
            param_var_data = fn_data.params[fn_data.params_index[index]]
            param_var_type = param_var_data.type
            assert(param_var_type != None)
            type_data = self._resolver.resolve_type_data(param_var_type)
            if inferred_type not in type_data.descendants and inferred_type != param_var_data.type:
                self.log_error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} at line {call_node.callee.id.line},  doesn't conform with {param_var_data.type}")
        return fn_data.type

    def _check_call_arguments_non_static(self, call_node : CallNode, fn_data : FunctionData, method_type_owner : str):
        fn_name = call_node.callee.id.lexeme
        if len(call_node.args) != len(fn_data.params) - 1:
            self.log_error(f"Function {fn_name} of type {method_type_owner} call at line {call_node.callee.id.line} doesn't match number of arguments, should be {len(fn_data.params)}")
        
        fn_name += ("_" + method_type_owner)

        for i, arg in enumerate(call_node.args):
            inferred_type = self._check_types(arg)
            index = i + 1 
            param_var_data = fn_data.params[fn_data.params_index[index]]
            param_var_type = param_var_data.type
            assert(param_var_type != None)
            type_data = self._resolver.resolve_type_data(param_var_type)
            if inferred_type not in type_data.descendants and inferred_type != param_var_data.type:
                self.log_error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} of type {method_type_owner} at line {call_node.callee.id.line},  doesn't conform with {param_var_data.type}")
        return fn_data.type

    def check_call_arguments(self, call_node : CallNode, fn_data : FunctionData, method_type_owner  : str):
        if method_type_owner == "":
            return self._check_call_arguments_static(call_node, fn_data)
        else:
            return self._check_call_arguments_non_static(call_node, fn_data, method_type_owner)

    def visit_call_node(self, call_node : CallNode):
        if isinstance(call_node.callee, LiteralNode):
            if call_node.callee.id.lexeme == "base" and self._in_type and self._in_method:
                type_data = self._resolver.resolve_type_data(self._type_name)
                func_name = self._method_name
                if type_data.ancestor == "object":
                    self.log_error(f"Call to base in {self._type_name} in {self._method_name} but there is no inheritance" )
                    return "object"
                methods = type_data.methods[func_name]
                if len(methods) <= 2:
                    self.log_error(f"There is no ancestor of {self._type_name} with method {self._method_name}")
                    return "object"
                method_name = methods[1]
                fn_name = method_name
                assert(fn_name in self._resolver.resolve_functions())
                fn_data = self._resolver.resolve_function_data(fn_name)
                self.check_call_arguments(call_node, fn_data, self._in_type)
                return fn_data.type
            
            else:
                fn_name = call_node.callee.id.lexeme
                if self._in_type and fn_name in self._resolver.resolve_type_data(self._type_name).methods:
                    type_data = self._resolver.resolve_type_data(self._type_name)
                    fn_data = self._resolver.resolve_function_data(fn_name)
                    self.check_call_arguments(call_node, fn_data, self._in_type)
                    return fn_data.type
                
                if fn_name not in self._resolver.resolve_functions():
                    if fn_name == "print":
                        return "object"
    
                    self.log_error(f"Call to {fn_name} at line {call_node.callee.id.line} but can't find this function")
                    return "object"
                
                fn_data = self._resolver.resolve_function_data(fn_name)
                self.check_call_arguments(call_node, fn_data, "")
                return fn_data.type

        else:
            assert(isinstance(call_node.callee, GetNode))
            fn_name = call_node.callee.id.lexeme
            left_inferred = self._check_types(call_node.callee.left)
            left_type_data = self._resolver.resolve_type_data(left_inferred)
            if fn_name not in left_type_data.methods:
                self.log_error(f"{fn_name} is not a method of inferred type {left_inferred} at line {call_node.callee.id.line}")
                return "object"
            
            fn_data = self._resolver.resolve_function_data(fn_name + "_" + left_inferred)
            self.check_call_arguments(call_node, fn_data, left_inferred)
            return fn_data.type

    def visit_get_node(self, get_node : GetNode):
        self._stack.append(get_node)
        if len(self._stack) > 2:
            self.log_error(f"After self should come at most one attribute, at line {get_node.id.line}")
        elif len(self._stack) == 2 and self._stack[-2].id != "self":
            self.log_error(f"After self should come at most one attribute, at line {get_node.id.line}")

        left_inferred_type = self._check_types(get_node.left)

        type_data = self._resolver.resolve_type_data(left_inferred_type)
        attr_name = get_node.id.lexeme

        if attr_name not in type_data.attributes:
            self.log_error(f"Type {self._in_type} do no has attribute {attr_name} at line {get_node.id.line}")
            self._stack.pop()
            return 'object'
        self._stack.pop()
        return type_data.attributes[attr_name].type
    
    def visit_set_node(self, set_node : SetNode):
        left_inferred_type = self._check_types(set_node.left)
        if not self._in_type or left_inferred_type != self._type_name:
            self.log_error(f"Attributes are private, at line {set_node.id.line}")
            return "object"

        type_data = self._resolver.resolve_type_data(self._type_name)
        attr_name = set_node.id.lexeme
        if attr_name not in type_data.attributes:
            self.log_error(f"Type {self._in_type} do no has attribute {attr_name} ")
            self._check_types(set_node.value)
            return 'object'

        attr_data = type_data.attributes[attr_name]
        value_type = self._check_types(set_node.value)

        type_data = self._resolver.resolve_type_data(attr_data.type)

        if value_type not in type_data.descendants and value_type != attr_data.type:
            self.log_error(f"Setting new value with type {value_type} for attribute {attr_name} doesn't conform,  at line {set_node.id.line}")
            return "object"
        return attr_data.type
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        infered_index = self._check_types(vector_get_node.index)
        if infered_index != "number":
            self.log_error(f'Cannot index a vector with a non-numerical type {infered_index}')
        
        inferred_type = self._check_types(vector_get_node.left)

        if not inferred_type.startswith('vector~'):
            self.log_error(f'Cannot index a non-vector type like {inferred_type}')
            return 'object'
        
        return inferred_type.split('~')[1]

    def visit_new_node(self, new_node : NewNode):
        type_name = new_node.id.lexeme
        if type_name not in self._resolver.resolve_types():
            self.log_error(f'Cannot instantiate a not declared type {type_name} at line {new_node.id.line}')
            return 'object'
        return type_name
    
    def visit_binary_node(self, binary_node : BinaryNode):
        left_inferred_type = self._check_types(binary_node.left)
        right_inferred_type = self._check_types(binary_node.right)
        line = binary_node.op.line
        op = binary_node.op.type
        if op == 'isOp' and isinstance(binary_node.right, LiteralNode):
            is_type = binary_node.right.id.lexeme

            if is_type not in self._resolver.resolve_types():
                self.log_error(f'Right operand of is : {is_type} must be an existing type at line {binary_node.op.line}')
            else:
                type_data = self._resolver.resolve_type_data(left_inferred_type)
                if is_type not in type_data.descendants:
                    self.log_error(f"Left operand type {left_inferred_type}  of is must be a descendant of right operand type {is_type} at line {line}")

            return 'bool'
        
        elif op == 'isOp':
            self.log_error(f"Right side of is should be a type at line {binary_node.op.line} ")

        if op == 'asOp' and isinstance(binary_node.right, LiteralNode):
            as_type = binary_node.right.id.lexeme

            if as_type not in self._resolver.resolve_types():
                self.log_error(f'Right operand of as not found {as_type} at line {binary_node.right.id.line}')
            else:
                type_data = self._resolver.resolve_type_data(as_type)
                if left_inferred_type not in type_data.descendants:
                    self.log_error(f'Left operand type {left_inferred_type} must be an ancestor of right operand type {as_type} at line {line}')

            return as_type

        elif op == "asOp":
            self.log_error(f"Right side of is should be a type at line {binary_node.op.line} ")


        match binary_node.op.type:
            case 'plus'| 'minus'| 'star'| 'div'| 'powerOp'| 'modOp'| 'greater'| 'less'| 'greaterEq'| 'lessEq':
                if left_inferred_type != 'number' or right_inferred_type != 'number':
                    self.log_error(f"Cannot apply binary operation to non-numerical types : {left_inferred_type} {right_inferred_type} at line {binary_node.op.line}")

                # this allows comparing any two types of objects.
                if op in ['greater', 'less', 'greaterEq', 'lessEq']:
                    return 'bool'
                
                return 'number'
            case 'and' | 'or':
                if left_inferred_type != 'bool' or right_inferred_type != 'bool':
                    self.log_error(f"Cannot apply binary operation to non-numerical types : {left_inferred_type} {right_inferred_type} at line {binary_node.op.line}")
                return 'bool'
            case 'doubleEqual' | 'notEqual':
                return 'bool'
    
    def visit_unary_node(self, unary_node : UnaryNode):
        inferred_type = self._check_types(unary_node.expr)
        if unary_node.op.type == 'not':
            if inferred_type != 'bool':
                self.log_error(f"Cannot negate a non-boolean expression like {inferred_type} at line {unary_node.op.line}")
            return 'bool'
        else:
            if inferred_type != 'number':
                self.log_error(f"Cannot negate a non-numerical expression like {inferred_type} at line {unary_node.op.line}")
            return 'number'
            
    def visit_literal_node(self, literal_node : LiteralNode):
        match literal_node.id.type:
            case 'number':
                return 'number'
            case 'string':
                return 'string'
            case 'true' | 'false':
                return 'bool'
            case 'null':
                return 'object'
            case 'id':
                try:
                    t =  self._resolver.resolve_var_data(literal_node.id.lexeme)
                    return t.type
                except:
                    self.log_error(f"Variable {literal_node.id.lexeme} at {literal_node.id.line} was not declared")
                    return "object"

    def _check_types(self, node : Statement) -> str:
        return node.accept(self)