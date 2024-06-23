.data
p_stack: .word 0 # Pointer to stack
stack_size: .word 10000 # First word of stack holds stack's size
stack_empty_msg: .asciiz "\nError, stack is empty\n"

.text
.globl stack_initialize
.globl stack_push
.globl stack_push_number
.globl stack_pop
# .globl done # Simulation code

stack_initialize:
	li $v0 9
	lw $a0 stack_size
	syscall
	sw $v0 p_stack # Store stack address
	
	# Set stack size equal to zero
	li $t0 0
	sw $t0 4($v0)
	jr $ra
	
stack_push:
	# Push
	addi $sp $sp -4
	sw $s0 4($sp)
	
	lw $s0 p_stack # Load stack address
	
	lw $t0 4($s0) # Load stack size
	lw $t1 stack_size
	beq $t0 $t1 stack_increase # Check if stack is full
	addi $t0 $t0 1 
	sw $t0 4($s0) # Increase stack size by one
	
	addi $t0 $t0 1 # Add one since the first position is occupied by the stack's size
	# Multiply by four (a word is 4 bytes)
	li $t1 4 
	mult $t0 $t1
	mflo $t0
	add $t0 $s0 $t0 # Add offset
	sw $a0 0($t0) # Push on the stack
	
	# Pop
	lw $s0 4($sp)
	addi $sp $sp 4
	jr $ra
	
	stack_increase: # TODO: Must be implemented (either throw an exception or make the stack grow dynamically)
	
	# Pop
	lw $s0 4($sp)
	addi $sp $sp 4
	jr $ra

stack_push_number:
	# Push
	addi $sp $sp -4
	sw $s0 4($sp)
	
	lw $s0 p_stack # Load stack address
	
	lw $t0 4($s0) # Load stack size
	lw $t1 stack_size
	beq $t0 $t1 stack_increase # Check if stack is full
	addi $t0 $t0 1 
	sw $t0 4($s0) # Increase stack size by one
	
	addi $t0 $t0 1 # Add one since the first position is occupied by the stack's size
	# Multiply by four (a word is 4 bytes)
	li $t1 4 
	mult $t0 $t1
	mflo $t0
	add $t0 $s0 $t0 # Add offset
	swc1 $f12 0($t0) # Push on the stack
	
	# Pop
	lw $s0 4($sp)
	addi $sp $sp 4
	jr $ra
	
	
	# Pop
	lw $s0 4($sp)
	addi $sp $sp 4
	jr $ra
	
stack_pop:
	#Push
	addi $sp $sp -4
	sw $s0 4($sp)
	
	lw $s0 p_stack # Load stack address
	lw $t0 4($s0) # Load stack size
	
	beq $t0 $zero stack_empty_error
	move $t2 $t0 # Store stack size
	addi $t0 $t0 1 # Add one since the first position is occupied by the stack's size
	# Multiply by four (a word is 4 bytes)
	li $t1 4
	mult $t0 $t1
	mflo $t0
	add $t0 $t0 $s0 # Add offset
	lw $v0 0($t0) # Load and return top of the stack
	lwc1 $f0 0($t0) # Load and return top of the stack
	
	addi $t2 $t2 -1
	sw $t2 4($s0) # Decrease size by 1
	
	#Pop
	lw $s0 4($sp)
	addi $sp $sp 4
	jr $ra
	
	stack_empty_error: # TODO: Must be implemented (throw a real MIPS exception)
	la $a0 stack_empty_msg
	jal print_str # Display error message
	li $v0 10
	syscall # Exit program
	
# done: # Simulation code
