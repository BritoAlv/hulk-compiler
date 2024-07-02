.data
vector_str0: .asciiz "Error: Index was outside of the bounds of the vector" 
vector_number0: .float 0.0 
vector_number1: .float 0.0 
vector_number2: .float 0.0 
vector_number3: .float 1.0 
vector_number4: .float 0.0 
vector_number5: .float 1.0 
vector_number6: .float 0.0 
vector_number7: .float 0.0 
vector_number8: .float 1.0 
vector_number9: .float 1.0 
vector_number10: .float 0.0 
vector_number11: .float 1.0 


.text
.globl build_Vector
.globl length_Vector
.globl append_Vector
.globl getNodeAt_Vector
.globl element_Vector
.globl set_Vector
.globl current_Vector
.globl next_Vector
# .globl done # Simulation code

build_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lwc1 $f12 vector_number0
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lwc1 $f12 vector_number1
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 20($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

length_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

append_Vector:
    addi $sp $sp -20
    sw $ra 4($sp)

    li $a0 16
    li $v0 9
    syscall
    li $t0 5
    sw $t0 ($v0) # Store type metadata
    move $a0 $v0
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    sw $v0 -4($sp)

    jal build_Node
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $t0 16($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 vector_number2
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.eq.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
                
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_0_append_Vector

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    j conditional_end_0_append_Vector

    conditional_else_0_append_Vector:

    lw $a0 8($sp)
    jal stack_push

    lw $t0 16($sp)
    lw $a0 8($t0)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setPrevious_Node
    move $a0 $v0
    jal stack_push
    call_end_setPrevious_0:

    jal stack_pop

    lw $t0 16($sp)
    lw $a0 8($t0)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setNext_Node
    move $a0 $v0
    jal stack_push
    call_end_setNext_1:

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 16($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    conditional_end_0_append_Vector:

    jal stack_pop

    lw $t0 16($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 vector_number3
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 16($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 20
    jr $ra

getNodeAt_Vector:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 16($sp)
    jal stack_push

    lwc1 $f12 vector_number4
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    lw $a0 16($sp)
    jal stack_push

    lw $t0 20($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.lt.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add $s0 $s0 $s1
    sgt $s0 $s0 $zero
    beq $s0 1 or_true_0
    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
    j or_end_0
    or_true_0:
    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push
    or_end_0:

    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_1_getNodeAt_Vector

    la $a0 vector_str0
    jal build_str
    move $a0 $v0
    jal stack_push            

    jal stack_pop
    sw $v0 -4($sp)

    jal error

    move $a0 $v0
    jal stack_push

    j conditional_end_1_getNodeAt_Vector

    conditional_else_1_getNodeAt_Vector:

    lwc1 $f12 vector_number5
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    lwc1 $f12 4($v0)
    neg.s $f12 $f12
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)

    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_0
    j while_body_0
    while_start_0:

    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_0
    jal stack_pop
    while_body_0:

    lwc1 $f12 vector_number6
    jal build_number
    move $a0 $v0
    jal stack_push

    j while_start_0
    while_null_end_0:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_0:

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 12($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
     
    bne $t0 1 while_null_end_1
    j while_body_1
    while_start_1:

    lw $a0 12($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)
    bne $t0 1 while_end_1
    jal stack_pop
    while_body_1:

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 vector_number7
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 0
    li $t0 1
    c.lt.s $f22 $f20
    movt $a0 $t0 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_2_getNodeAt_Vector

    lw $t0 20($sp)
    lw $a0 4($t0)
    jal stack_push

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    j conditional_end_2_getNodeAt_Vector

    conditional_else_2_getNodeAt_Vector:

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNext_Node
    move $a0 $v0
    jal stack_push
    call_end_getNext_2:

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)
    jal stack_push
    
    conditional_end_2_getNodeAt_Vector:

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    lwc1 $f12 vector_number8
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    move $a0 $v0
    sw $a0 12($sp)
    jal stack_push
    
    jal stack_pop

    lw $a0 8($sp)
    jal stack_push

    j while_start_1
    while_null_end_1:
    jal build_null
    move $a0 $v0
    jal stack_push
    while_end_1:

    conditional_end_1_getNodeAt_Vector:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra

element_Vector:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 12($sp)
    jal stack_push

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNodeAt_Vector
    move $a0 $v0
    jal stack_push
    call_end_getNodeAt_3:

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getValue_Node
    move $a0 $v0
    jal stack_push
    call_end_getValue_4:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

set_Vector:
    addi $sp $sp -24
    sw $ra 4($sp)

    lw $a0 20($sp)
    jal stack_push

    lw $a0 16($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal getNodeAt_Vector
    move $a0 $v0
    jal stack_push
    call_end_getNodeAt_5:

    jal stack_pop
    move $a0 $v0
    sw $a0 8($sp)

    lw $a0 8($sp)
    jal stack_push

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal setValue_Node
    move $a0 $v0
    jal stack_push
    call_end_setValue_6:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 24
    jr $ra

next_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    lwc1 $f12 vector_number9
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    sub.s $f20 $f22 $f20
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    li $a0 1
    c.le.s $f22 $f20
    movt $a0 $zero 0
    jal build_bool
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 4($v0)

    bne $t0 1 conditional_else_3_next_Vector

    lwc1 $f12 vector_number10
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    li $a0 0
    jal build_bool
    move $a0 $v0
    jal stack_push

    j conditional_end_3_next_Vector

    conditional_else_3_next_Vector:

    lw $a0 8($sp)
    jal stack_push

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    jal stack_pop
    sw $v0 -8($sp)

    jal stack_pop
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    sw $v0 -4($sp)

    jal element_Vector
    move $a0 $v0
    jal stack_push
    call_end_element_7:

    jal stack_pop
    lw $t0 8($sp)
    sw $v0 20($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $t0 8($sp)
    lw $a0 16($t0)
    jal stack_push

    lwc1 $f12 vector_number11
    jal build_number
    move $a0 $v0
    jal stack_push

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s2 $v0 
    lw $s0 4($s2)
    lwc1 $f20 4($s2)

    jal stack_pop
    
    lw $t0 ($v0) # Check if null
    beq $t0 -1 null_error
    move $s3 $v0
    lw $s1 4($s3)
    lwc1 $f22 4($s3)
    
    add.s $f20 $f20 $f22
    mov.s $f12 $f20
    jal build_number
    move $a0 $v0
    jal stack_push
            
    jal stack_pop
    lw $t0 8($sp)
    sw $v0 16($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    li $a0 1
    jal build_bool
    move $a0 $v0
    jal stack_push

    conditional_end_3_next_Vector:

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

current_Vector:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 20($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

build_Node:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    jal build_null
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop

    lw $a0 12($sp)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

getValue_Node:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 4($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

setValue_Node:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 4($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

getNext_Node:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 12($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

getPrevious_Node:
    addi $sp $sp -12
    sw $ra 4($sp)

    lw $t0 8($sp)
    lw $a0 8($t0)
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 12
    jr $ra

setNext_Node:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 12($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

setPrevious_Node:
    addi $sp $sp -16
    sw $ra 4($sp)

    lw $a0 8($sp)
    jal stack_push

    jal stack_pop
    lw $t0 12($sp)
    sw $v0 8($t0)
    move $a0 $v0
    jal stack_push

    jal stack_pop
    lw $ra 4($sp)
    addi $sp $sp 16
    jr $ra

# done: # Simulation code