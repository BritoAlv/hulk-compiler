# from os import name
# from turtle import right
# from sqlalchemy import false
# from traitlets import default
from common.ErrorLogger.ErrorLogger import ErrorLogger
from common.ast_nodes.expressions import *
from common.ast_nodes.expressions import VectorGetNode
from common.ast_nodes.statements import *
from common.visitor import Visitor



class Type:
    def __init__(self, name) -> None:
        self.name = name
        self.attribute = []
        self.method = []

    def get_attribute(self, name):
        for i in self.attribute:
            if i.name == name:
                return i
        return None
    
    def get_method(self, name, args):
        for i in self.method:
            if i.name == name and i.args == args:
                return i
        return None

    def define_attribute(self, name, type):
        if self.get_attribute(name) != None:
            return False
        self.attribute.append(Attribute(name, type))

    def define_method(self, name, return_type, arg):
        if self.get_attribute(name) != None:
            return False
        self.method.append(Method(name, return_type, arg))

class Attribute:
    def __init__(self, name, itype) -> None:
        self.name = name
        self.type = itype

class Method:
    def __init__(self, name, return_type, args) -> None:
        self.name = name
        self.type = return_type
        self.args = args

class Context():
    def __init__(self , parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.function = {}
        self.types : list[Type] = []

    def is_defined(self, var) -> bool:
        return self.dict.get(var) or (self.parent != None and self.parent.is_defined(var))
    
    def is_defined_func(self, func, args) -> bool:
        if self.function.get(func) and self.function[func] == args:
            return True
        return (self.parent != None and self.parent.is_defined_func(func, args))
    
    def define(self, var, type) -> bool:
        if self.is_defined(var):
            return False
        self.dict[var] = type
        return True
    
    def define_func(self, var, args) -> bool:
        if self.is_defined_func(var, args):
            return False
        self.function[var] = True
        return True
    
    def create_child_context(self):
        return Context(self)
    
    def get_type(self, type_name):
        for i in self.types:
            if i.name == type_name:
                return i
        return None
    def get_type_for(self, symbol):
        pass
    def defineSymbol(self, symbol, type) -> bool:
        return False
    def create_type(self, name):
        if (self.get_type(name) != None):
            return False
        self.types.append(Type(name))
        return True

class NodeClass:
    def __init__(self, name, sons = []) -> None:
        self.name = name
        self.sons = sons
class Hierarchy:
    def __init__(self) -> None:
        self.root = NodeClass("Object", [NodeClass("Number"), NodeClass("String"), NodeClass("Boolean")])

    def get_type(self, actual: NodeClass, name):
        if (actual.name == name):
            return actual
        for i in actual.sons:
            if self.get_type(i, name) != None:
                return i
        return None
    
    def add_type(self, name, ancestor_name):
        ancestor = self.get_type(self.root, ancestor_name)
        if ancestor != None:
            ancestor.sons.append(name)

# construye el contexto de los tipos definidos y chequea que no hayan dos con el mismo nombre
class TypeCollectorVisitor(Visitor):
    def __init__(self, context : Context):
        self.context = context
        self.error_logger = ErrorLogger()
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)
        print(self.context.get_type("Perro") )
    
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        pass

    def visit_method_node(self, method_node : MethodNode):
        pass

    def visit_type_node(self, type_node : TypeNode):
        if self.context.create_type(type_node.id.lexeme) == False:
            self.error_logger.add("variable ya creada")


    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        if self.context.create_type(protocol_node.id.lexeme) == False:
            self.error_logger.add("variable ya creada")

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
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True

    def visit_literal_node(self, literal_node : LiteralNode):
        pass
 
