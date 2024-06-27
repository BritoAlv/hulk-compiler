from code_gen.resolver import Resolver
from common.ast_nodes.base import Statement
from common.ast_nodes.expressions import BinaryNode, BlockNode, CallNode, DestructorNode, ExplicitVectorNode, ForNode, GetNode, IfNode, ImplicitVectorNode, LetNode, LiteralNode, NewNode, SetNode, UnaryNode, VectorGetNode, VectorSetNode, WhileNode
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
        self._in_type = False
        self._func_name : str = None
        self._type_name : str = None

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
            static_data_code += f'str{i}: .asciiz {str_literal} \n' 
            i += 1

        i = 0
        for number_literal in self._literal_numbers:
            static_data_code += f'number{i}: .float {number_literal} \n' 
            i += 1
        static_data_code += '\n'

        return GenerationResult(static_data_code + code)
    
    def visit_method_node(self, method_node: MethodNode) -> GenerationResult:
        func_name = method_node.id.lexeme
        
        if self._in_type:
            func_name = f'{func_name}_{self._type_name}'

        self._func_name = func_name
        self._resolver.start(func_name)
        func_data = self._resolver.resolve_function_data(func_name)
        stack_size = func_data.var_count * WORD_SIZE + 2 * WORD_SIZE

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
        self._func_name = None # Restore to None since we're exiting the node
        return GenerationResult(code, result.type)
    
    def visit_block_node(self, block_node: BlockNode):
        code = ''
        type = None

        for i, expr in enumerate(block_node.exprs):
            result = self._generate(expr)
            code += result.code

            # Pop all the expression results previous to the last one
            if i < len(block_node.exprs) - 1:
                code += '''
    jal stack_pop
'''
            type = result.type

        return GenerationResult(code, type)
    
    def visit_let_node(self, let_node: LetNode):
        self._resolver.next() # Move to next context
        code = ''
        for assignment in let_node.assignments:
            var_name = assignment.id.lexeme
            value = assignment.body
            offset = self._get_offset(var_name)

            result = self._generate(value)
            code += result.code

            self._resolver.resolve_var_data(var_name).type = result.type # TODO: Remove when types are correctly inferred during semantic analysis

            if result.type == 'bool':
                code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_bool
    move $a0 $v0
    sw $a0 {offset}($sp)
        '''
            elif result.type == 'str':
                code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_str
    move $a0 $v0
    sw $a0 {offset}($sp)
        '''
            elif result.type == 'number':
                code += f'''
    jal stack_pop
    lwc1 $f12 4($v0)
    jal build_number
    move $a0 $v0
    sw $a0 {offset}($sp)
        '''
            else:
                code += f'''
    jal stack_pop
    move $a0 $v0
    sw $a0 {offset}($sp)
        '''
                
        result = self._generate(let_node.body)

        code += result.code
        type = result.type

        self._resolver.next() # Move to next context
        return GenerationResult(code, type)

    def visit_destructor_node(self, destructor_node: DestructorNode):
        var_name = destructor_node.id.lexeme
        offset = self._get_offset(var_name)

        # We won't update type since we're assuming type-checking was already performed
        result = self._generate(destructor_node.expr)
        code = result.code
        
        if result.type == 'bool':
            code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_bool
    move $a0 $v0
    sw $a0 {offset}($sp)
    jal stack_push
    '''
        elif result.type == 'string':
            code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_str
    move $a0 $v0
    sw $a0 {offset}($sp)
    jal stack_push
    '''
        elif result.type == 'number':
            code += f'''
    jal stack_pop
    lwc1 $f12 4($v0)
    jal build_number
    move $a0 $v0
    sw $a0 {offset}($sp)
    jal stack_push
    '''
        else:
            code += f'''
    jal stack_pop
    move $a0 $v0
    jal stack_push
    '''

        return GenerationResult(code, result.type)

    def visit_call_node(self, call_node: CallNode):
        # Function call
        if isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme != 'base':
            func_name = call_node.callee.id.lexeme
            code = ''
            arg_types = []

            # We won't verify that length of args match length of params, previous semantic analysis assumed
            i = 1
            for arg in call_node.args:
                result = self._generate(arg)
                arg_types.append(result.type)
                code += result.code
                offset = -(i * WORD_SIZE)
                code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
    '''         
                i += 1

            
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
                func_type = 'object'
            else:
                func_type = self._resolver.resolve_function_data(func_name).type
            
            code += f'''
    jal {func_name}
