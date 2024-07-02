from hmac import new
from textwrap import indent
from common.ast_nodes.expressions import UnaryNode
from common.ast_nodes.statements import *
from common.ast_nodes.expressions import *
from common.visitor import Visitor

class IndentManager:
    def __init__(self, printer):
        self.printer = printer

    def __enter__(self):
        self.printer.indent += 1

    def __exit__(self, type, value, traceback):
        self.printer.indent -= 1

class TreePrinter(Visitor):
    def __init__(self):
        self.indent = 0
        self.current = ""

    def do_space(self):
        a = ""
        for i in range(0, self.indent):
            a += "    "
        return a + "└── "

    def add_word(self, word):
        self.current += self.do_space() + word + "\n"

    def visit_program_node(self, program_node : ProgramNode):
        self.add_word("Program")
        with IndentManager(self):
            for decl in program_node.decls:
                decl.accept(self)
        return self.current
    
    
    def visit_attribute_node(self, attribute_node : AttributeNode):
        self.add_word("Attribute")
        with IndentManager(self):
            self.add_word(attribute_node.id.lexeme)
            if attribute_node.type != None:
                self.add_word("type = " + attribute_node.type.lexeme)
            attribute_node.body.accept(self)
        return self.current
   
    def visit_method_node(self, method_node : MethodNode):
        self.add_word("Method : " + method_node.id.lexeme)
        with IndentManager(self):
            self.add_word("params :")
            with IndentManager(self):
                for param in method_node.params:
                    self.add_word(param[0].lexeme + (" of type :" + param[1].lexeme if param[1] != None else ""))

        with IndentManager(self):
            self.add_word("body : ")
            with IndentManager(self):
                method_node.body.accept(self)

        return self.current
    
    def visit_type_node(self, type_node : TypeNode):
        opt_inheritance = ""
        if type_node.ancestor_id != None:
            opt_inheritance = " inheriting: " + type_node.ancestor_id.lexeme # type: ignore
        
        self.add_word("Class " + type_node.id.lexeme)
        if type_node.ancestor_id != None:
            self.add_word(opt_inheritance)
        
        with IndentManager(self):
            self.add_word("Attributes")
            with IndentManager(self):
                for attr in type_node.attributes:
                    opt_type = ""
                    if attr[1] != None:
                        opt_type = " of type " + attr[1].lexeme
                    self.add_word(attr[0].lexeme+ opt_type)
            self.add_word("Methods")
            with IndentManager(self):
                for method in type_node.methods:
                    method.accept(self) # type: ignore
        
        return self.current
        
    def visit_signature_node(self, signature_node : SignatureNode):
        self.add_word("Signature Node " + signature_node.id.lexeme + " of type " + signature_node.type.lexeme)
        self.add_word("Params:")
        with IndentManager(self):
            for param in signature_node.params:
                self.add_word(param[0].lexeme + " of type " + param[1].lexeme)
        return self.current
    
    def visit_protocol_node(self, protocol_node : ProtocolNode):
        self.add_word("Protocol Node")
        opt_type = ""
        if protocol_node.ancestor_node != None:
            opt_type = " inheriting: " + protocol_node.ancestor_node.lexeme
        self.add_word("Protocol Node " + protocol_node.id.lexeme + opt_type)
        return self.current

    def visit_let_node(self, let_node : LetNode):
        self.add_word("Let Node ")
        with IndentManager(self):
            self.add_word("Assignments: ")
            with IndentManager(self):
                for assi in let_node.assignments:
                    assi.accept(self)
            self.add_word("Body: ")
            with IndentManager(self):
                let_node.body.accept(self)
        return self.current
    
    def visit_while_node(self, while_node : WhileNode):
        self.add_word("While ")
        with IndentManager(self):
            self.add_word("Condition ")
            with IndentManager(self):
                while_node.condition.accept(self)
            self.add_word("Body ")
            with IndentManager(self):
                while_node.body.accept(self)
        return self.current
    
    def visit_if_node(self, if_node : IfNode):
        self.add_word("If ")
        with IndentManager(self):
            for (condition, body) in if_node.body:
                self.add_word("Condition ")
                with IndentManager(self):
                    condition.accept(self)
                self.add_word("Body ")
                with IndentManager(self):
                    body.accept(self)
            self.add_word("Else ")
            with IndentManager(self):
                if_node.elsebody.accept(self)
        return self.current
    
    def visit_explicit_vector_node(self, explicit_vector_node : ExplicitVectorNode):
        self.add_word("Explicit Vector ")
        with IndentManager(self):
            self.add_word("Elements ")
            for element in explicit_vector_node.items:
                element.accept(self)
        return self.current
    
    def visit_implicit_vector_node(self, implicit_vector_node : ImplicitVectorNode):
        self.add_word("Implicit Vector " + implicit_vector_node.target.lexeme)
        with IndentManager(self):
            self.add_word("Iterable ")
            with IndentManager(self):
                implicit_vector_node.iterable.accept(self)
            self.add_word("Result ")
            with IndentManager(self):
                implicit_vector_node.result.accept(self)
        return self.current
    
    def visit_destructor_node(self, destructor_node : DestructorNode):
        self.add_word("Destructor " + destructor_node.id.lexeme)
        self.add_word("To")
        with IndentManager(self):
            destructor_node.expr.accept(self)
        return self.current
            
    def visit_block_node(self, block_node : BlockNode):
        self.add_word("Block")
        self.add_word("{")
        with IndentManager(self):
            for statement in block_node.exprs:
                statement.accept(self)
        self.add_word("}")
        return self.current
        
    def visit_call_node(self, call_node : CallNode):
        self.add_word("Call to ")
        with IndentManager(self):
            call_node.callee.accept(self)
            self.add_word("With Args: ")
            with IndentManager(self):
                for arg in call_node.args:
                    arg.accept(self)
        return self.current

    def visit_get_node(self, get_node : GetNode):
        self.add_word("Get Node")
        with IndentManager(self):
            self.add_word("With Left Part: ")
            get_node.left.accept(self)
            self.add_word("At ID: " + get_node.id.lexeme)
        return self.current
        
    def visit_set_node(self, set_node : SetNode):
        self.add_word("Set Node")
        with IndentManager(self):
            self.add_word("With Left Part: ")
            set_node.left.accept(self)
            self.add_word("At ID: " + set_node.id.lexeme)
            self.add_word("Assigning Value: ")
            set_node.value.accept(self)
        return self.current
    
    def visit_vector_set_node(self, vector_set_node : VectorSetNode):
        self.add_word("Vector Set")
        with IndentManager(self):
            self.add_word("At Position: ")
            vector_set_node.left.accept(self)
            self.add_word("With Index: ")
            with IndentManager(self):
                vector_set_node.index.accept(self)
            with IndentManager(self):
                self.add_word("Assigning Value: ")
            vector_set_node.value.accept(self)
        return self.current    

    def visit_vector_get_node(self, vector_get_node : VectorGetNode):
        self.add_word("Vector Get")
        with IndentManager(self):
            self.add_word("At Position: ")
            vector_get_node.left.accept(self)
            self.add_word("With Index: ")
            vector_get_node.index.accept(self)
        return self.current
    
    def visit_new_node(self, new_node : NewNode):
        self.add_word("New " + new_node.id.lexeme)
        with IndentManager(self):
            self.add_word("Args: ")
            for arg in new_node.args:
                arg.accept(self)
        return self.current

    def visit_binary_node(self, binary_node : BinaryNode):
        self.add_word("BinaryNode: " + binary_node.op.lexeme)
        with IndentManager(self):
            binary_node.left.accept(self)
            binary_node.right.accept(self)
        return self.current
    
    def visit_literal_node(self, literal_node : LiteralNode):
        self.add_word("Literal: " + literal_node.id.lexeme)
        return self.current

    def visit_unary_node(self, unary_node: UnaryNode):
        self.add_word("Unary: " + unary_node.op.lexeme)
        self.add_word("Expr: ")
        with IndentManager(self):
            unary_node.expr.accept(self)
        return self.current