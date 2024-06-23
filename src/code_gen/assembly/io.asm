.data
nl: .asciiz "\n"
true: .asciiz "true"
false: .asciiz "false"

.text
.globl print_number
.globl print_str
.globl number_to_str
.globl str_concat
.globl str_space_concat
# .globl done # Simulation code

#** Printing code

print_number:
	# la $a0 nl
	# li $v0 4
	# syscall 
	
	li $v0 2
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra
	
print_str:
	# move $t0 $a0
	# la $a0 nl
	# li $v0 4
	# syscall 
	#move $a0 $t0
	
	li $v0 4
	syscall
	
	la $a0 nl
	li $v0 4
	syscall
	
	jr $ra

print_bool:
	addi $sp $sp -4
	sw $ra 4($sp)
	bne $a0 1 print_bool_false
	la $a0 true
	jal print_str
	lw $ra 4($sp)
	addi $sp $sp 4
	jr $ra

	print_bool_false:
	la $a0 false
	jal print_str
	lw $ra 4($sp)
	addi $sp $sp 4
	jr $ra

#** String manipulation code

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


#** Conversions code

number_to_str:
	addi $sp $sp -8
	sw $ra 4($sp)
	sw $s0 8($sp)
	
	cvt.w.s $f12 $f12
	swc1 $f12 8($sp)
	lw $a0 8($sp)
	move $s0 $a0
	abs $a0 $a0
	
	jal int_to_str
	move $t0 $v0

	slt $s0 $s0 $zero
	beq $s0 1 number_to_str_negative
	lw $ra 4($sp)
	lw $s0 8($sp)
	addi $sp $sp 8
	jr $ra

	number_to_str_negative:
	li $t1 45
	li $v0 9
	li $a0 2
	syscall
	sb $t1 ($v0)
	li $t1 0
	sb $t1 1($v0)

	move $a0 $v0
	move $a1 $t0
	jal str_concat
	
	lw $ra 4($sp)
	lw $s0 8($sp)
	addi $sp $sp 8
	jr $ra
	
int_to_str:
	addi $sp $sp -12
	sw $ra 4($sp)
	sw $s0 8($sp)
	sw $s1 12($sp)
	
	move $s0 $a0 # Save n
	
	# Base case (n < 10)
	li $t1 10 
	slt $t0 $s0 $t1
	beq $t0 $zero int_to_str_recursive_case
	jal digit_to_str
	lw $ra 4($sp)
	lw $s0 8($sp)
	lw $s1 12($sp)
	addi $sp $sp 12
	jr $ra
	
	int_to_str_recursive_case:
	li $t1 10
	div $s0 $t1
	mflo $s0
	mfhi $s1
	
	move $a0 $s0
	jal int_to_str
	move $s0 $v0
	
	move $a0 $s1
	jal digit_to_str
	move $s1 $v0
	
	move $a0 $s0
	move $a1 $s1
	jal str_concat 
	
	lw $ra 4($sp)
	lw $s0 8($sp)
	lw $s1 12($sp)
	addi $sp $sp 12
	jr $ra
	
digit_to_str:
	addi $t0 $a0 48
	li $a0 2
	li $v0 9
	syscall
	sb $t0 0($v0)
	sb $zero 1($v0)
	jr $ra

# done: # Simulation code