'''
            code += '''
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, func_type)
        # Method call
        else:

            if isinstance(call_node.callee, LiteralNode) and call_node.callee.id.lexeme == 'base':
                type_data = self._resolver.resolve_type_data(self._type_name)
                self_offset = self._get_offset('self')
                code = f'''
    lw $t0 {self_offset}($sp)
    sw $t0 {-WORD_SIZE}($sp)
    '''
                # Remove type name attached to method name
                func_name = self._func_name
                if self._in_type:
                    func_name = self._func_name[0 : self._func_name.rfind('_')]

                method_name = type_data.methods[func_name][1]
            elif isinstance(call_node.callee, GetNode):
                result = self._generate(call_node.callee)
                type_data = self._resolver.resolve_type_data(result.type)
                called_method = call_node.callee.id.lexeme

                code = result.code

                method_name = type_data.methods[called_method][0]
                code += f'''
    jal stack_pop
    sw $v0 {-WORD_SIZE}($sp)
'''         
            else:
                raise Exception("Functions are not a type here, cannot be called that way")
                
            i = 2
            for arg in call_node.args:
                result = self._generate(arg)
                code += result.code
                offset = -(i * WORD_SIZE)
                code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
    '''         
                i += 1
            
            code += f'''
    jal {method_name}
    move $a0 $v0
    jal stack_push
'''
            func_data = self._resolver.resolve_function_data(method_name)
            return GenerationResult(code, func_data.type)
    
    def visit_literal_node(self, literal_node: LiteralNode):

        if literal_node.id.type == 'number':
            index = len(self._literal_numbers)
            number_literal = literal_node.id.lexeme

            if '.' not in number_literal:
                number_literal += '.0'

            self._literal_numbers.append(number_literal)
            code = f'''
    lwc1 $f12 number{index}
    jal build_number
    move $a0 $v0
    jal stack_push
'''         
            return GenerationResult(code, 'number')
        
        elif literal_node.id.type == 'id':
            var_name = literal_node.id.lexeme
            offset = self._get_offset(var_name)
            type = self._resolver.resolve_var_data(var_name).type

            code = f'''
    lw $a0 {offset}($sp)
    jal stack_push
'''
            return GenerationResult(code, type)
        
        elif literal_node.id.type == 'string':
            index = len(self._literal_strings)
            str_literal = literal_node.id.lexeme
            self._literal_strings.append(str_literal)
            code = f'''
    la $a0 str{index}
    jal build_str
    move $a0 $v0
    jal stack_push            
'''
            return GenerationResult(code, 'string')
        
        elif literal_node.id.type == 'true':
            code = '''
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        elif literal_node.id.type == 'false':
            code = '''
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        elif literal_node.id.type == 'self':
            offset = self._get_offset('self')
            code = f'''
    lw $a0 {offset}($sp)
    jal stack_push
