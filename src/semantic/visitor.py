from common.ErrorLogger import Error
from common.ast_nodes.expressions import *
from common.ast_nodes.statements import *
from common.visitor import Visitor



class ComputedValue:
    def __init__(self, type, value = None) -> None:
        self.type = type
        self.value = value 

class Vector:
    def __init__(self, values) -> None:
        self.values = values
    def __str__(self) -> str:
        return "Vector"
    
class Type:
    def __init__(self, name, args, methods = [], attribute = []) -> None:
        self.name = name
        self.attribute = attribute
        self.method = methods
        self.args = args

    def add_args(self, args):
        for (i, j) in args:
            self.args.append(Attribute(i, j))

    def get_attribute(self, name):
        for i in self.attribute:
            if i.name == name:
                return i
        return None
    
    def get_method(self, name, args):
        for i in self.method:
            if i.name == name :
                return i
        return None  
    
    def get_method_whithout_params(self, name):
        for i in self.method:
            if i.name == name:
                return i
        return None     

    def define_attribute(self, name, type):
        if self.get_attribute(name) != None:
            return False
        self.attribute.append(Attribute(name, type))

    def define_method(self, name, return_type, args):
        if self.get_method(name, args) != None:
            return False
        args_type = []
        for (i, j) in args:
            args_type.append(Attribute(i.lexeme, j.lexeme if j != None else None))
        self.method.append(Method(name, return_type, args_type))

class Attribute:
    def __init__(self, name, itype) -> None:
        self.name = name
        self.type = itype

class Method:
    def __init__(self, name, return_type, args) -> None:
        self.name = name
        self.type = return_type
        self.args = args

class ContextValue:
    def __init__(self, type, value = None) -> None:
        self.value = value
        self.type = type

