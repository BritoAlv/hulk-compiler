from sqlalchemy import false
from common.ast_nodes.expressions import *
from common.ast_nodes.statements import *
from common.visitor import Visitor

class Context():
    def __init__(self , parent = None) -> None:
        self.parent = parent
        self.dict = {}
        self.function = {}

    def is_defined(self, var) -> bool:
        return self.dict.get(var) or (self.parent != None and self.parent.is_defined(var))
    
    def is_defined_func(self, func, args) -> bool:
        if self.function.get(func) and self.function[func] == args:
            return True
        return (self.parent != None and self.parent.is_defined_func(func, args))
    
    def define(self, var) -> bool:
        if self.is_defined(var):
            return False
        self.dict[var] = True
        return True
    
    def define_func(self, var, args) -> bool:
        if self.is_defined_func(var, args):
            return False
        self.function[var] = True
        return True
    
    def create_child_context(self):
        return Context(self)

class VariableDefinedVisitor(Visitor):
    def __init__(self):
        self.context = Context()
    
    def visit_program_node(self, program_node : ProgramNode):
        for i in program_node.decls:
            if i.accept(self) != True:
                return False
        return True
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        # if attribute_node.body.accept(self) and 
        if self.context.define(attribute_node.id.lexeme):
            return True

    def visit_method_node(self, method_node : MethodNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        for i in method_node.params:
            self.context.define(i[0].lexeme)
        self.context = old_context
        return method_node.body.accept(self)

    def visit_type_node(self, type_node : TypeNode):
        return True

    def visit_signature_node(self, signature_node : SignatureNode):
        return True

    def visit_protocol_node(self, protocol_node : ProtocolNode):
        return True

    def visit_let_node(self, let_node : LetNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        for i in let_node.assignments:
            if i.accept(self) == False:
                return False

        mk = let_node.body.accept(self)             
        self.context = old_context
        return mk

    def visit_while_node(self, while_node : WhileNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        if while_node.condition.accept(self) and while_node.body.accept(self):
            return True
        self.context = old_context
        return False
    def visit_for_node(self, for_node : ForNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        if self.context.define(for_node.target.lexeme) and for_node.iterable.accept(self) and for_node.body.accept(self):
            return True
        self.context = old_context
        return False
    def visit_if_node(self, if_node : IfNode):
        for (i, j) in if_node.body:
            old_context = self.context
            self.context = old_context.create_child_context()
            if i.accept(self) == False or j.accept(self) == False:
                return False
            self.context = old_context
        return True

    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        for i in explicit_vector_node.items:
            i.accept(self)
        return True

    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        self.context.define(implicit_vector_node.target)
        implicit_vector_node.iterable.accept(self)
        implicit_vector_node.result.accept(self)
        self.context = old_context
        return True

    def visit_destructor_node(self, destructor_node : DestructorNode):
        return self.context.is_defined(destructor_node.id.lexeme) and destructor_node.expr.accept(self)
        

    def visit_block_node(self, block_node : BlockNode):
        old_context = self.context
        self.context = old_context.create_child_context()
        for i in block_node.exprs:
           print(i)
           if i.accept(self) == False:
                return False
        self.context = old_context
        return True
    
    def visit_call_node(self, call_node : CallNode):
        mk = call_node.callee.accept(self)
        for i in call_node.args:
            if i.accept(self) == False:
                return False
        return True

    def visit_get_node(self, get_node : GetNode):
        return self.context.define(get_node.id.lexeme) and get_node.left.accept(self)

    def visit_set_node(self, set_node : SetNode):
        set_node.left.accept(self)
        set_node.value.accept(self)
        return True

    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        vector_set_node.index.accept(self)
        vector_set_node.left.accept(self)
        vector_set_node.value.accept(self)
        return True

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        return vector_get_node.left.accept(self) and vector_get_node.index.accept(self)

    def visit_new_node(self, new_node : NewNode):
        if self.context.is_defined(new_node.id.lexeme):
            return False
        for i in new_node.args:
            i.accept(self)
        return True

    def visit_binary_node(self, binary_node : BinaryNode):
        return binary_node.left.accept(self) and binary_node.right.accept(self)
    
    def visit_unary_node(self, binary_node : UnaryNode):
        
        return True
    

    def visit_literal_node(self, literal_node : LiteralNode):
        return True




from parsing.parser.parser import Parser
from parsing.parser_generator_lr.parsing_table import ParsingTable

tableHulk = ParsingTable.load_parsing_table("hulk_grammar")
# print(tableHulk)

node = tableHulk.parse(
    [Token(x, x, 0, 0) for x in [
        'lbrace',
        'let', 'id', 'colon', 'id', 'equal', 'id', 'plus', 'number', 'in', 'lparen', 'number', 'rparen', 'semicolon',
        
        'id', 'destrucOp', 'lparen', 'number', 'plus', 'number', 'rparen', 'semicolon',

        'number', 'semicolon',

        'id', 'dot', 'id', 'semicolon',

        'id', 'dot', 'id', 'dot', 'id', 'lparen', 'rparen', 'semicolon',
        'rbrace', 'semicolon',
        '$']]
)


node.root.print([0], 0, True)

v = Vi()

p = Parser()

context = Context()
ast = p.toAst(node)
print(ast.accept(v))
