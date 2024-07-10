from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor
from common.ErrorLogger import Error
class SemanticCheck(Visitor):
    """
    Set Types for the given symbols in the Program.
    """
    def __init__(self, resolver : Resolver):
        self._resolver = resolver
        self._errors : list[Error] = []

        self._in_type = False
        self._in_method = False
        self._in_attribute = False
        self._method_name :  str | None = None
        self._type_name : str = None
        self._stack = [[]]

    def semantic_check(self, program : ProgramNode) -> list[str]:
        self._semantic_check(program)
        return self._errors
    
    def log_error(self, error : str):
        self._errors.append(error)

    def visit_program_node(self, program_node : ProgramNode):
        for decl in program_node.decls:
            self._semantic_check(decl)
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        attr_name = attribute_node.id.lexeme
        if not self._in_type:
            self.log_error(Error(f"Attribute {attribute_node.id.lexeme} declaration must be inside a type declaration", attribute_node.id.line, attribute_node.id.offsetLine))
            self._stack.append([])
            self._semantic_check(attribute_node.body)
            self._stack.pop()
            return 
        
        type_data = self._resolver.resolve_type_data(self._type_name)
        
        if attr_name not in type_data.attributes:
            self.log_error(Error(f"Attribute {attr_name} not in {self._type_name} attributes " , attribute_node.id.line , attribute_node.id.offsetLine))
            return
        self._in_attribute = True
        self._stack.append([])
        self._semantic_check(attribute_node.body)
        self._stack.pop()
        self._in_attribute = False
        
        if attribute_node.type != None: 
            stated_type = attribute_node.type.lexeme
            if stated_type not in self._resolver.resolve_types():
                self.log_error(Error(f"Type {stated_type} given for attribute {attr_name} in type declaration {self._type_name} does not exist " , attribute_node.id.line , attribute_node.id.offsetLine))
    
    def visit_method_node(self, method_node : MethodNode):
        self._in_method = True
        func_name = method_node.id.lexeme

        if func_name in ["print"] and not self._in_type:
            self.log_error(Error(f"Can't declare a method called [print] " , method_node.id.line , method_node.id.offsetLine))

        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._method_name = func_name
        
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        
        i = 0
        for param, type in method_node.params:
            i += 1
            if type != None and type.lexeme in self._resolver.resolve_types():
                func_data.params[param.lexeme].type = type.lexeme
                continue
            elif type != None:
                self.log_error(Error(f"Parameter Type {type.lexeme} given for param {param.lexeme} at method {method_node.id.lexeme} " + (f"in type declaration {self._type_name}" if self._in_type else "") + f" does not exist " , method_node.id.line , method_node.id.offsetLine))

        declared_type = method_node.type
        self._stack.append([])
        self._semantic_check(method_node.body)
        self._stack.pop()

        if declared_type != None:
            declared_type = declared_type.lexeme
            if declared_type not in self._resolver.resolve_types():
                self.log_error(Error(f"Type {declared_type} given for method {method_node.id.lexeme} " + (f"in type declaration {self._type_name}" if self._in_type else "") + f" does not exist " , method_node.id.line , method_node.id.offsetLine))

        self._in_method = False    
        self._method_name = None
        return None
    
    def visit_type_node(self, type_node : TypeNode):
        self._in_type = True
        self._type_name = type_node.id.lexeme

        if self._type_name in ["Any"]:
            self.log_error(Error(f"Can't declare [Any] as typenames " , type_node.id.line , type_node.id.offsetLine))

        if type_node.ancestor_id != None:
            ancestor = type_node.ancestor_id.lexeme
            if ancestor not in self._resolver.resolve_types():
                self.log_error(Error(f"Can't inherit {type_node.id.lexeme} from a non-existing type {ancestor} " , type_node.id.line , type_node.id.offsetLine))
            elif ancestor in ["Number", "String", "Vector", "Node", "Boolean"]:
                self.log_error(Error(f"Can't inherit {type_node.id.lexeme} from a basic type like [Number, String, Vector, Node, Boolean] " , type_node.id.line , type_node.id.offsetLine))

        for method in type_node.methods:
            self._semantic_check(method)

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
            self._stack.append([])
            self._semantic_check(assig.body)
            self._stack.pop()
            if op_type != None and op_type.lexeme not in self._resolver.resolve_types():
                self.log_error(Error(f"Given tipe for variable {var_name} in let_expression doesn't exist " , assig.id.line , assig.id.offsetLine))
                    
        self._stack.append([])
        self._semantic_check(let_node.body)
        self._stack.pop()
        self._resolver.next()

    def visit_while_node(self, while_node : WhileNode):
        self._stack.append([])
        self._semantic_check(while_node.condition) 
        self._stack.pop()
        self._stack.append([])
        self._semantic_check(while_node.body)
        self._stack.pop()
    
    def visit_if_node(self, if_node : IfNode):
        self._stack.append([])
        self._semantic_check(if_node.elsebody)
        self._stack.pop()
        for st in if_node.body:
            self._stack.append([])
            self._semantic_check(st[0])
            self._stack.pop()
            self._stack.append([])
            self._semantic_check(st[1])
            self._stack.pop()
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        print("Not Needed")
        pass

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        print("Not Needed")
        pass
    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        var_name = destructor_node.id.lexeme
        try:
            self._resolver.resolve_var_data(var_name)
            self._stack.append([])
            self._semantic_check(destructor_node.expr)
            self._stack.pop()
        except:
            self.log_error(Error(f"Trying to destruct a not unitialized variable " , destructor_node.id.line , destructor_node.id.offsetLine))
            return 'Object'


    def visit_block_node(self, block_node : BlockNode):
        for expr in block_node.exprs:
            self._stack.append([])
            self._semantic_check(expr)
            self._stack.pop()

    def visit_call_node(self, call_node : CallNode):
        self._stack[-1].append(call_node)
        if not isinstance(call_node.callee, GetNode) and not isinstance(call_node.callee, LiteralNode):
            self.log_error(Error(f"An expression can't return a function " , call_node.handle.line , call_node.handle.offsetLine)) 
        self._semantic_check(call_node.callee)
        self._stack[-1].pop()
        for arg in call_node.args:
            self._stack.append([])
            self._semantic_check(arg)
            self._stack.pop()

    def visit_get_node(self, get_node : GetNode):
        self._stack[-1].append(get_node)
        if isinstance(get_node.left, LiteralNode) and get_node.left.id.lexeme == "self" and self._in_attribute and self._resolver.resolve_var_data("self").type == self._type_name:
            self.log_error(Error(f"Cannot access to self in attribute declaration " , get_node.left.id.line , get_node.left.id.offsetLine))
            return "Object"
        
        if isinstance(get_node.left, LiteralNode) and not self._in_type and isinstance(self._stack[-2], GetNode) :
            self.log_error(Error(f"Attributes are private " , get_node.left.id.line , get_node.left.id.offsetLine))

        self._semantic_check(get_node.left)
        self._stack[-1].pop()
    
    def visit_set_node(self, set_node : SetNode):
        if isinstance(set_node.left, LiteralNode) and set_node.left.id.lexeme == "self" and self._in_attribute and self._resolver.resolve_var_data("self").type == self._type_name:
            self.log_error(Error(f"Cannot access to self in attribute declaration " , set_node.left.id.line , set_node.left.id.offsetLine))
            return "Object"
        self._semantic_check(set_node.left)
        self._semantic_check(set_node.value)
        
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        pass
    
    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        self._semantic_check(vector_get_node.index)
        self._semantic_check(vector_get_node.left)

    def visit_new_node(self, new_node : NewNode):
        type_name = new_node.id.lexeme

        if type_name in self._resolver.resolve_protocols():
            self.log_error(Error(f"Cannot instantiate a protocol {type_name} " , new_node.id.line , new_node.id.offsetLine))

        if type_name not in self._resolver.resolve_types():
            self.log_error(Error(f"Cannot instantiate a not declared type {type_name} " , new_node.id.line , new_node.id.offsetLine))
            return 'Object'
        for arg in new_node.args:
            self._semantic_check(arg)
        return type_name
    
    def visit_binary_node(self, binary_node : BinaryNode):
        self._semantic_check(binary_node.left)
        self._semantic_check(binary_node.right)
    
    def visit_unary_node(self, unary_node : UnaryNode):
        self._semantic_check(unary_node.expr)
            
    def visit_literal_node(self, literal_node : LiteralNode):
        pass

    def _semantic_check(self, node : Statement) -> str:
        return node.accept(self)