from freegames import vector
from common.ast_nodes.base import Expr, Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, UnaryNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.token_class import Token
from common.visitor import Visitor


class VectorModifier(Visitor):

    def replace(self, expr : Statement):
        if isinstance(expr, ImplicitVectorNode):
            return self.ModifyImplicit(expr)
        if isinstance(expr, ExplicitVectorNode):
            return self.ModifyExplicit(expr)
        return expr

    def visit_attribute_node(self, attribute_node: AttributeNode):
        attribute_node.body = self.replace(attribute_node.body)
        attribute_node.body.accept(self)

    def visit_binary_node(self, binary_node: BinaryNode):
        binary_node.left = self.replace(binary_node.left)
        binary_node.left.accept(self)

        binary_node.right = self.replace(binary_node.right)
        binary_node.right.accept(self)

    def visit_unary_node(self, unary_node: UnaryNode):
        unary_node.expr = self.replace(unary_node.expr)
        unary_node.expr.accept(self)

    def visit_block_node(self, block_node: BlockNode):
        for i in range(0, len(block_node.exprs)):
            block_node.exprs[i] = self.replace(block_node.exprs[i])
            block_node.exprs[i].accept(self)

    def visit_call_node(self, call_node: CallNode):
        call_node.callee = self.replace(call_node.callee)
        call_node.callee.accept(self)
        for i in range(0, len(call_node.args)):
            call_node.args[i] = self.replace(call_node.args[i])
            call_node.args[i].accept(self)

    def visit_destructor_node(self, destructor_node: DestructorNode):
        destructor_node.expr = self.replace(destructor_node.expr)
        destructor_node.expr.accept(self)

    def visit_implicit_vector_node(self, implicit_vector_node: ImplicitVectorNode):
        implicit_vector_node.iterable = self.replace(implicit_vector_node.iterable)
        implicit_vector_node.iterable.accept(self)

        implicit_vector_node.result = self.replace(implicit_vector_node.result)
        implicit_vector_node.result.accept(self)

    def visit_let_node(self, let_node: LetNode):
        for i in range(0, len(let_node.assignments)):
            let_node.assignments[i] = self.replace(let_node.assignments[i])
            let_node.assignments[i].accept(self)
        let_node.body = self.replace(let_node.body)
        let_node.body.accept(self)

    def visit_literal_node(self, literal_node: LiteralNode):
        pass

    def visit_new_node(self, new_node: NewNode):
        for i in range(0, len(new_node.args)):
            new_node.args[i] = self.replace(new_node.args[i])
            new_node.args[i].accept(self)
    
    def visit_while_node(self, while_node: WhileNode):
        while_node.condition = self.replace(while_node.condition)
        while_node.condition.accept(self)
        while_node.body = self.replace(while_node.body)
        while_node.body.accept(self)
    
    def visit_explicit_vector_node(self, explicit_vector_node: ExplicitVectorNode):
        for i in range(0, len(explicit_vector_node.items)):
            explicit_vector_node.items[i] = self.replace(explicit_vector_node.items[i])
            explicit_vector_node.items[i].accept(self)

    def visit_get_node(self, get_node: GetNode):
        get_node.left = self.replace(get_node.left)
        get_node.left.accept(self)

    def visit_if_node(self, if_node: IfNode):
        for i in range(0, len(if_node.body)):
            if_node.body[i] = (self.replace(if_node.body[i][0]), self.replace(if_node.body[i][1]))
            if_node.body[i][0].accept(self)
            if_node.body[i][1].accept(self)

        if_node.elsebody = self.replace(if_node.elsebody)
        if_node.elsebody.accept(self)

    def visit_method_node(self, method_node: MethodNode):
        method_node.body = self.replace(method_node.body)
        method_node.body.accept(self)
    
    def visit_program_node(self, program_node: ProgramNode):
        for i in range(0, len(program_node.decls)):
            program_node.decls[i] = self.replace(program_node.decls[i])
            program_node.decls[i].accept(self)
        return program_node
    
  
    def ModifyImplicit(self, implicit_vector_node : ImplicitVectorNode) -> LetNode:
        iter = implicit_vector_node.iterable
        result = implicit_vector_node.result
        target = implicit_vector_node.target
        return LetNode(
                    [
                        AttributeNode(
                            target,
                            LiteralNode(Token('null', 'null')),
                            Token('id', 'Object')),
                        AttributeNode(
                            Token('id', 'source'),
                            iter
                        ),
                        AttributeNode(
                            Token('id', 'target'),
                            NewNode(Token('id', 'Vector'), [])
                        )
                    ],
                    BlockNode(
                        [
                            WhileNode(
                                CallNode(
                                    GetNode(
                                        LiteralNode(Token('id', 'source')),
                                        Token('id', 'next')
                                    ),
                                    []
                                ),
                                BlockNode([
                                    DestructorNode(
                                        target,
                                        CallNode(
                                            GetNode(
                                                LiteralNode(Token('id', 'source')),
                                                Token('id', 'current')
                                            ),
                                            []
                                        )
                                    ),
                                    CallNode(
                                    GetNode(
                                        LiteralNode(Token('id', 'target')),
                                        Token('id', 'append')
                                    ),
                                    [result]
                                    ),
                                ]),
                            ),
                            LiteralNode(Token('id', 'target'))
                        ]
                    )
                )

    def ModifyExplicit(self, explicit_vector_node : ExplicitVectorNode) -> LetNode:
        expr_list : list[Expr] = []
        for expr in explicit_vector_node.items:
            expr_list.append(
                CallNode(
                    GetNode(
                        LiteralNode(
                            Token('id', 'vec')
                        ),
                        Token('id', 'append')
                    ),
                    [expr])
            )
        expr_list.append(LiteralNode(Token('id', 'vec')))
        node = LetNode(
            [
                AttributeNode(
                    Token('id', 'vec'),
                    NewNode(
                        Token('id', 'Vector'), 
                        [])
                ),
            ],
            BlockNode(expr_list)
        )
        return node
    
    def visit_protocol_node(self, protocol_node: ProtocolNode):
        for i in range(0, len(protocol_node.signatures)):
            protocol_node.signatures[i] = self.replace(protocol_node.signatures[i])
            protocol_node.signatures[i].accept(self)

    def visit_set_node(self, set_node: SetNode):
        set_node.left = self.replace(set_node.left)
        set_node.left.accept(self)
        set_node.value = self.replace(set_node.value)
        set_node.value.accept(self)

    def visit_signature_node(self, signature_node: SignatureNode):
        pass

    def visit_type_node(self, type_node: TypeNode):
        for i in range(0, len(type_node.methods)):
            type_node.methods[i] = self.replace(type_node.methods[i])
            type_node.methods[i].accept(self)
        
    def visit_vector_get_node(self, vector_get_node: VectorGetNode):
        vector_get_node.left = self.replace(vector_get_node.left)
        vector_get_node.left.accept(self)

        vector_get_node.index = self.replace(vector_get_node.index)
        vector_get_node.index.accept(self)

    def visit_vector_set_node(self, vector_set_node: VectorSetNode):
        vector_set_node.left = self.replace(vector_set_node.left)
        vector_set_node.left.accept(self)

        vector_set_node.index = self.replace(vector_set_node.index)
        vector_set_node.index.accept(self)

        vector_set_node.value = self.replace(vector_set_node.value)
        vector_set_node.value.accept(self)