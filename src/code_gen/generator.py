from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, VectorGetNode, VectorSetNode, WhileNode
from common.ast_nodes.statements import AttributeNode, MethodNode, ProgramNode, ProtocolNode, SignatureNode, TypeNode
from common.visitor import Visitor


WORD_SIZE = 4

class GenerationResult:
    def __init__(self, code : str, type : str = None) -> None:
        self.code = code
        self.type = type

class Generator(Visitor):
    def __init__(self, resolver : Resolver) -> None:
        self._resolver = resolver
        
        self._on_function_block = False
        self._func_name : str = None

        self._literal_strings : list[str] = []
        self._literal_numbers : list[str] = []
        self._if_index = 0
        self._while_index = 0

    def generate(self, program : ProgramNode) -> str:
        result = self._generate(program)
        return result.code
    
    def visit_program_node(self, program_node: ProgramNode):
        code = '''
.text
# j main # Simulation code
'''
        for decl in program_node.decls:
            code += self._generate(decl).code

        static_data_code = '''
.data
'''
        # Add static data
        i = 0
        for str_literal in self._literal_strings:
            static_data_code += f'str{i}: .asciiz "\\n{str_literal}\\n" \n' 
            i += 1

        i = 0
        for number_literal in self._literal_numbers:
            static_data_code += f'number{i}: .float {number_literal} \n' 
            i += 1
        static_data_code += '\n'

        return GenerationResult(static_data_code + code)
    
    def visit_method_node(self, method_node: MethodNode) -> GenerationResult:
        func_name = method_node.id.lexeme

        self._func_name = func_name
        self._resolver.start(func_name)
        stack_size = self._resolver.var_count * WORD_SIZE + 2 * WORD_SIZE

        code = f'''
{func_name}:
    addi $sp $sp -{stack_size}
    sw $ra 4($sp)
'''
        
        if func_name == 'main':
            code += '''
    jal stack_initialize
'''
        
        self._on_function_block = True
        result = self._generate(method_node.body)
        code += result.code

        code += f'''
    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp {stack_size}
    jr $ra
'''
        
        if func_name == 'main':
            code += '''    
    # j done # Simulation code
    \n
'''
        return GenerationResult(code, result.type)
    
    def visit_block_node(self, block_node: BlockNode):
        code = ''
        type = None

        for expr in block_node.exprs:
            result = self._generate(expr)
            code += result.code
            type = result.type

        return GenerationResult(code, type)
    
    def visit_let_node(self, let_node: LetNode):
        self._next_context() # Move to next context, since it's a let-node

        code = ''
        for assignment in let_node.assignments:
            var_name = assignment.id.lexeme
            value = assignment.body
            offset = self._get_offset(var_name)

            result = self._generate(value)
            code += result.code

            # Update variable's type (Assuming type-checking has been correctly done previously)
            # It would be better if type were resolved previously (during type-checking)
            self._resolver.resolve(var_name).type = result.type

            if result.type != 'number':
                code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
            else:
                code += f'''
    jal stack_pop
    swc1 $f0 {offset}($sp)
'''
        result = self._generate(let_node.body)
        code += result.code
        type = result.type

        return GenerationResult(code, type)

    def visit_destructor_node(self, destructor_node: DestructorNode):
        var_name = destructor_node.id.lexeme
        offset = self._get_offset(var_name)

        # We won't update type since we're assuming type-checking was already performed
        result = self._generate(destructor_node.expr)
        code = result.code
        
        if result.type != 'number':
            code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
    move $a0 $v0
    jal stack_push
'''
        else:
            code += f'''
    jal stack_pop
    swc1 $f0 {offset}($sp)
    mov.s $f12 $f0
    jal stack_push_number
'''

        return GenerationResult(code, result.type)

    def visit_call_node(self, call_node: CallNode):
        code = ''
        arg_types = []
        # We won't verify that length of args match length of params, previous semantic analysis assumed
        i = 1
        for arg in call_node.args:
            result = self._generate(arg)
            arg_types.append(result.type)
            code += result.code
            offset = -(i * WORD_SIZE)
            if result.type != 'number':
                code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''         
            else:
                code += f'''
    jal stack_pop
    swc1 $f0 {offset}($sp)
