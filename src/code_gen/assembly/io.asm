.data
nl: .asciiz "\n"

.text
.globl print_number
.globl print_string
# .globl done # Simulation code

print_number:
	move $t0 $a0
	la $a0 nl
	li $v0 4
	syscall 
	
	move $a0 $t0
	li $v0 1
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra
	
print_string:
	move $t0 $a0
	la $a0 nl
	li $v0 4
	syscall 
	
	move $a0 $t0
	li $v0 4
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra

str_len: 
	li $t0 0 # Counter
	
	str_len_loop:
	lb $t1 ($a0) # Load character at address $a0
	beq $t1 0 str_len_end # Check if it's equal to the null terminator character
	addi $t0 $t0 1 # Increase counter
	addi $a0 $a0 1 # Move to the next byte
	j str_len_loop
	str_len_end:
	move $v0 $t0
	jr $ra
	
str_concat:
	addi $sp $sp -20
	sw $s0 4($sp)
	sw $s1 8($sp)
	sw $s2 12($sp)
	sw $s3 16($sp)
	sw $ra 20($sp)
	
	move $s0 $a0 # Save str1 address
	move $s1 $a1 # Save str2 address
	
	jal str_len # len(str1)
	move $s2 $v0
	
	move $a0 $a1
	jal str_len # len(str2)
	move $t0 $v0
	
	add $s2 $s2 $t0 # len(str1) + len(str2) + 1
	addi $s2 $s2 1
	
	li $t0 4
	div $s2 $t0
	mflo $s2 # Quotient
	mfhi $t0 # Remainder 
	
	bne $t0 $zero increase_quotient
	j size_ready
	increase_quotient:
	addi $s2 $s2 1
	size_ready:
	
	li $v0 9
	move $a0 $s2
	syscall
	move $s3 $v0 # Save concatenation string address
	
	move $t1 $s0
	move $t2 $s3
	str1_loop:
	lb $t0 ($t1) 
	beq $t0 0 str1_end
	sb $t0 ($t2)
	addi $t1 $t1 1
	addi $t2 $t2 1
	j str1_loop
	str1_end:
	
	move $t1 $s1
	str2_loop:
	lb $t0 ($t1) 
	beq $t0 0 str2_end
	sb $t0 ($t2)
	addi $t1 $t1 1
	addi $t2 $t2 1
	j str2_loop
	str2_end:
	sb $t0 ($t2)
	
	move $v0 $s3	

	lw $s0 4($sp)
	lw $s1 8($sp)
	lw $s2 12($sp)
	lw $s3 16($sp)
	lw $ra 20($sp)
	addi $sp $sp 20
	jr $ra

str_space_concat:
	addi $sp $sp -20
	sw $s0 4($sp)
	sw $s1 8($sp)
	sw $s2 12($sp)
	sw $s3 16($sp)
	sw $ra 20($sp)
	
	move $s0 $a0 # Save str1 address
	move $s1 $a1 # Save str2 address
	
	jal str_len # len(str1)
	move $s2 $v0
	
	move $a0 $a1
	jal str_len # len(str2)
	move $t0 $v0
	
	add $s2 $s2 $t0 # len(str1) + len(str2) + 2
	addi $s2 $s2 2
	
	li $t0 4
	div $s2 $t0
	mflo $s2 # Quotient
	mfhi $t0 # Remainder 
	
	bne $t0 $zero increase_quotient_space
	j size_ready_space
	increase_quotient_space:
	addi $s2 $s2 1
	size_ready_space:
	
	li $v0 9
	move $a0 $s2
	syscall
	move $s3 $v0 # Save concatenation string address
	
	move $t1 $s0
	move $t2 $s3
	str1_loop_space:
	lb $t0 ($t1) 
	beq $t0 0 str1_end_space
	sb $t0 ($t2)
	addi $t1 $t1 1
	addi $t2 $t2 1
	j str1_loop_space
	str1_end_space:
	li $t0 32
	sb $t0 ($t2)
	addi $t2 $t2 1
	
	move $t1 $s1
	str2_loop_space:
	lb $t0 ($t1) 
	beq $t0 0 str2_end_space
	sb $t0 ($t2)
	addi $t1 $t1 1
	addi $t2 $t2 1
	j str2_loop_space
	str2_end_space:
	sb $t0 ($t2)
	
	move $v0 $s3	

	lw $s0 4($sp)
	lw $s1 8($sp)
	lw $s2 12($sp)
	lw $s3 16($sp)
	lw $ra 20($sp)
	addi $sp $sp 20
	jr $ra	

# done: # Simulation code