class ContextLower():
    def __init__(self, parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.method = []

    def is_defined(self, var) -> bool:  # da o False si no existe o el valor del dict
        if self.dict.get(var)!= None:
            return True
        
        return (self.parent != None and self.parent.is_defined(var))
   
    def is_defined_local(self, var) -> bool:  # da o False si no existe o el valor del dict
        return self.dict.get(var) != None
    
    def is_defined_func(self, name, args) -> bool:
        for i in self.method:
            if i.name == name:
                return i
        return self.parent.is_defined_func(name, args) if self.parent != None else None
    
    def is_defined_func_whithout_params(self, name) -> bool:
        for i in self.method:
            if i.name == name:
                return True
        return (self.parent != None and self.parent.is_defined_func_whithout_params(name))
    
    def get(self, name):
        get = self.dict.get(name)
        if get != None:
            return get
        if self.parent != None:
            return self.parent.get(name)
        return None

    def define(self, var, type, value = None) -> bool:
        if self.dict.get(var) != None:
            return False
        self.dict[var] = ContextValue(type, value)
        return True
    
    def remove_define(self, var) -> bool:
        if self.is_defined(var):
            self.dict.pop(var)
    
    def define_func(self, name, return_type, args) -> bool:
        if self.is_defined_func(name, args) != None:
            return False
        args_type = []
        for (i, j) in args:
            args_type.append(Attribute(i.lexeme, j.lexeme if j != None else None))
        self.method.append(Method(name, return_type, args_type))

    def create_child_context(self):
        return ContextLower(self)
        
class Context():
    def __init__(self , parent = None) -> None:
        self.context_lower : ContextLower = ContextLower()
        self.types : list[Type] = []

    def is_defined(self, var) -> bool:
        return self.context_lower.is_defined(var)
    
    def is_defined_local(self, var) -> bool:
        return self.context_lower.is_defined_local(var)
    
    def is_defined_func(self, func, args) -> bool:
        return self.context_lower.is_defined_func(func, args)

    def is_defined_func_whithout_params(self, func) -> bool:
        return self.context_lower.is_defined_func_whithout_params(func)


    def get(self, name):
        return self.context_lower.get(name)     
    
    def set(self, name, type_new = None, value = None):
        self.context_lower.dict[name] = ComputedValue(type_new, value)

    def define(self, var, type = None, value = None) -> bool:
        return self.context_lower.define(var, type, value)
    
    def remove_define(self, var) -> bool:
        return self.context_lower.remove_define(var)
    
    def define_func(self, var, return_type, args) -> bool:
        return self.context_lower.define_func(var, return_type, args)
    
    def create_child_context(self):
        self.context_lower = self.context_lower.create_child_context()
    
    def remove_child_context(self):
        self.context_lower = self.context_lower.parent 

    def get_type(self, type_name):
        for i in self.types:
            if i.name == type_name:
                return i
        return None
    
    def get_protocols(self):
        protocols = []
        for i in self.types:
            if i.args == None:
                protocols.append(i)
        return protocols

    def defineSymbol(self, symbol, type) -> bool:
        return False
    
    def create_type(self, name, args = [], methods = []):
        if (self.get_type(name) != None):
            return False
        self.types.append(Type(name, args, methods))
        return True



class FunctionCollectorVisitor(Visitor):
    def __init__(self, context : Context):
        self.context = context
        self.error_logger = []

    def visit_program_node(self, program_node : ProgramNode):
        j = 1
        for i in program_node.decls:
            if j < len(program_node.decls):
                i.accept(self)
            j+=1

    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass
    def visit_method_node(self, method_node : MethodNode):
        id = method_node.id.lexeme
        args = method_node.params
        ret = method_node.type.lexeme if method_node.type != None else "Object"

        if (self.context.is_defined_func(id, args)) == None:
            self.context.define_func(id, ret, args)
            return
        #self.error_logger.append(Error(f"function {id} already exist", method_node.id.line, method_node.id.offsetLine))

    def visit_type_node(self, type_node : TypeNode):
        pass
    def visit_signature_node(self, signature_node : SignatureNode):
        pass
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass
    def visit_let_node(self, let_node : LetNode):
        pass
    def visit_while_node(self, while_node : WhileNode):
        pass
    def visit_for_node(self, for_node : ForNode):
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
        pass
    def visit_call_node(self, call_node : CallNode):
        pass
    def visit_get_node(self, get_node : GetNode):
        pass
    def visit_set_node(self, set_node : SetNode):
        pass
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        pass
    def visit_new_node(self, new_node : NewNode):
        pass
    def visit_binary_node(self, binary_node : BinaryNode):
        pass
    def visit_unary_node(self, unary_node : UnaryNode):
        pass
    def visit_literal_node(self, literal_node : LiteralNode):
        pass




class VariableDefinedVisitor(Visitor):
    def __init__(self, context):
        self.context: Context = context
        self.error_logger = []
        self.actual_type = None
        self.queue_call = []
        self.is_instanciated_type_attr = False
        self.analize_attr_type = False
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        id = attribute_node.id.lexeme
        if self.actual_type != None and self.analize_attr_type == True: 
            id = 'self.' + id
        if self.context.is_defined_local(id) == False: # variable no declarada antes
            self.context.define(id)
            if self.is_instanciated_type_attr == True:
                self.is_instanciated_type_attr = False
                attribute_node.body.accept(self)
                return ComputedValue(None, id)
            attribute_node.body.accept(self)
            return
        else:   # pq si estoy en un let puede ya estar definida y se puede sobrescribir
            if len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1]) == "let":
                attribute_node.body.accept(self)
                self.context.context_lower.dict[id] = ComputedValue(None, None)
            else:
                #self.error_logger.append(Error(f"attribute {id} already defined", attribute_node.id.line, attribute_node.id.offsetLine))
                pass
        
            
    def visit_method_node(self, method_node : MethodNode):
        id = method_node.id.lexeme
        attr = []
        if id == "main":
            return method_node.body.accept(self)
 
        self.context.create_child_context()
        for (i, j) in method_node.params:
            d = self.context.is_defined(i.lexeme)
            if d != False:
                #self.error_logger.append(Error(f"param of function already exist", method_node.id.line, method_node.id.offsetLine))
                pass
            else:
                self.context.define(i.lexeme)
        method_node.body.accept(self)            
        self.context.remove_child_context()
        return ComputedValue(None, None)

    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = type_node.id.lexeme
        self.context.create_child_context()
        self.context.define("self", "self")
        self.context.define_func("base", "base", []) # base es un llamado de funcion

        for i in type_node.methods:
            if i.id.lexeme == "build":
                for j in i.params: # definir los parametros para el constructor
                    self.context.define(j[0].lexeme, j[1].lexeme if j[1] != None else None)
                self.is_instanciated_type_attr = True
                attr = []
                for j in i.body.exprs: # inicializar los atributos
                    self.analize_attr_type = True
                    attr.append(j.accept(self))
                    self.analize_attr_type = False
                self.is_instanciated_type_attr = False

                for j in attr:
                    if j != None:
                        self.context.define(j.value, j.type)

                for j in i.params:
                    self.context.remove_define(j[0].lexeme)
            else:
                i.accept(self)
        self.context.remove_child_context()
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        for (i, j) in signature_node.params :
            if self.context.context_lower.dict.get(i.lexeme) == None:
                self.context.context_lower.dict[i.lexeme] = True
            else:
                #_logger.append(Error(f"param already exist in signature ", signature_node.id.line, signature_node.id.offsetLine))
                pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        for i in protocol_node.signatures:
            i.accept(self)
            
    def visit_let_node(self, let_node : LetNode):
        self.context.create_child_context()
        self.queue_call.append("let")
        for i in let_node.assignments:
            i.accept(self)
        self.queue_call.pop()
        let_node.body.accept(self)             
        self.context.remove_child_context()

    def visit_while_node(self, while_node : WhileNode):
        self.context.create_child_context()
        while_node.condition.accept(self)
        while_node.body.accept(self)
        self.context.remove_child_context()
    
    def visit_for_node(self, for_node : ForNode):
        self.context.create_child_context()
        if self.context.is_defined_local(for_node.target.lexeme) == False:
            #self.error_logger.add(Error(f"variable not defined", for_node.target.line, for_node.target.offsetLine))
            pass
        for_node.iterable.accept(self) 
        for_node.body.accept(self)
        self.context.remove_child_context()
    
    def visit_if_node(self, if_node : IfNode):
        for (i, j) in if_node.body:
            self.context.create_child_context()
            i.accept(self)
            t = j.accept(self)
            self.context.remove_child_context()

        self.context.create_child_context()
        if_node.elsebody.accept(self)
        self.context.remove_child_context()

    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        for i in explicit_vector_node.items:
            i.accept(self)

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        self.context.create_child_context()
        if self.context.is_defined_local(implicit_vector_node.target.lexeme) == False:
            self.context.define(implicit_vector_node.target.lexeme)
        else:
            #self.error_logger.append(Error(f"variable {implicit_vector_node.target.lexeme} not defined", implicit_vector_node.target.line, implicit_vector_node.target.offsetLine))
            pass
        implicit_vector_node.iterable.accept(self)
        implicit_vector_node.result.accept(self)
        self.context.remove_child_context()

    def visit_destructor_node(self, destructor_node : DestructorNode):
        if self.context.is_defined(destructor_node.id.lexeme) == False:
            #self.error_logger.append(Error(f"variable {destructor_node.id.lexeme} not defined ", destructor_node.id.line, destructor_node.id.offsetLine))
            pass
        
        id = destructor_node.id.lexeme
        type = self.context.get(id).type
        if id == "self" and  type == "self":
            self.error_logger.append(Error(f"self not cant use in a destructor_node", destructor_node.id.line, destructor_node.id.offsetLine))
            return
        destructor_node.expr.accept(self)
        

    def visit_block_node(self, block_node : BlockNode):
        self.context.create_child_context()
        for i in block_node.exprs:
           i.accept(self)
        self.context.remove_child_context()    

    def visit_call_node(self, call_node : CallNode):
        self.queue_call.append("call")
        call_node.callee.accept(self)
        self.queue_call.pop()
        aux_queue = self.queue_call
        for i in call_node.args:
            i.accept(self)
        self.queue_call = aux_queue

    def visit_get_node(self, get_node : GetNode):
        self.queue_call.append("get")
        left = get_node.left.accept(self)
        self.queue_call.pop()

    def visit_set_node(self, set_node : SetNode):
        set_node.left.accept(self)
        set_node.value.accept(self)

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        vector_set_node.index.accept(self)
        vector_set_node.left.accept(self)
        vector_set_node.value.accept(self)
        return True

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        vector_get_node.left.accept(self)
        vector_get_node.index.accept(self)

    def visit_new_node(self, new_node : NewNode):
        for i in new_node.args:
            i.accept(self)

    def visit_binary_node(self, binary_node : BinaryNode):
        binary_node.left.accept(self) 
        if binary_node.op.lexeme == "is" or binary_node.op.lexeme == "as":
            return
        binary_node.right.accept(self)
    
    def visit_unary_node(self, binary_node : UnaryNode):
        binary_node.expr.accept(self)    

    def visit_literal_node(self, literal_node : LiteralNode):
        if literal_node.id.lexeme == "PI":
            literal_node.id.lexeme = "3.1415"
            literal_node.id.type = "number"
        id = literal_node.id.lexeme
        match literal_node.id.type: 
            case "id":
                defined = self.context.is_defined(id)

                if id == "self" and defined:
                    if self.context.get("self").type == "self":
                        if (len(self.queue_call) == 2) and self.queue_call[0] == 'get' and self.queue_call[1] == 'get':
                            #self.error_logger.append(Error(f"trying to get a attribute private", literal_node.id.line, literal_node.id.offsetLine))
                            pass
                            
                        if len(self.queue_call) > 2:
                            mk = self.queue_call[0] 
                            for i in range(1, len(self.queue_call) - 2):
                                ele = self.queue_call[i]
                                if ele != "get" and ele != "call":
                                    break
                                if mk != ele:
                                    mk = ele
                                else:
                                    #self.error_logger.append(Error(f"not correct use of callist", literal_node.id.line, literal_node.id.offsetLine))
                                    pass
                    return
                if defined != False and len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1]) == "get":
                    var = self.context.get(id)
                    return ComputedValue(var.type, var.value)
                if len(self.queue_call) > 0 and (self.queue_call[len(self.queue_call) - 1]) == "call":
                    if self.context.is_defined_func_whithout_params(id) == True:
                        return ComputedValue(None, id)
                    else:
                        #self.error_logger.append(Error(f"function {id} not defined", literal_node.id.line, literal_node.id.offsetLine))
                        pass
                        return

                if defined != False:
                    var = self.context.get(id)
                else:
                   #self.error_logger.append(Error(f"variable {id} not defined", literal_node.id.line, literal_node.id.offsetLine))
                   pass
                return ComputedValue(None)
        return ComputedValue("Object", None)