class TypeBuilderVisitor(Visitor):
    def __init__(self, context : Context, hierarchy : Hierarchy):
        self.context = context
        self.actual_type = None
        self.hierarchy = hierarchy
        self.error_logger = ErrorLogger()
        print(self.context.get_type("Perro") )

    def visit_program_node(self, program_node : ProgramNode):
        j = 1
        for i in program_node.decls:
            if j < len(program_node.decls):
                # print(i, len(program_node.decls))
                i.accept(self)
            j+=1
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        if self.actual_type != None:
            if self.actual_type.get_attribute(attribute_node.id.lexeme) == None:
                self.actual_type.define_attribute(attribute_node.id.lexeme, attribute_node.type.lexeme if attribute_node.type != None else "object")
                return    
            self.error_logger.add("atributo ya definido " + attribute_node.id.lexeme + " de " + self.actual_type.name)

    def visit_method_node(self, method_node : MethodNode):
        if self.actual_type != None:
            if self.actual_type.get_method(method_node.id.lexeme, len(method_node.params)) == None:
                self.actual_type.define_method(method_node.id.lexeme, method_node.type.lexeme if method_node.type != None else "object", len(method_node.params))
                return
            self.error_logger.add("metodo ya definido " + method_node.id.lexeme + " de " + self.actual_type.name)
            
    def visit_type_node(self, type_node : TypeNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(type_node.id.lexeme)
        if type_node.ancestor_id != None:
            ancestor_type = self.context.get_type(type_node.ancestor_id.lexeme)
            if ancestor_type == False:
                self.error_logger.add("clase herada incorrectamente")
            self.hierarchy.add_type(type_node.id.lexeme, type_node.ancestor_id.lexeme)
        for i in type_node.methods:
            i.body.accept(self)
        self.actual_type = last_type

    def visit_signature_node(self, signature_node : SignatureNode):
        if self.actual_type != None:
            if self.actual_type.get_method(signature_node.id.lexeme, len(signature_node.params)) == None:
                self.actual_type.define_method(signature_node.id.lexeme, signature_node.type.lexeme if signature_node.type != None else "object", len(signature_node.params))
                return
                
            self.error_logger.add("metodo ya definido " + signature_node.id.lexeme + " de " + self.actual_type.name)

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        last_type = self.actual_type
        self.actual_type = self.context.get_type(protocol_node.id.lexeme)
        if protocol_node.ancestor_node != None:
            ancestor_type = self.context.get_type(protocol_node.ancestor_node.lexeme)
            if ancestor_type == False:
                self.error_logger.add("clase herada incorrectamente")
            self.hierarchy.add_type(protocol_node.id.lexeme, protocol_node.ancestor_node.lexeme)
        
        for i in protocol_node.signatures:
            i.accept(self)
            
        self.actual_type = last_type

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
        # print(1)
        for i in block_node.exprs:
            i.accept(self)

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

    def visit_literal_node(self, literal_node : LiteralNode):
        pass
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True
    

class TypeCheckerVisitor(Visitor):
    def __init__(self, context : Context, hierarchy : Hierarchy):
        self.context = context
        self.actual_type = None
        self.hierarchy = hierarchy
        self.error_logger = ErrorLogger()
        print(self.context.get_type("Perro") )


    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            i.accept(self)

    def visit_attribute_node(self, attribute_node : AttributeNode):
        if self.context.is_defined(attribute_node.id.lexeme) == False:
            body = attribute_node.body.accept(self)
            if (attribute_node.type != None):
                if (attribute_node.type.lexeme == body):
                    self.context.define(attribute_node.id.lexeme, body)
                    return 
                self.error_logger.add("atributo " + attribute_node.id.lexeme + " con tipo incorrecto")
                return
            self.context.define(attribute_node.id.lexeme, body)
            return
        self.error_logger.add("atributo " + attribute_node.id.lexeme + "ya definido")
        
    def visit_method_node(self, method_node : MethodNode):
        return method_node.body.accept(self)

    def visit_type_node(self, type_node : TypeNode):
        pass

    def visit_signature_node(self, signature_node : SignatureNode):
        pass

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        pass

    def visit_let_node(self, let_node : LetNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        for i in let_node.assignments:
            i.accept(self)
        # self.context.dict[""]
        value = let_node.body.accept(self)             
        self.context = old_context
        return value
    
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
        type = self.context.get_type(new_node.id.lexeme) 
        if type != None:
            for i in new_node.args:
                i.accept(self)
            return type.name
        self.error_logger.add("clase no definida " + new_node.id.lexeme)

    def visit_binary_node(self, binary_node : BinaryNode):
        left = binary_node.left.accept(self)
        right = binary_node.right.accept(self)
        # print(left, right)
        if left == right:
            return left
        self.error_logger.add("inconsistencia de tipos en op binaria")
        return "Object"
    def visit_unary_node(self, unary_node : UnaryNode):
        pass

    def visit_literal_node(self, literal_node : LiteralNode):
        match literal_node.id.type:
            case "false":
                return "Bolean"
            case "true":
                return "Bolean"
            case "number":
                return "Number"
            case "string":
                return "String"
        return "Object"




class SemanticAnalysis:
    def __init__(self) -> None:
        pass
    
    def run(self, ast):
        context = Context()
        hierarchy = Hierarchy()

        typeCollectorVisitor = TypeCollectorVisitor(context)
        typeBuilderVisitor = TypeBuilderVisitor(context, hierarchy)
        typeCheckerVisitor = TypeCheckerVisitor(context, hierarchy)

        err1 = typeCollectorVisitor.error_logger
        err2 = typeBuilderVisitor.error_logger
        err3 = typeCheckerVisitor.error_logger

        ast.accept(typeCollectorVisitor)
        ast.accept(typeBuilderVisitor)
        ast.accept(typeCheckerVisitor)
        
        err1.log_errors()
        err2.log_errors()
        err3.log_errors()

# from parsing.parser.parser import Parser
# from parsing.parser_generator_lr.parsing_table import ParsingTable

# tableHulk = ParsingTable.load_parsing_table("hulk_grammar")
# # print(tableHulk)

# node = tableHulk.parse(
#     [Token(x, x, 0, 0) for x in [
#         'type', 'id', 'lparen', 'id', 'colon', 'id', 'comma', 'id', 'colon', 'id', 'rparen',
#         'lbrace',
#             'id', 'equal', 'id', 'semicolon',
#             'id', 'equal', 'id', 'semicolon',
#             'id', 'equal', 'id', 'minus', 'number','semicolon',

#             'id', 'lparen', 'rparen', 'colon', 'id', 'arrow', 'lparen', 'self', 'dot', 'id', 'destrucOp', 'self', 'dot', 'id', 'plus', 'number', 'rparen', 'less', 'id', 'semicolon',
#         'rbrace',

#         'protocol', 'id',
#         'lbrace',
#             'id', 'lparen', 'id', 'colon', 'id', 'rparen', 'colon', 'id', 'semicolon',
#             'id', 'lparen', 'rparen', 'colon', 'id', 'semicolon',
#         'rbrace',
        
#         'protocol', 'id', 'extends', 'id',
#         'lbrace',
#             'id', 'lparen', 'id', 'colon', 'id', 'rparen', 'colon', 'id', 'semicolon',
#             'id', 'lparen', 'rparen', 'colon', 'id', 'semicolon',
#         'rbrace',

#         'lbrace',

#         'let', 'id', 'equal', 'lbracket', 'id', 'doubleOr', 'id', 'in', 'id', 'lparen', 'id', 'comma', 'id', 'rparen', 'rbracket', 'in', 'id', 'lparen', 'id', 'rparen', 'semicolon',

#         'let', 'id', 'equal', 'lbracket', 'number', 'comma', 'number', 'comma', 'number', 'comma', 'number', 'comma', 'number', 'rbracket', 'in',
#         'for', 'lparen', 'id', 'in', 'id', 'rparen',
#             'id', 'lparen', 'id', 'rparen', 'semicolon',

#         'lparen', 'id', 'rparen', 'dot', 'id', 'semicolon',

#         'let', 'id', 'equal', 'new', 'id', 'lparen', 'number', 'comma', 'id', 'rparen', 'in', 'id', 'lparen', 'id', 'rparen', 'semicolon',
#         'rbrace', 'semicolon',
#         '$']]
# )


# node.root.print([0], 0, True)

# context = Context()

# typeCollectorVisitor = TypeCollectorVisitor(context)
# typeBuilderVisitor = TypeBuilderVisitor(context)

# p = Parser()

# ast = p.toAst(node)

# ast.accept(typeCollectorVisitor)
# print(ast.accept(typeBuilderVisitor))
