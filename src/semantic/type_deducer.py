from code_gen.environment import FunctionData, VarData
from code_gen.resolver import Resolver
from common.ErrorLogger import Error
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

from termcolor import colored

class TypeDeducer(Visitor):
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[str] = []

        self._in_type = False
        self._in_method = False
        self._in_attribute = False
        self._type_determiner : list[list[None | str]] = [[]]
        self._method_name :  str | None = None
        self._type_name : str = None
        self._deduced = False

    def check_types(self, program : ProgramNode) -> list[str]:
        i = 1
        while True:
            print(f"Iteration {i} :")
            self._errors = []
            self._deduced = False
            self._check_types(program)
            if not self._deduced :
                break
            i += 1
        return self._errors

    def type_implements_protocol(self, protocol_name, type_name) -> bool:
        ans = True
        protocol_data = self._resolver.resolve_protocols()[protocol_name]
        type_data = self._resolver.resolve_type_data(type_name)

        if protocol_data.ancestor != None:
            ans = ans and self.type_implements_protocol(protocol_data.ancestor, type_name)

        for signature in protocol_data.methods:
            ans = ans and self.type_implements_signature(signature + "_" + protocol_name, type_name)

        return ans
    
    def type_implements_signature(self, signature_name, type_name) -> bool:
        type_data = self._resolver.resolve_type_data(type_name)
        if type_data.ancestor != None and self.type_implements_signature(signature_name, type_data.ancestor):
            return True

        for method in type_data.methods:
            if self.method_implements_signature(signature_name, type_data.methods[method][0]):
                return True
        
        return False
    
    def method_implements_signature(self, signature_name, method_name) -> bool:
        if signature_name.split("_")[0] != method_name.split("_")[0]:
            return False
        signature_data = self._resolver.resolve_function_data(signature_name)
        method_data = self._resolver.resolve_function_data(method_name)

        if len(method_data.params) - 1 != len(signature_data.params):
            return False
        
        if method_data.type == "Any":
            return False
        
        # return values should be as good as specified covariant.
        if self._resolver.resolve_lowest_common_ancestor(signature_data.type, method_data.type) != signature_data.type:
            return False
        
        for param in method_data.params:
            if param != "self":
                if param not in signature_data.params:
                    return False
                else:
                    param_data_method = method_data.params[param]
                    param_data_signature = signature_data.params[param]
                    if self._resolver.resolve_lowest_common_ancestor(param_data_method.type, param_data_signature) != param_data_method.type:
                        return False

        return True


    def log_error(self, error : str):
        self._errors.append(error)

    def push_type_determiner(self, ob : str):
        self._type_determiner[-1].append(ob)

    def match_type_determiner(self, op : str, custom_type):
        match op:
            case "+" | "-" | "*" | "/" | "%" | "^" | ">" | ">=" | "<=" | "<" :
                self._type_determiner[-1].append("Number")
            case "!" | "|" | "&&" :
                self._type_determiner[-1].append("Boolean")
            case _:
                self._type_determiner[-1].append(custom_type)

    def pop_type_determiner(self):
        self._type_determiner[-1].pop()

    def update_type(self, data : FunctionData | VarData):
        g = "---------------------------------------"
        print(g)
        print(f"Entering due to symbol {data.name}")
        if (len(self._type_determiner[-1]) > 0 and self._type_determiner[-1][-1] != "Any" and self._type_determiner[-1][-1] != "null"):
            if data.type == "Any":
                data.type = self._type_determiner[-1][-1]
                print(colored(f"Deduced type for symbol {data.name} from Any to {self._type_determiner[-1][-1]}", "blue"))
                self._deduced = True
                print(g)
            else:
                obtained_type = self._resolver.resolve_lowest_common_ancestor(data.type, self._type_determiner[-1][-1])
                # if there is some type there already then it should be good enough.
                if obtained_type != self._type_determiner[-1][-1]:
                    print(colored(f"Symbol {data.name} obtained type : {self._type_determiner[-1][-1]} does not conforms with its actual type :  {data.type}", "red" ))
                    print(g)
                    raise Exception(self._type_determiner[-1][-1], data.type)
                else:
                    print(colored(f"Symbol {data.name} obtained type : {self._type_determiner[-1][-1]} conforms with its actual type :  {data.type}", "green"))
                    print(g)
        else:
            print(f"There is nothing to do so continue")
            print(g)
        return data.type
    
    def inherits(self, type : str, data : VarData | FunctionData ) -> bool:
        if type in self._resolver.resolve_protocols() and data.type == "Object":
            return True
        return type in self._resolver.resolve_type_data(data.type).descendants or type == data.type
            
    def visit_program_node(self, program_node : ProgramNode): 
        for decl in program_node.decls:
            self._check_types(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        type_data = self._resolver.resolve_type_data(self._type_name)
        attr_data = type_data.attributes[attr_name]
        self._type_determiner.append([])
        self.push_type_determiner(attr_data.type)
        inferred_type = self._check_types(attribute_node.body)
        self._type_determiner.pop()
        if inferred_type == "null" and attribute_node.type == "Any":
            self.log_error(Error(f"Can't set to null attribute declaration without specifiying type " , attribute_node.id.line , attribute_node.id.offsetLine))

        elif inferred_type == "null":
            pass
        else:
            try:
                if attr_data.type == "Any":
                    self.push_type_determiner(inferred_type)
                    self.update_type(attr_data)
                    self.pop_type_determiner()
                else:
                    if attr_data.type in self._resolver.resolve_protocols():
                        if not self.type_implements_protocol(attr_data.type, inferred_type):
                            self.log_error(Error(f"Inferred type {inferred_type} for attribute {attr_name} does not implement protocol {attr_data.type} " , attribute_node.id.line , attribute_node.id.offsetLine))
                    elif not self.inherits(inferred_type, attr_data):
                        self.log_error(Error(f"Attribute {attr_name} type inferred {inferred_type} does not conform with actual type {attr_data.type} " , attribute_node.id.line , attribute_node.id.offsetLine))
            except Exception as e:
                self.log_error(Error(f"Attribute {attr_name} type given {e.args[1]} does not  conform with {e.args[0]} " , attribute_node.id.line , attribute_node.id.offsetLine))
                self.pop_type_determiner()

        return type_data.attributes[attr_name].type
        
    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        self._type_determiner.append([])
        self.push_type_determiner(func_data.type)
        inferred_type = self._check_types(method_node.body)
        self._type_determiner.pop()

        if method_node.type == "Any" and inferred_type == "null":
            self.log_error(Error(f"Return of method can't be null if method is not typed " , method_node.id.line , method_node.id.offsetLine))

        self._in_method = False    
        self._method_name = None

        try:
            if func_data.type == "Any":
                self.push_type_determiner(inferred_type)
                self.update_type(func_data)
                self.pop_type_determiner()
            else:
                if func_data.type in self._resolver.resolve_protocols():
                    if not self.type_implements_protocol(func_data.type, inferred_type):
                        self.log_error(Error(f"Inferred type {inferred_type} for method {func_name} does not implement protocol {func_data.type} " , method_node.id.line , method_node.id.offsetLine))
                elif not self.inherits(inferred_type, func_data):
                    self.log_error(Error(f"Function {func_name} type inferred {inferred_type} does not conform with actual type {func_data.type} " , method_node.id.line , method_node.id.offsetLine))
        except Exception as e:
            self.log_error(Error(f"Method {func_name} type given {e.args[1]} does not  conform with {e.args[0]} " , method_node.id.line , method_node.id.offsetLine))
            self.pop_type_determiner()

        return func_data.type
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        for method in type_node.methods:
            self._type_determiner.append([])
            self._check_types(method)
            self._type_determiner.pop()

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
            self._type_determiner.append([])
            self.push_type_determiner(var_data.type)
            inferred_type = self._check_types(assig.body)
            self._type_determiner.pop()
            if assig.type == "Any" and inferred_type == "null":
                self.log_error(Error(f"Can't set to null a non typed variable " , assig.id.line , assig.id.offsetLine))
                var_data.type = "Object"
            
            elif inferred_type == "null":
                continue

            try:
                if var_data.type == "Any":
                    self.push_type_determiner(inferred_type)
                    self.update_type(var_data)
                    self.pop_type_determiner()
                else:
                    if var_data.type in self._resolver.resolve_protocols():
                        if not self.type_implements_protocol(var_data.type, inferred_type):
                            self.log_error(Error(f"Inferred type {inferred_type} for variable {var_name} does not implement protocol {var_data.type} " , assig.id.line , assig.id.offsetLine))                    
                    elif not self.inherits(inferred_type, var_data):
                        self.log_error(Error(f"Variable {var_name} type inferred {inferred_type} does not conform with actual type {var_data.type} " , assig.id.line , assig.id.offsetLine))
            except Exception as e:
                self.log_error(Error(f"Variable {var_name} type given {e.args[1]} does not  conform with {e.args[0]} " , assig.id.line , assig.id.offsetLine))
                self.pop_type_determiner()

        f_type = self._check_types(let_node.body)
        self._resolver.next()
        return f_type

    def visit_while_node(self, while_node : WhileNode):
        self.push_type_determiner("Boolean")
        condition_type = self._check_types(while_node.condition)
        self.pop_type_determiner()
        if condition_type != 'Boolean':
            self.log_error(Error(f"While condition must evaluate to a boolean " , while_node.handle.line , while_node.handle.offsetLine))
        
        type_r = self._check_types(while_node.body)
        return type_r
    
    def visit_if_node(self, if_node : IfNode):
        initial_type = self._check_types(if_node.elsebody)
        for st in if_node.body:
            self.push_type_determiner("Boolean")
            cond_type = self._check_types(st[0])
            self.pop_type_determiner()
            if cond_type != 'Boolean':
                self.log_error(Error(f"Conditions of if / elif must evaluate to a boolean not to {cond_type} " , if_node.handle.line , if_node.handle.offsetLine))
            type = self._check_types(st[1])
            initial_type = self._resolver.resolve_lowest_common_ancestor(initial_type, type)
        return initial_type
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        print("No need -> explicit_vector_node")
        pass
    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        print("No need -> implicit_vector_node")
        pass

    def visit_destructor_node(self, destructor_node : DestructorNode):
        var_name = destructor_node.id.lexeme
        
        var_data = self._resolver.resolve_var_data(var_name)
        inferred_type = self._check_types(destructor_node.expr)
        if inferred_type == "null" and var_data.type != "Any":
            return var_data.type
        if inferred_type == "null" and var_data.type == "Any":
            self.log_error(Error(f"Can't set to null a non typed variable " , destructor_node.id.line , destructor_node.id.offsetLine))
            return "Object"
        try:
            if var_data.type == "Any":    
                self.push_type_determiner(inferred_type)
                self.update_type(var_data)
                self.pop_type_determiner()
            else:
                if var_data.type in self._resolver.resolve_protocols():
                    if not self.type_implements_protocol(var_data.type, inferred_type):
                        self.log_error(Error(f"Inferred type {inferred_type} for variable {var_name} does not implement protocol {var_data.type} " , destructor_node.id.line , destructor_node.id.offsetLine))                   
                elif not self.inherits(inferred_type, var_data):
                    self.log_error(Error(f"Variable {var_name} type inferred {inferred_type} does not conform with actual type {var_data.type} " , destructor_node.id.line , destructor_node.id.offsetLine))
        except:
            self.log_error(Error(f"Infered type {inferred_type} doens't conform with {var_data.type} when using destruct " , destructor_node.id.line , destructor_node.id.offsetLine))
            self.pop_type_determiner()

            
        return var_data.type


    def visit_block_node(self, block_node : BlockNode):
        for i in range(0, len(block_node.exprs)-1):
            self._type_determiner.append([])
            type = self._check_types(block_node.exprs[i])
            self._type_determiner.pop()
        
        type = self._check_types(block_node.exprs[-1])
        return type
    
    def _check_call_arguments_static(self, call_node : CallNode, fn_data : FunctionData):
        fn_name = call_node.callee.id.lexeme

        if len(call_node.args) != len(fn_data.params):
            self.log_error(Error(f"Function {fn_name} call doesn't match number of arguments, should be {len(fn_data.params)}, got {len(call_node.args)} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
            return fn_data.type

        for i, arg in enumerate(call_node.args):
            self._type_determiner.append([])
            inferred_type = self._check_types(arg)
            self._type_determiner.pop()
            index = i
            param_var_data = fn_data.params[fn_data.params_index[index]]
            try:
                if self._in_method and self._method_name == fn_name:
                    self.push_type_determiner(inferred_type)
                    self.update_type(param_var_data)
                    self.pop_type_determiner()
                else:
                    if param_var_data.type != "Any":
                        if param_var_data.type in self._resolver.resolve_protocols():
                            if not self.type_implements_protocol(param_var_data.type, inferred_type):
                                self.log_error(Error(f"Inferred type {inferred_type} for argument {i+1} does not implement protocol {param_var_data.type} in call to {fn_name} " , call_node.callee.id.line , call_node.callee.id.offsetLine))   
                        elif not self.inherits(inferred_type, param_var_data):
                            self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} doesn't conform with {param_var_data.type}" , call_node.callee.id.line , call_node.callee.id.offsetLine))
            except:
                self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} doesn't conform with {param_var_data.type} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
        return fn_data.type


    def _check_call_arguments_protocol(self, call_node : CallNode, fn_data : FunctionData, method_type_owner : str):
        fn_name = call_node.callee.id.lexeme
        fn_name += ("_" + method_type_owner)

        if len(call_node.args)  != len(fn_data.params):
            self.log_error(Error(f"Function {fn_name} of type {method_type_owner} call  doesnt match number of arguments should be {len(fn_data.params)}, got {len(call_node.args)} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
            return fn_data.type
        
        for i, arg in enumerate(call_node.args):
            self._type_determiner.append([])
            inferred_type = self._check_types(arg)
            self._type_determiner.pop()
            param_var_data = fn_data.params[fn_data.params_index[i]]
            try:
                if param_var_data.type != "Any":
                    if param_var_data.type in self._resolver.resolve_protocols():
                        if not self.type_implements_protocol(param_var_data.type, inferred_type):
                            self.log_error(Error(f"Inferred type {inferred_type} for argument {i+1} does not implement protocol {param_var_data.type} in call to {fn_name} " , call_node.callee.id.line , call_node.callee.id.offsetLine)) 
                    elif not self.inherits(inferred_type, param_var_data):
                            self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} of type {method_type_owner} ,  doesn't conform with {param_var_data.type} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
            except:
                self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} of type {method_type_owner} ,  doesn't conform with {param_var_data.type} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                
        return fn_data.type



    def _check_call_arguments_non_static(self, call_node : CallNode, fn_data : FunctionData, method_type_owner : str):
        fn_name = call_node.callee.id.lexeme        
        fn_name += ("_" + method_type_owner)

        if len(call_node.args) != len(fn_data.params) - 1:
            self.log_error(Error(f"Function {fn_name} of type {method_type_owner} call  doesn't match number of arguments, should be {len(fn_data.params) - 1}, got {len(call_node.args)} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
            return fn_data.type

        for i, arg in enumerate(call_node.args):
            self._type_determiner.append([])
            inferred_type = self._check_types(arg)
            self._type_determiner.pop()
            index = i + 1 
            param_var_data = fn_data.params[fn_data.params_index[index]]
            try:
                if self._in_method and self._method_name == fn_name:
                    self.push_type_determiner(inferred_type)
                    self.update_type(param_var_data)
                    self.pop_type_determiner()
                else:
                    if param_var_data.type != "Any":
                        if param_var_data.type in self._resolver.resolve_protocols():
                            if not self.type_implements_protocol(param_var_data.type, inferred_type):
                                self.log_error(Error(f"Inferred type {inferred_type} for argument {i+1} does not implement protocol {param_var_data.type} in call to {fn_name} " , call_node.callee.id.line , call_node.callee.id.offsetLine)) 
                        elif not self.inherits(inferred_type, param_var_data):
                            self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} of type {method_type_owner} ,  doesn't conform with {param_var_data.type} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
            except:
                self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to {fn_name} of type {method_type_owner} ,  doesn't conform with {param_var_data.type} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                

                    
        return fn_data.type

    def check_call_arguments(self, call_node : CallNode, fn_data : FunctionData, method_type_owner  : str):
        if method_type_owner == "":
            return self._check_call_arguments_static(call_node, fn_data)
        else:
            if method_type_owner in self._resolver.resolve_protocols():
                return self._check_call_arguments_protocol(call_node, fn_data, method_type_owner)
            return self._check_call_arguments_non_static(call_node, fn_data, method_type_owner)

    def check_call_base(self, call_node : CallNode):
        type_data = self._resolver.resolve_type_data(self._type_name)
        func_name = self._method_name
        if type_data.ancestor == "Object":
            self.log_error(Error(f"Call to base in {self._type_name} in {self._method_name} but there is no inheritance " , call_node.handle.line , call_node.handle.offsetLine))
            return "Object"
        methods = type_data.methods[func_name.split("_")[0]]
        if len(methods) < 2:
            self.log_error(Error(f"There is no ancestor of {self._type_name} with method {self._method_name} " , call_node.handle.line , call_node.handle.offsetLine))
            return "Object"
        method_name = methods[1]
        fn_name = method_name
        assert(fn_name in self._resolver.resolve_functions())
        fn_data = self._resolver.resolve_function_data(fn_name)
        if self._method_name == fn_name:
            try:
                self.update_type(fn_data)
            except:
                self.log_error(Error(f"Can't deduce correct type for function {fn_name} " , call_node.handle.line , call_node.handle.offsetLine))
            
        old_name = call_node.callee.id.lexeme
        call_node.callee.id.lexeme = fn_name.split("_")[0]
        self.check_call_arguments(call_node, fn_data, fn_name.split("_")[1])
        call_node.callee.id.lexeme = old_name
        return fn_data.type

    def visit_call_node(self, call_node : CallNode):
        if isinstance(call_node.callee, LiteralNode):
            if call_node.callee.id.lexeme == "base" and self._in_type and self._in_method:
                return self.check_call_base(call_node)
            else:
                fn_name = call_node.callee.id.lexeme
                if self._in_type and fn_name in self._resolver.resolve_type_data(self._type_name).methods and isinstance(call_node.callee, GetNode):
                    type_data = self._resolver.resolve_type_data(self._type_name)
                    fn_data = self._resolver.resolve_function_data(fn_name)
                    if self._method_name == fn_name:
                        try:
                            self.update_type(fn_data)
                        except:
                            self.log_error(Error(f"Can't deduce correct type for function {fn_name} " , call_node.handle.line , call_node.handle.offsetLine))
                    self.check_call_arguments(call_node, fn_data, self._in_type)
                    return fn_data.type
                
                if fn_name not in self._resolver.resolve_functions():
                    if fn_name == "print":
                        if len(call_node.args) != 1:
                            self.log_error(Error(f"Print only takes one argument " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                        for arg in call_node.args:
                            self._type_determiner.append([])
                            self._check_types(arg)
                            self._type_determiner.pop()
                        return "Object"
    
                    self.log_error(Error(f"Call to {fn_name}, but can't find this function " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                    return "Object"
                
                fn_data = self._resolver.resolve_function_data(fn_name)
                if self._method_name == fn_name:
                    try:
                        self.update_type(fn_data)
                    except:
                        self.log_error(Error(f"Can't deduce correct type for function {fn_name} " , call_node.handle.line , call_node.handle.offsetLine))
                self.check_call_arguments(call_node, fn_data, "")
                return fn_data.type
        else:
            assert(isinstance(call_node.callee, GetNode))
            fn_name = call_node.callee.id.lexeme
            self._type_determiner.append([])
            left_inferred = self._check_types(call_node.callee.left)
            self._type_determiner.pop()

            if left_inferred in self._resolver.resolve_protocols():
                # do another analysis
                fn_data = self._resolver.resolve_protocol_function_data(fn_name, left_inferred)
                if fn_data == None:
                    self.log_error(Error(f"{fn_name} is not a method of inferred protocol type {left_inferred} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                    return "Object"
                else:   
                    self.check_call_arguments(call_node, fn_data, left_inferred)
                    return fn_data.type
            else:
                left_type_data = self._resolver.resolve_type_data(left_inferred)
                if fn_name not in left_type_data.methods:
                    self.log_error(Error(f"{fn_name} is not a method of inferred type {left_inferred} " , call_node.callee.id.line , call_node.callee.id.offsetLine))
                    return "Object"
                
                owner_type = left_type_data.methods[fn_name][0].split("_")[1]
                fn_data = self._resolver.resolve_function_data(fn_name + "_" + owner_type)
                if self._method_name == fn_name + "_" + owner_type:
                    try:
                        self.update_type(fn_data)
                    except:
                        self.log_error(Error(f"Can't deduce correct type for function {fn_name} " , call_node.handle.line , call_node.handle.offsetLine))
                self.check_call_arguments(call_node, fn_data, owner_type)
                return fn_data.type

    def visit_get_node(self, get_node : GetNode):
        self._type_determiner.append([])
        left_inferred_type = self._check_types(get_node.left)
        self._type_determiner.pop()
        
        type_data = self._resolver.resolve_type_data(left_inferred_type)
        attr_name = get_node.id.lexeme

        if attr_name not in type_data.attributes:
            self.log_error(Error(f"Type {left_inferred_type} do no has attribute {attr_name} " , get_node.id.line , get_node.id.offsetLine))
            return "Object"
        try:
            self.update_type(type_data.attributes[attr_name])
        except Exception as e:
            self.log_error(Error(f"Can't deduce correct type for attribute {attr_name} obtained {e.args[0]}, should {e.args[1]} " , get_node.id.line , get_node.id.offsetLine))
        return type_data.attributes[attr_name].type
    
    def visit_set_node(self, set_node : SetNode):
        self._type_determiner.append([])
        left_inferred_type = self._check_types(set_node.left)
        self._type_determiner.pop()
        if not self._in_type or left_inferred_type != self._type_name:
            self.log_error(Error(f"Attributes are private, " , set_node.id.line , set_node.id.offsetLine))
            self._check_types(set_node.value)
            return "Object"

        type_data = self._resolver.resolve_type_data(self._type_name)
        attr_name = set_node.id.lexeme
        if attr_name not in type_data.attributes:
            self.log_error(Error(f"Type {self._type_name} do no has attribute {attr_name} " , set_node.id.line , set_node.id.offsetLine))
            self._check_types(set_node.value)
            return 'Object'

        attr_data = type_data.attributes[attr_name]
        value_type = self._check_types(set_node.value)

        type_data = self._resolver.resolve_type_data(attr_data.type)

        try:
            self.push_type_determiner(value_type)
            self.update_type(attr_data)
            self.pop_type_determiner()
        except:
            self.log_error(Error(f"Updating value with type {value_type} for attribute {attr_name} doesn't conform with its type {attr_data.type},  " , set_node.id.line , set_node.id.offsetLine))
            self.pop_type_determiner()
            return "Object"
        return attr_data.type
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        self.push_type_determiner("Number")
        infered_index = self._check_types(vector_get_node.index)
        self.pop_type_determiner()
        if infered_index != "Number":
            self.log_error(f'Cannot index a vector with a non-numerical type {infered_index}')
        
        self.push_type_determiner("Vector")
        inferred_type = self._check_types(vector_get_node.left)
        self.pop_type_determiner()

        if inferred_type != ('Vector'):
            self.log_error(f'Cannot index a non-vector type like {inferred_type}')
            return 'Object'
        
        return "Object"

    def visit_new_node(self, new_node : NewNode):
        type_name = new_node.id.lexeme
        
        type_data = self._resolver.resolve_type_data(type_name)
        constructor = type_data.methods["build"][0]
        fn_data = self._resolver.resolve_function_data(constructor)

        if len(new_node.args) != len(fn_data.params) - 1:
            self.log_error(Error(f"Trying to instantiate a new type with wrong number of arguments " , new_node.id.line , new_node.id.offsetLine))
            return type_name
        
        for i, arg in enumerate(new_node.args):
            self._type_determiner.append([])
            inferred_type = self._check_types(arg)
            self._type_determiner.pop() 
            param_var_data = fn_data.params[fn_data.params_index[i+1]]
            try:
                self.push_type_determiner(inferred_type)
                self.update_type(param_var_data)
                self.pop_type_determiner()
            except:
                self.log_error(Error(f"Argument {i+1} inferred type {inferred_type} , in call to constructor of type {type_name} ,  doesn't conform with {param_var_data.type} " , new_node.id.line , new_node.id.offsetLine))
                self.pop_type_determiner()
        return type_name
    
    def visit_is(self, binary_node : BinaryNode):
        is_type = binary_node.right.id.lexeme
        if is_type not in self._resolver.resolve_types():
            self.log_error(Error(f"Right operand of is : {is_type} must be an existing type " , binary_node.op.line , binary_node.op.offsetLine))
        else:
            self._type_determiner.append([])
            left_inferred_type = self._check_types(binary_node.left)
            self._type_determiner.pop()
        return 'Boolean'

    def visit_as(self, binary_node : BinaryNode):
        as_type = binary_node.right.id.lexeme
        if as_type not in self._resolver.resolve_types():
            self.log_error(Error(f"Right operand of as not found {as_type} " , binary_node.right.id.line , binary_node.right.id.offsetLine))
        else:
            self._type_determiner.append([])
            left_inferred_type = self._check_types(binary_node.left)
            self._type_determiner.pop()
        return as_type

    def visit_at(self, binary_node :  BinaryNode):
        self._type_determiner.append([])
        left_infered_type = self._check_types(binary_node.left)
        self._type_determiner.pop()
        self._type_determiner.append([])
        right_inferred_type = self._check_types(binary_node.right)
        self._type_determiner.pop()
        if left_infered_type not in ["String", "Number"]:
            self.log_error(Error(f"Can only use @ operator with String and Number , left = {left_infered_type}, right = {right_inferred_type} " , binary_node.op.line , binary_node.op.offsetLine))
        if right_inferred_type not in ["String", "Number"]:
            self.log_error(Error(f"Can only use @ operator with String and Number , left = {left_infered_type}, right = {right_inferred_type} " , binary_node.op.line , binary_node.op.offsetLine))
        return "String"

    def visit_binary_node(self, binary_node : BinaryNode):
        line = binary_node.op.line
        op = binary_node.op.lexeme
        if op == "is" or op == "as":
            if not isinstance(binary_node.right, LiteralNode):
                self.log_error(Error(f"Right side of operators is, as should be types " , binary_node.op.line , binary_node.op.offsetLine))
                return "Object"
            else:
                match op:
                    case "is":
                        return self.visit_is(binary_node)
                    case "as":
                        return self.visit_as(binary_node)
        if op == "@" or op == "@@":
            return self.visit_at(binary_node)

        if op != "==" and op != "!=":
            self.match_type_determiner(binary_node.op.lexeme, "")
            left_inferred_type = self._check_types(binary_node.left)
            self.pop_type_determiner()
            self.match_type_determiner(binary_node.op.lexeme, "")
            right_inferred_type = self._check_types(binary_node.right)
            self.pop_type_determiner()
        else:
            self._type_determiner.append([])
            left_inferred_type = self._check_types(binary_node.left)
            self._type_determiner.pop()
            self._type_determiner.append([])
            right_inferred_type = self._check_types(binary_node.right)
            self._type_determiner.pop()
        
        match binary_node.op.type:
            case 'plus'| 'minus'| 'star'| 'div'| 'powerOp'| 'modOp'| 'greater'| 'less'| 'greaterEq'| 'lessEq':
                if left_inferred_type != 'Number' or right_inferred_type != 'Number':
                    self.log_error(Error(f"Cannot apply binary arithmetic operation to non-numerical types : left type is {left_inferred_type}, right type is  {right_inferred_type} " , binary_node.op.line , binary_node.op.offsetLine))

                # this allows comparing any two types of objects.
                if binary_node.op.type in ['greater', 'less', 'greaterEq', 'lessEq']:
                    return 'Boolean'
                
                return 'Number'
            case 'and' | 'or':
                if left_inferred_type != 'Boolean' or right_inferred_type != 'Boolean':
                    self.log_error(Error(f"Cannot apply binary boolean operation to non-numerical types : left type is {left_inferred_type},  right type is {right_inferred_type} " , binary_node.op.line , binary_node.op.offsetLine))
                return 'Boolean'
            case 'doubleEqual' | 'notEqual':
                return 'Boolean'
            case 'doubleAt' | 'at':
                return self._resolver.resolve_lowest_common_ancestor(left_inferred_type, right_inferred_type)    

    def visit_unary_node(self, unary_node : UnaryNode):
        self.match_type_determiner(unary_node.op.lexeme, "")
        inferred_type = self._check_types(unary_node.expr)
        self.pop_type_determiner()
        if unary_node.op.type == 'not':
            if inferred_type != 'Boolean':
                self.log_error(Error(f"Cannot negate a non-boolean expression like {inferred_type} " , unary_node.op.line , unary_node.op.offsetLine))
            return 'Boolean'
        else:
            if inferred_type != 'Number':
                self.log_error(Error(f"Cannot negate a non-numerical expression like {inferred_type} " , unary_node.op.line , unary_node.op.offsetLine))
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
                    t = self._resolver.resolve_var_data(literal_node.id.lexeme)
                    try:
                        self.update_type(t)
                        return t.type
                    except Exception as e:
                        self.log_error(Error(f"Variable {literal_node.id.lexeme} type {e.args[0]} does not conform with obtained type {e.args[1]} " , literal_node.id.line , literal_node.id.offsetLine))
                        return t.type
                except:
                    self.log_error(Error(f"Variable {literal_node.id.lexeme} is not declared " , literal_node.id.line , literal_node.id.offsetLine))
                    return "Object"

    def _check_types(self, node : Statement) -> str:
        return node.accept(self)