'''
            i += 1

        if isinstance(call_node.callee, LiteralNode):
            func_name = call_node.callee.id.lexeme

            # Handle print particular case
            if func_name == 'print':
                arg_type = arg_types[0]
                if arg_type == 'number':
                    func_name = 'print_number'
                elif arg_type == 'bool':
                    func_name = 'print_bool'
                elif arg_type == 'string':
                    func_name = 'print_str'
                else:
                    func_name = 'print_pointer'
                func_type = arg_type
            else:
                func_type = self._resolver.get_func_type(func_name)
            
            code += f'''
    jal {func_name}
'''
            if func_type != 'number':
                code += '''
    move $a0 $v0
    jal stack_push
'''
            else:
                code += '''
    mov.s $f12 $f0
    jal stack_push_number
'''
            return GenerationResult(code, func_type)
    
    def visit_literal_node(self, literal_node: LiteralNode):

        if literal_node.id.type == 'number':
            index = len(self._literal_numbers)
            number_literal = literal_node.id.lexeme

            if '.' not in number_literal:
                number_literal += '.0'

            self._literal_numbers.append(number_literal)
            code = f'''
    lwc1 $f12 number{index}
    jal stack_push_number
'''         
            return GenerationResult(code, 'number')
        
        elif literal_node.id.type == 'id':
            var_name = literal_node.id.lexeme
            offset = self._get_offset(var_name)
            type = self._resolver.resolve(var_name).type

            if type != 'number':
                code = f'''
    lw $a0 {offset}($sp)
    jal stack_push
'''
            else:
                code = f'''
    lwc1 $f12 {offset}($sp)
    jal stack_push_number
'''
            return GenerationResult(code, type)
        
        elif literal_node.id.type == 'string':
            index = len(self._literal_strings)
            str_literal = literal_node.id.lexeme
            self._literal_strings.append(str_literal)
            code = f'''
    la $a0 str{index}
    jal stack_push            
'''
            return GenerationResult(code, 'string')
        
        elif literal_node.id.type == 'true':
            code = '''
    li $a0 1
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        elif literal_node.id.type == 'false':
            code = '''
    li $a0 0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        
    def visit_binary_node(self, binary_node: BinaryNode):
        left_result = self._generate(binary_node.left)
        right_result = self._generate(binary_node.right)
        left_type = left_result.type
        right_type = right_result.type

        code = left_result.code
        code += right_result.code
        code += '''
    jal stack_pop
    move $s0 $v0
    mov.s $f20 $f0
    jal stack_pop
    move $s1 $v0
    mov.s $f22 $f0
        '''

        # Addition
        if binary_node.op.type == 'plus':
            code += '''
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal stack_push_number
            '''
            return GenerationResult(code, 'number')
        # Subtraction
        elif binary_node.op.type == 'minus':
            code += '''
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal stack_push_number
            '''
            return GenerationResult(code, 'number')
        # Multiplication
        elif binary_node.op.type == 'star':
            code +='''
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal stack_push_number
            '''
            return GenerationResult(code, 'number')
        # Division
        elif binary_node.op.type == 'div':
            code +='''
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal stack_push_number
            '''
            return GenerationResult(code, 'number')
        # GreaterThan
        elif binary_node.op.type == 'greater':
            code +='''
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal stack_push
            '''
            return GenerationResult(code, 'bool')
        # LessThan
        elif binary_node.op.type == 'less':
            code +='''
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal stack_push
            '''
            return GenerationResult(code, 'bool')
        # GreaterThanOrEqual
        elif binary_node.op.type == 'greaterEq':
            code +='''
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal stack_push
            '''
            return GenerationResult(code, 'bool')
        # LessThanOrEqual
        elif binary_node.op.type == 'lessEq':
            code +='''
    li $a0 0
    li $t0 1
    c.le.s $f22 $f20
    movt $a0 $t0 0
    jal stack_push
            '''
            return GenerationResult(code, 'bool')
        # DoubleEqual
        elif binary_node.op.type == 'doubleEqual':
            if left_type == 'number':
                code +='''
    li $a0 0
    li $t0 1
    c.eq.s $f22 $f20
    movt $a0 $t0 0
    jal stack_push
                '''
            else:
                code += '''
    seq $s0 $s0 $s1
    move $a0 $s0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        # NotEqual
        elif binary_node.op.type == 'notEqual':
            if left_type == 'number':
                code +='''
    li $a0 1
    c.eq.s $f22 $f20
    movt $a0 $zero 0
    jal stack_push
            '''
            else:
                code +='''
    seq $s0 $s0 $s1
    seq $s0 $s0 0
    move $a0 $s0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        # String concatenation
        elif binary_node.op.type == 'at' or binary_node.op.type == 'doubleAt':
            if left_type == 'number':
                code +='''
    mov.s $f12 $f20
    jal number_to_str
    move $s0 $v0 
            '''
            elif left_type == 'bool':
                code +='''
    move $a0 $s0
    jal bool_to_str
    move $s0 $v0
