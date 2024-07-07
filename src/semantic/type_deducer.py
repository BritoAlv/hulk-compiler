from code_gen.environment import FunctionData, VarData
from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class TypeDeducer(Visitor):
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[str] = []

        self._in_type = False
        self._in_method = False
        self._in_attribute = False
        self._type_determiner = []
        self._method_name :  str | None = None
        self._type_name : str = None
        self._stack : list[GetNode | CallNode] = []

    def check_types(self, program : ProgramNode) -> list[str]:
        self._check_types(program)
        return self._errors

    def log_error(self, error : str):
        self._errors.append(error)

    def push_type_determiner(self, op : str, custom_type = ""):
        match op:
            case "+" | "-" | "*" | "/" | "%" | "^" | ">" | ">=" | "<=" | "<" :
                self._type_determiner.append("Number")
            case "!" | "and" | "or" :
                self._type_determiner.append("Boolean")
            case _:
                self._type_determiner.append(custom_type)

    def pop_type_determiner(self):
        self._type_determiner.pop()

    def update_type(self, data):
        if (data.type == "Any" or data.type == None) and len(self._type_determiner) > 0:
            data.type = self._type_determiner[-1]
        if (data.type != "Any" and data.type == None) and len(self._type_determiner) > 0:
            data.type = self._resolver.resolve_lowest_common_ancestor(data.type, self._type_determiner[-1])
        return data.type

    def visit_program_node(self, program_node : ProgramNode): 
        for decl in program_node.decls:
            self._check_types(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        default_type = "Any" if attribute_node.type == None else attribute_node.type.lexeme
        if not self._in_type:
            self.log_error(f'Attribute {attribute_node.id.lexeme} declaration must be inside a type declaration at line {attribute_node.id.line}')
            self._check_types(attribute_node.body)
            return default_type
        
        self._in_attribute = True

        type_data = self._resolver.resolve_type_data(self._type_name)
        self._in_attribute = True
        if attr_name not in type_data.attributes:
            self.log_error(f"Attribute {attr_name} not in {self._type_name} attributes at line {attribute_node.id.line}")
            return default_type
        
        var_data = type_data.attributes[attr_name]
        self._in_attribute = True
        var_data.type = default_type
        inferred_type = self._check_types(attribute_node.body)
        self._in_attribute = False

        if attribute_node.type != None:
            var_data.type = attribute_node.type.lexeme
            type_data = self._resolver.resolve_type_data(var_data.type)
            if inferred_type == "null":
                return var_data.type  
            if inferred_type not in type_data.descendants and inferred_type != var_data.type:
                self.log_error(f'Given type for attribute {attr_name} in {self._type_name} does not conform with its initialization body at line {attribute_node.id.line}')
        else:
            if inferred_type == "null":
                self.log_error(f"Can't set to null attribute declaration without specifiying type at line {attribute_node.id.line}")
                var_data.type = "Object"
            else:
                var_data.type = inferred_type
        
        return var_data.type

    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        default_type = "Any" if method_node.type == None else method_node.type.lexeme
        func_data.type = default_type

        inferred_type = self._check_types(method_node.body)

        if method_node.type != None:
            type_data = self._resolver.resolve_type_data(method_node.type.lexeme)
            if inferred_type not in type_data.descendants and inferred_type != default_type:
                self.log_error(f'Given type for method {func_name} in {self._type_name} does not conform with its return body at line {method_node.id.line}')
        else:
            if inferred_type == "Any":
                self.log_error(f"Can't deduce type for function / method {method_node.id.lexeme} at line {method_node.id.line}")
                func_data.type = "Object"
            else:
                func_data.type = inferred_type
            return func_data.type
            
        self._in_method = False    
        self._method_name = None

        return func_data.type
    
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
            default_type = "Any" if assig.type == None else assig.type.lexeme
            var_data = self._resolver.resolve_var_data(var_name)
            var_data.type = default_type
            inferred_type = self._check_types(assig.body)
            if assig.type != None:
                op_type_data = self._resolver.resolve_type_data(assig.type.lexeme)
                if inferred_type == "null":
                    continue
                if inferred_type not in op_type_data.descendants and inferred_type != assig.type.lexeme:
                    self.log_error(f"Type {inferred_type} does not conform with {assig.type.lexeme} in Let Expression near line {assig.id.line}")
            else:
                if inferred_type == "null":
                    self.log_error(f"Can't set to null a non typed variable at line {assig.id.line}")
                    var_data.type = "Object"
                else:
                    var_data.type = inferred_type 
        f_type = self._check_types(let_node.body)
        self._resolver.next()
        return f_type

    def visit_while_node(self, while_node : WhileNode):
        self.push_type_determiner("Boolean")
        condition_type = self._check_types(while_node.condition)
        self.pop_type_determiner()
        if condition_type != 'Boolean':
            self.log_error(f'While condition must evaluate to a boolean at line {while_node.handle.line}')
        return self._check_types(while_node.body)
    
    def visit_if_node(self, if_node : IfNode):
        initial_type = self._check_types(if_node.elsebody)
        for st in if_node.body:
            self.push_type_determiner("Boolean")
            cond_type = self._check_types(st[0])
            self.pop_type_determiner()
            if cond_type != 'Boolean':
                self.log_error(f"Conditions of if / elif must evaluate to a boolean not to {cond_type} at line {if_node.handle.line}")
            type = self._check_types(st[1])
            if type != "Any":
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
            if inferred_type == "null" and var_data.type != None:
                return var_data.type
            if inferred_type == "null" and var_data.type == None:
                self.log_error(f"Can't set to null a non typed variable at line {destructor_node.id.line}")
                return "Object"
            if inferred_type not in self._resolver.resolve_type_data(var_data.type).descendants and inferred_type != var_data.type:
                self.log_error(f"Infered type {inferred_type} doens't conform with {var_data.type} when using destruct at line {destructor_node.id.line}")
            return var_data.type
        except:
            self.log_error(f"Trying to destruct a not unitialized variable at line {destructor_node.id.line}" )
            return 'Object'

    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            type = self._check_types(expr)
        return type
    
    def _check_call_arguments_static(self, call_node : CallNode, fn_data : FunctionData):
        fn_name = call_node.callee.id.lexeme
        if len(call_node.args) != len(fn_data.params):
            self.log_error(f"Function {fn_name} call at line {call_node.callee.id.line} doesn't match number of arguments, should be {len(fn_data.params)}, got {len(call_node.args)}")
            return fn_data.type

        for i, arg in enumerate(call_node.args):
            inferred_type = self._check_types(arg)
            index = i
            param_var_data = fn_data.params[fn_data.params_index[index]]
            param_var_type = param_var_data.type
            if param_var_type == None:
                fn_data.params[fn_data.params_index[index]].type = inferred_type
            else:
                type_data = self._resolver.resolve_type_data(param_var_type)
                if inferred_type not in type_data.descendants and inferred_type != param_var_data.type:
                    self.log_error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} at line {call_node.callee.id.line},  doesn't conform with {param_var_data.type}")
        return fn_data.type

    def _check_call_arguments_non_static(self, call_node : CallNode, fn_data : FunctionData, method_type_owner : str):
        fn_name = call_node.callee.id.lexeme
        if len(call_node.args) != len(fn_data.params) - 1:
            self.log_error(f"Function {fn_name} of type {method_type_owner} call at line {call_node.callee.id.line} doesn't match number of arguments, should be {len(fn_data.params) - 1}, got {len(call_node.args)}")
            return fn_data.type
        
        fn_name += ("_" + method_type_owner)

        for i, arg in enumerate(call_node.args):
            inferred_type = self._check_types(arg)
            index = i + 1 
            param_var_data = fn_data.params[fn_data.params_index[index]]
            param_var_type = param_var_data.type
            if param_var_type == None:
                param_var_data.type = inferred_type
            else:
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
        self._stack.append(call_node)
        if isinstance(call_node.callee, LiteralNode):
            if call_node.callee.id.lexeme == "base" and self._in_type and self._in_method:
                type_data = self._resolver.resolve_type_data(self._type_name)
                func_name = self._method_name
                if type_data.ancestor == "Object":
                    self.log_error(f"Call to base in {self._type_name} in {self._method_name} but there is no inheritance")
                    self._stack.pop()
                    return "Object"
                methods = type_data.methods[func_name.split("_")[0]]
                if len(methods) < 2:
                    self.log_error(f"There is no ancestor of {self._type_name} with method {self._method_name} at line {call_node.handle.line}")
                    self._stack.pop()
                    return "Object"
                method_name = methods[1]
                fn_name = method_name
                assert(fn_name in self._resolver.resolve_functions())
                fn_data = self._resolver.resolve_function_data(fn_name)
                if self._method_name == fn_name:
                    self.update_type(fn_data)
                old_name = call_node.callee.id.lexeme
                call_node.callee.id.lexeme = fn_name.split("_")[0]
                self.check_call_arguments(call_node, fn_data, fn_name.split("_")[1])
                call_node.callee.id.lexeme = old_name
                self._stack.pop()
                return fn_data.type
            else:
                fn_name = call_node.callee.id.lexeme
                if self._in_type and fn_name in self._resolver.resolve_type_data(self._type_name).methods and isinstance(call_node.callee, GetNode):
                    type_data = self._resolver.resolve_type_data(self._type_name)
                    fn_data = self._resolver.resolve_function_data(fn_name)
                    if self._method_name == fn_name:
                        self.update_type(fn_data)
                    self.check_call_arguments(call_node, fn_data, self._in_type)
                    self._stack.pop()
                    return fn_data.type
                
                if fn_name not in self._resolver.resolve_functions():
                    if fn_name == "print":
                        if len(call_node.args) != 1:
                            self.log_error(f"Print only takes one argument at line {call_node.callee.id.line}")
                        for arg in call_node.args:
                            self._check_types(arg)
                        self._stack.pop()
                        return "Object"
    
                    self.log_error(f"Call to {fn_name} at line {call_node.callee.id.line} but can't find this function")
                    self._stack.pop()
                    return "Object"
                
                fn_data = self._resolver.resolve_function_data(fn_name)
                if self._method_name == fn_name:
                    self.update_type(fn_data)
                self.check_call_arguments(call_node, fn_data, "")
                self._stack.pop()
                return fn_data.type
        else:
            assert(isinstance(call_node.callee, GetNode))
            fn_name = call_node.callee.id.lexeme
            left_inferred = self._check_types(call_node.callee.left)
            left_type_data = self._resolver.resolve_type_data(left_inferred)
            if fn_name not in left_type_data.methods:
                self.log_error(f"{fn_name} is not a method of inferred type {left_inferred} at line {call_node.callee.id.line}")
                self._stack.pop()
                return "Object"
            
            owner_type = left_type_data.methods[fn_name][0].split("_")[1]
            fn_data = self._resolver.resolve_function_data(fn_name + "_" + owner_type)
            if self._method_name == fn_name:
                self.update_type(fn_data)
            self.check_call_arguments(call_node, fn_data, owner_type)
            self._stack.pop()
            return fn_data.type

    def visit_get_node(self, get_node : GetNode):

        if isinstance(get_node.left, LiteralNode) and get_node.left.id.lexeme == "self" and self._in_attribute and self._resolver.resolve_var_data("self").type == self._type_name:
            self.log_error(f"Cannot access to self in attribute declaration at line {get_node.left.id.line}")
            return "Object"

        self._stack.append(get_node)
        if len(self._stack) > 2:
            self.log_error(f"After self should come at most one attribute, at line {get_node.id.line}")
        elif len(self._stack) == 2:
            if isinstance(self._stack[-2], GetNode):
                if self._stack[-2].id != "self":
                    self.log_error(f"After self should come at most one attribute, at line {get_node.id.line}")
            if isinstance(self._stack[-2], CallNode) and not self._in_type:
                self.log_error(f"Attributes are private at line {self._stack[-2].handle.line}")
            

        left_inferred_type = self._check_types(get_node.left)

        type_data = self._resolver.resolve_type_data(left_inferred_type)
        attr_name = get_node.id.lexeme

        if attr_name not in type_data.attributes:
            self.log_error(f"Type {self._type_name} do no has attribute {attr_name} at line {get_node.id.line}")
            self._stack.pop()
            return "Object"
        self._stack.pop()
        return self.update_type(type_data.attributes[attr_name])
    
    def visit_set_node(self, set_node : SetNode):
        if isinstance(set_node.left, LiteralNode) and set_node.left.id.lexeme == "self" and self._in_attribute and self._resolver.resolve_var_data("self").type == self._type_name:
            self.log_error(f"Cannot access to self in attribute declaration at line {set_node.left.id.line}")
            return "Object" 

        left_inferred_type = self._check_types(set_node.left)
        if not self._in_type or left_inferred_type != self._type_name:
            self.log_error(f"Attributes are private, at line {set_node.id.line}")
            return "Object"

        type_data = self._resolver.resolve_type_data(self._type_name)
        attr_name = set_node.id.lexeme
        if attr_name not in type_data.attributes:
            self.log_error(f"Type {self._in_type} do no has attribute {attr_name} ")
            self._check_types(set_node.value)
            return 'Object'

        attr_data = type_data.attributes[attr_name]
        value_type = self._check_types(set_node.value)

        type_data = self._resolver.resolve_type_data(attr_data.type)

        if value_type not in type_data.descendants and value_type != attr_data.type:
            self.log_error(f"Setting new value with type {value_type} for attribute {attr_name} doesn't conform,  at line {set_node.id.line}")
            return "Object"
        return attr_data.type
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        infered_index = self._check_types(vector_get_node.index)
        if infered_index != "Number":
            self.log_error(f'Cannot index a vector with a non-numerical type {infered_index}')
        
        inferred_type = self._check_types(vector_get_node.left)

        if not inferred_type.startswith('Vector'):
            self.log_error(f'Cannot index a non-vector type like {inferred_type}')
            return 'Object'
        
        return "Object"

    def visit_new_node(self, new_node : NewNode):
        type_name = new_node.id.lexeme
        if type_name not in self._resolver.resolve_types():
            self.log_error(f'Cannot instantiate a not declared type {type_name} at line {new_node.id.line}')
            return 'Object'
        return type_name
    
    def visit_is(self, binary_node : BinaryNode):
        is_type = binary_node.right.id.lexeme
        if is_type not in self._resolver.resolve_types():
            self.log_error(f'Right operand of is : {is_type} must be an existing type at line {binary_node.op.line}')
        else:
            self.push_type_determiner("", binary_node.right.id.lexeme)
            left_inferred_type = self._check_types(binary_node.left)
            self.pop_type_determiner()
            type_data = self._resolver.resolve_type_data(left_inferred_type)
            if is_type not in type_data.descendants:
                self.log_error(f"Left operand type {left_inferred_type}  of is must be a descendant of right operand type {is_type} at line {binary_node.op.line}")
        return 'Boolean'

    def visit_as(self, binary_node : BinaryNode):
        as_type = binary_node.right.id.lexeme
        if as_type not in self._resolver.resolve_types():
            self.log_error(f'Right operand of as not found {as_type} at line {binary_node.right.id.line}')
        else:
            self.push_type_determiner(as_type)
            left_inferred_type = self._check_types(binary_node.left)
            type_data = self._resolver.resolve_type_data(left_inferred_type)
            self.pop_type_determiner()
            if as_type not in type_data.descendants:
                self.log_error(f'Left operand type {left_inferred_type} must be an ancestor of right operand type {as_type} at line {binary_node.op.line}')

        return as_type

    def visit_at(self, binary_node :  BinaryNode):

        left_infered_type = self._check_types(binary_node.left)
        right_inferred_type = self._check_types(binary_node.right)
        if left_infered_type not in ["String", "Number"]:
            self.log_error(f"Can only use @ operator with String and Number at line {binary_node.op.line}")
        if right_inferred_type not in ["String", "Number"]:
            self.log_error(f"Can only use @ operator with String and Number at line {binary_node.op.line}")
        return "String"

    def visit_binary_node(self, binary_node : BinaryNode):
        line = binary_node.op.line
        op = binary_node.op.lexeme
        if op == "is" or op == "as":
            if not isinstance(binary_node.right, LiteralNode):
                self.log_error(f"Right side of operators is, as should be types at line {line}")
                return "Object"
            else:
                match op:
                    case "is":
                        return self.visit_is(binary_node)
                    case "as":
                        return self.visit_as(binary_node)
        if op == "@" or op == "@@":
            return self.visit_at(binary_node)
        self.push_type_determiner(binary_node.op.lexeme)
        left_inferred_type = self._check_types(binary_node.left)
        self.pop_type_determiner()
        self.push_type_determiner(binary_node.op.lexeme)
        right_inferred_type = self._check_types(binary_node.right)
        self.pop_type_determiner()
        
        match binary_node.op.type:
            case 'plus'| 'minus'| 'star'| 'div'| 'powerOp'| 'modOp'| 'greater'| 'less'| 'greaterEq'| 'lessEq':
                if left_inferred_type != 'Number' or right_inferred_type != 'Number':
                    self.log_error(f"Cannot apply binary operation to non-numerical types : {left_inferred_type} {right_inferred_type} at line {binary_node.op.line}")

                # this allows comparing any two types of objects.
                if binary_node.op.type in ['greater', 'less', 'greaterEq', 'lessEq']:
                    return 'Boolean'
                
                return 'Number'
            case 'and' | 'or':
                if left_inferred_type != 'Boolean' or right_inferred_type != 'Boolean':
                    self.log_error(f"Cannot apply binary operation to non-numerical types : {left_inferred_type} {right_inferred_type} at line {binary_node.op.line}")
                return 'Boolean'
            case 'doubleEqual' | 'notEqual':
                return 'Boolean'
            case 'doubleAt' | 'at':
                return self._resolver.resolve_lowest_common_ancestor(left_inferred_type, right_inferred_type)    

    def visit_unary_node(self, unary_node : UnaryNode):
        self.push_type_determiner(unary_node.op.lexeme)
        inferred_type = self._check_types(unary_node.expr)
        self.pop_type_determiner()
        if unary_node.op.type == 'not':
            if inferred_type != 'Boolean':
                self.log_error(f"Cannot negate a non-boolean expression like {inferred_type} at line {unary_node.op.line}")
            return 'Boolean'
        else:
            if inferred_type != 'Number':
                self.log_error(f"Cannot negate a non-numerical expression like {inferred_type} at line {unary_node.op.line}")
            return 'Number'
            
    def visit_literal_node(self, literal_node : LiteralNode):
        match literal_node.id.type:
            case 'number':
                return 'Number'
            case 'string':
                return 'String'
            case 'true' | 'false':
                return 'Boolean'
            case 'null':
                return "null"
            case 'id':
                try:
                    t =  self._resolver.resolve_var_data(literal_node.id.lexeme)
                    return self.update_type(t)

                except:
                    self.log_error(f"Variable {literal_node.id.lexeme} at line {literal_node.id.line} was not declared")
                    return "Object"

    def _check_types(self, node : Statement) -> str:
        return node.accept(self)