'''
            return GenerationResult(code, self._type_name)
        
    def visit_binary_node(self, binary_node: BinaryNode):
        left_result = self._generate(binary_node.left)

        if binary_node.op.type == 'isOp' and isinstance(binary_node.right, LiteralNode) and binary_node.right.id.type == 'id':
            type_name = binary_node.right.id.lexeme
            type_id = self._resolver.resolve_type_data(type_name).id
            
            code = left_result.code
            code += f'''
    jal stack_pop
    lw $s0 ($v0)
    li $s1 {type_id}
    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        elif binary_node.op.type == 'asOp' and isinstance(binary_node.right, LiteralNode) and binary_node.right.id.type == 'id':
            type_name = binary_node.right.id.lexeme

            try:
                self._resolver.resolve_type_data(type_name)            
            except:
                raise Exception(f'Type {type_name} is not defined')

            return GenerationResult(left_result.code, type_name)

        right_result = self._generate(binary_node.right)
        left_type = left_result.type
        right_type = right_result.type

        code = left_result.code
        code += right_result.code
        code += '''
    jal stack_pop
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
        '''

        # Addition
        if binary_node.op.type == 'plus':
            code += '''
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        # Subtraction
        elif binary_node.op.type == 'minus':
            code += '''
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        # Multiplication
        elif binary_node.op.type == 'star':
            code +='''
    mul.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        # Division
        elif binary_node.op.type == 'div':
            code +='''
    div.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'number')
        # Logical And and Or
        elif binary_node.op.type == 'and' or binary_node.op.type == 'or':
            if binary_node.op.type == 'and':
                code +='''
    add $s0 $s0 $s1
    beq $s0 2 and_true
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j and_end
    and_true:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    and_end:
            '''
            else:    
                code += '''
    add $s0 $s0 $s1
    sgt $s0 $s0 $zero
    beq $s0 1 or_true
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j or_end
    or_true:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    or_end:
'''
            return GenerationResult(code, 'bool')
        # GreaterThan
        elif binary_node.op.type == 'greater':
            code +='''
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
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
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            return GenerationResult(code, 'bool')
        # GreaterThanOrEqual
        elif binary_node.op.type == 'greaterEq':
            code +='''
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
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
    jal build_bool
    move $a0 $v0
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
    jal build_bool
    move $a0 $v0
    jal stack_push
                '''
            else:
                code += '''
    seq $s0 $s0 $s1
    move $a0 $s0
    jal build_bool
    move $a0 $v0
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
    jal build_bool
    move $a0 $v0
    jal stack_push
            '''
            else:
                code +='''
    seq $s0 $s0 $s1
    seq $s0 $s0 0
    move $a0 $s0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        # String concatenation
        elif binary_node.op.type == 'at' or binary_node.op.type == 'doubleAt':
            if right_type == 'number':
                code +='''
    mov.s $f12 $f20
    jal number_to_str
    move $s0 $v0 
            '''
            elif right_type == 'bool':
                code +='''
    move $a0 $s0
    jal bool_to_str
    move $s0 $v0
'''
            elif right_type != 'string':
                code +='''
    move $a0 $s0
    jal pointer_to_str
    move $s0 $v0
'''
            if left_type == 'number':
                code +='''
    mov.s $f12 $f22
    jal number_to_str
    move $s1 $v0 
            '''
            elif left_type == 'bool':
                code +='''
    move $a0 $s1
    jal bool_to_str
    move $s1 $v0
'''
            elif left_type != 'string':
                code +='''
    move $a0 $s1
    jal pointer_to_str
    move $s1 $v0
'''
            if binary_node.op.type == 'at':
                code += '''
    move $a0 $s1
    move $a1 $s0
    jal str_concat
    move $a0 $v0
    jal build_str
    move $a0 $v0
    jal stack_push
'''
            else:
                code += '''
    move $a0 $s1
    move $a1 $s0
    jal str_space_concat
    move $a0 $v0
    jal build_str
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
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            else:
                code +='''
    mov.s $f12 $f22
    mov.s $f14 $f20
    jal mod
    mov.s $f12 $f0
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'number')
        else:
            raise Exception("Invalid operation")

    def visit_type_node(self, type_node: TypeNode):
        self._type_name = type_node.id.lexeme
        self._in_type = True

        code = ''
        for method in type_node.methods:
            code += self._generate(method).code

        self._type_name = None # Restore to None since we're exiting the node
        self._in_type = False # Restore to False since we're exiting the node
        return GenerationResult(code)

    def visit_protocol_node(self, protocol_node: ProtocolNode):
        pass

    def visit_attribute_node(self, attribute_node: AttributeNode):
        attribute_name = attribute_node.id.lexeme
        result = self._generate(attribute_node.body)
        code = result.code

        type_data = self._resolver.resolve_type_data(self._type_name)
        type_data.attributes[attribute_name].type = result.type # TODO: Remove when types are correctly inferred during semantic analysis

        self_offset = self._get_offset('self')
        attribute_offset = (type_data.attributes[attribute_name].index + type_data.inherited_offset) * WORD_SIZE

        if result.type == 'bool':
                code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_bool
        
        '''
        elif result.type == 'str':
            code += f'''
    jal stack_pop
    lw $a0 4($v0)
    jal build_str
        '''
        elif result.type == 'number':
            code += f'''
    jal stack_pop
    lwc1 $f12 4($v0)
    jal build_number
        '''
        else:
            code += f'''
    jal stack_pop
        '''
            
        code += f'''
    lw $t0 {self_offset}($sp)
    sw $v0 {attribute_offset}($t0)
    move $a0 $v0
    jal stack_push