'''
            elif left_type != 'string':
                code +='''
    move $a0 $s0
    jal pointer_to_str
    move $s0 $v0
'''
            if right_type == 'number':
                code +='''
    mov.s $f12 $f22
    jal number_to_str
    move $s1 $v0 
            '''
            elif right_type == 'bool':
                code +='''
    move $a0 $s1
    jal bool_to_str
    move $s1 $v0
'''
            elif right_type != 'string':
                code +='''
    move $a0 $s1
    jal pointer_to_str
    move $s1 $v0
'''
            if binary_node.op.type == 'at':
                code += '''
    move $a0 $s0
    move $a1 $s1
    jal str_concat
    move $a0 $v0
    jal stack_push
'''
            else:
                code += '''
    move $a0 $s0
    move $a1 $s1
    jal str_space_concat
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'string')
        # Power
        elif binary_node.op.type == 'powerOp' or binary_node.op.type == 'modOp':
            if binary_node.op.type == 'powerOp':
                code +='''
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal power
    mov.s $f12 $f0
    jal stack_push_number
'''
            else:
                code +='''
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal mod
    mov.s $f12 $f0
    jal stack_push_number
'''
            return GenerationResult(code, 'number')
        else:
            raise Exception("Invalid operation")

    def visit_type_node(self, type_node: TypeNode):
        pass

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        pass

    def visit_signature_node(self, signature_node: SignatureNode):
        pass
    
    def visit_if_node(self, if_node: IfNode):
        types : list[str] = []
        code = ''
        i = 0
        for condition, expr in if_node.body:
            condition_result = self._generate(condition)

            if i > 0:
                code += f'''
    conditional_{self._if_index}_{i - 1}_{self._func_name}:
'''
            code += condition_result.code
            code += f'''
    jal stack_pop
'''
            if i < len(if_node.body) - 1:
                code += f'''
    bne $v0 1 conditional_{self._if_index}_{i}_{self._func_name}
'''
            else:
                code += f'''
    bne $v0 1 conditional_else_{self._if_index}_{self._func_name}
'''
            
            expr_result = self._generate(expr)
            code += expr_result.code
            types.append(expr_result.type)
            code += f'''
    j conditional_end_{self._if_index}_{self._func_name}
'''
            i += 1

        code += f'''
    conditional_else_{self._if_index}_{self._func_name}:
'''
        else_result = self._generate(if_node.elsebody)
        code += else_result.code
        types.append(else_result.type)

        code += f'''
    conditional_end_{self._if_index}_{self._func_name}:
'''

        self._if_index += 1

        # Check return type
        base_type = types[0]
        for type in types:
            if type != base_type:
                return GenerationResult(code, 'object')
        
        return GenerationResult(code, base_type)


    def visit_while_node(self, while_node: WhileNode):
        code = ''
        condition_result = self._generate(while_node.condition)
        code += condition_result.code
        code += f'''
    jal stack_pop
    bne $v0 1 while_end_{self._while_index}
    j while_body_{self._while_index}
    while_start_{self._while_index}:
'''
        code += condition_result.code
        code += f'''
    jal stack_pop
    bne $v0 1 while_end_{self._while_index}
    jal stack_pop
    while_body_{self._while_index}:
'''
        body_result = self._generate(while_node.body)
        code += body_result.code
        code += f'''
    j while_start_{self._while_index}
    while_end_{self._while_index}:
'''
        self._while_index += 1

        return GenerationResult(code, body_result.type)

    def visit_for_node(self, for_node: ForNode):
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
    
    def _generate(self, stmt : Statement) -> GenerationResult:
        return stmt.accept(self)
        
    def _get_offset(self, var_name: str) -> int:
        return ((self._resolver.var_count + 2) * WORD_SIZE) - ((self._resolver.resolve(var_name).index + 1) * WORD_SIZE)
    
    def _next_context(self):
        if not self._on_function_block:
            self._resolver.next()
        else:
            self._on_function_block = False