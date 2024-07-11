from common.ast_nodes.base import Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, UnaryNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.graph import Graph
from common.token_class import Token
from common.visitor import Visitor
from common.ErrorLogger import Error

class TypeConstructorData:
    def __init__(self, params : list[tuple[Token, Token]], method : MethodNode) -> None:
        self.params = params
        self.method = method

class ConstructorBuilder(Visitor):
    def __init__(self) -> None:
        self._type_graph = Graph()
        self._root_types : list[str] = []
        self._type_constructors : dict[str, TypeConstructorData] = {}
        self._errors = []

    def build(self, program : ProgramNode): 
        self._build(program)
        self._handle_inheritance()
        return self._errors

    def visit_program_node(self, program_node: ProgramNode):
        for decl in program_node.decls:
            self._build(decl)

    def visit_type_node(self, type_node: TypeNode):
        type_name = type_node.id.lexeme

        for method in type_node.methods:
            method_name = method.id.lexeme

            if method_name == 'build':
                self._type_constructors[type_name] = TypeConstructorData([] + method.params, method)

        if type_node.ancestor_id != None:
            ancestor = type_node.ancestor_id.lexeme
            self._type_graph.add((ancestor, type_name))
        else:
            if type_name not in self._type_graph.vertices:
                self._type_graph.add_vertex(type_name)
            self._root_types.append(type_name)
    
    def visit_method_node(self, method_node: MethodNode):
        pass

    def visit_let_node(self, let_node: LetNode):
        pass

    def visit_block_node(self, block_node: BlockNode):
        pass 

    def visit_destructor_node(self, destructor_node: DestructorNode):
        pass

    def visit_binary_node(self, binary_node: BinaryNode):
        pass     

    def visit_call_node(self, call_node: CallNode):
        pass

    def visit_unary_node(self, unary_node : UnaryNode):
        pass

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        pass

    def visit_signature_node(self, signature_node: SignatureNode):
        pass
    
    def visit_if_node(self, if_node: IfNode):
        pass

    def visit_while_node(self, while_node: WhileNode):
        pass

    def visit_new_node(self, new_node: NewNode):
        pass
    
    def visit_get_node(self, get_node: GetNode):
        pass

    def visit_set_node(self, set_node: SetNode):
        pass

    def visit_explicit_vector_node(self, explicit_vector_node: ExplicitVectorNode):
        pass

    def visit_implicit_vector_node(self, implicit_vector_node: ImplicitVectorNode):
        pass

    def visit_vector_get_node(self, vector_get_node: VectorGetNode):
        pass

    def visit_vector_set_node(self, vector_set_node: VectorSetNode):
        pass

    def visit_literal_node(self, literal_node: LiteralNode):
        pass

    def _build(self, stmt: Statement):
        return stmt.accept(self)
    
    def _handle_inheritance(self):
        if self._type_graph.is_cyclic():
            self._errors.append(Error(f"Can't have cyclic inheritance in types {self._type_graph.cyclic_edge[0]} and {self._type_graph.cyclic_edge[1]}", 0, 0))
            return
        
        stack : list[str] = [] + self._root_types
        graph = self._type_graph
        
        while(len(stack) > 0):
            vertex = stack.pop()
            neighbors = graph.neighbors(vertex)

            for neighbor in neighbors:
                # Update constructor params to descendant types
                if len(self._type_constructors[neighbor].params) == 0 and len(self._type_constructors[vertex].params) > 0:
                    params = self._type_constructors[vertex].params
                    method = self._type_constructors[neighbor].method

                    if isinstance(method.body, BlockNode):
                        self._type_constructors[neighbor].params = [] + params
                        method.params = [] + params
                        method.body.exprs = [
                            CallNode(
                                LiteralNode(
                                    Token('id', 'base')
                                ),
                                [LiteralNode(id) for id, _ in params]
                            )
                        ] + method.body.exprs[1:]
                
                # Push onto stack
                stack.append(neighbor)