'''

        return GenerationResult(code)

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
    lw $t0 4($v0)
'''
            if i < len(if_node.body) - 1:
                code += f'''
    bne $t0 1 conditional_{self._if_index}_{i}_{self._func_name}
'''
            else:
                code += f'''
    bne $t0 1 conditional_else_{self._if_index}_{self._func_name}
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
    lw $t0 4($v0)
    move $v0 $zero # Set default while-value to zero
     
    bne $t0 1 while_end_{self._while_index}
    j while_body_{self._while_index}
    while_start_{self._while_index}:
'''
        code += condition_result.code
        code += f'''
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_{self._while_index}
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
        type_name = new_node.id.lexeme
        type_data = self._resolver.resolve_type_data(type_name)
        type_size = type_data.inherited_offset + len(type_data.attributes)
        type_id = type_data.id

        code = f'''
    li $a0 {type_size * WORD_SIZE}
    li $v0 9
    syscall
    sw $v0 {-WORD_SIZE}($sp)
    li $t0 {type_id}
    sw $t0 ($v0)
'''
        
        i = 2
        for arg in new_node.args:
            result = self._generate(arg)
            code += result.code
            offset = -(i * WORD_SIZE)
            code += f'''
    jal stack_pop
    sw $v0 {offset}($sp)
'''
            i += 1
        code += f'''
    jal build_{type_name}
    move $a0 $v0
    jal stack_push
'''
        return GenerationResult(code, type_name)
    
    def visit_unary_node(self, unary_node : UnaryNode):
        result = self._generate(unary_node.expr)
        code = result.code
        if unary_node.op.type == 'not':
            code += '''
    jal stack_pop
    lw $a0 4($v0)
    li $t0 0
    seq $a0 $a0 $t0
    jal build_bool
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'bool')
        else:
            code += '''
    jal stack_pop
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, 'number')
    
    def visit_get_node(self, get_node: GetNode):
        if isinstance(get_node.left, LiteralNode) and get_node.left.id.lexeme == 'self':
            type_data = self._resolver.resolve_type_data(self._type_name)
            if get_node.id.lexeme in type_data.attributes:
                var_data = type_data.attributes[get_node.id.lexeme]
                attribute_offset = (var_data.index + type_data.inherited_offset) * WORD_SIZE
                self_offset = self._get_offset('self')
                code = f'''
    lw $t0 {self_offset}($sp)
    lw $a0 {attribute_offset}($t0)
    jal stack_push
'''
                return GenerationResult(code, var_data.type)
        return self._generate(get_node.left)
                
    def visit_set_node(self, set_node: SetNode):
        if isinstance(set_node.left, LiteralNode) and set_node.left.id.lexeme == 'self':
            result = self._generate(set_node.value)
            code = result.code

            type_data = self._resolver.resolve_type_data(self._type_name)
            var_data = type_data.attributes[set_node.id.lexeme]
            self_offset = self._get_offset('self')
            attribute_offset = (var_data.index + type_data.inherited_offset) * WORD_SIZE
            code += f'''
    jal stack_pop
    lw $t0 {self_offset}($sp)
    sw $v0 {attribute_offset}($t0)
    move $a0 $v0
    jal stack_push
'''
            return GenerationResult(code, result.type)

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
        func_data = self._resolver.resolve_function_data(self._func_name)

        return ((func_data.var_count + 2) * WORD_SIZE) - ((self._resolver.resolve_var_data(var_name).index + 1) * WORD_SIZE)
