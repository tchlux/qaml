from qubo import QUBO
from exceptions import UsageError

# Given an arbitrary number of bit indices, assume they represent a
# big-endian integer. Generate a QUBO that minimizes this integer.
def int_abs_min(*bit_indices):
    constants = {f"a{b}" : 2**(len(bit_indices)-i-1)
                 for i,b in enumerate(bit_indices)}
    interactions = {f"b{bit_indices[0]}b{b}" : -2**(len(bit_indices)-i)
                    for i,b in enumerate(bit_indices)}
    constants.update(interactions)
    return QUBO(constants)


# Given an arbitrary number of bit indices, assume they represent a
# big-endian integer. Generate a QUBO that minimizes this integer.
def int_min(*bit_indices):
    return QUBO({f"a{b}" : (2**(len(bit_indices)-i-1) if i > 0
                            else -2**(len(bit_indices)-1))
                 for i,b in enumerate(bit_indices)})

# Given an arbitrary number of bit indices, assume they represent a
# big-endian unsigned integer. Generate a QUBO that minimizes this integer.
def uint_min(*bit_indices):
    return QUBO({f"a{b}" : 2**(len(bit_indices)-i-1)
                 for i,b in enumerate(bit_indices)})

# Perform the operation 'a + b + i = c' where 'a' and 'b' are (b)-bit
# integers, 'i' is a 0 or 1 carry-in bit, and 'c' is a (b+1)-bit
# integer. Exactly (3*b + 2) indices must be provided to this routine,
# the number of bits is inferred.
def int_full_add(*bit_indices):
    # Compute and verify the number of bits.
    b = (len(bit_indices) - 2) // 3
    if (b*3 + 2) != len(bit_indices):
        raise(UsageError("Exactly 3*b+2 bits must be provided for b-bit addition."))
    # Initialize a QUBO to store the addition operator.
    iadd = QUBO()
    # Assign the 'a' terms.
    for row in range(2*b):
        p = 2*(b - row%b - 1)
        b_idx = bit_indices[row]
        iadd[f'a{b_idx}'] = 2**p
    # Set the "carry in bit" a coefficient.
    iadd[f'a{bit_indices[2*b]}'] = 1
    # Set the rest of the a coefficients.
    for row in range(b+1):
        p = 2*(b - row)
        b_idx = bit_indices[2*b + 1 + row]
        iadd[f'a{b_idx}'] = 2**p
    # Assign the negative 'b' terms.
    for row in range(b+1):
        for col in range(2*b+1):
            p = -2*b + row + min(col,2*b-1)%b
            b1_idx = bit_indices[col]
            b2_idx = bit_indices[2*b + row + 1]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**abs(p) * -1
    # Assign the right triangle.
    for col in range(b):
        for row in range(b-col):
            p = 2*(b - col) - row
            b1_idx = bit_indices[2*b + col + 1]
            b2_idx = bit_indices[2*b + col + row + 2]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Assign the top triangle.
    for row in range(1,2*b+1):
        for col in range(row):
            p = (2*b - min(row,2*b-1)%b) - 1 - col%b
            b1_idx = bit_indices[col]
            b2_idx = bit_indices[row]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Return the QUBO
    return iadd
    

# Perform the operation 'a + b = c' where 'a' and 'b' are (b)-bit
# integers and 'c' is a (b+1)-bit integer. Exactly (3*b + 1) indices
# must be provided to this routine, the number of bits is inferred.
def int_half_add(*bit_indices):
    # Compute and verify the number of bits.
    b = (len(bit_indices) - 1) // 3
    if (b*3 + 1) != len(bit_indices):
        raise(UsageError("Exactly 3*b+1 bits must be provided for b-bit addition."))
    # Initialize a QUBO to store the addition operator.
    iadd = QUBO()
    # Assign the 'a' terms.
    for row in range(2*b):
        p = 2*(b - row%b - 1)
        b_idx = bit_indices[row]
        iadd[f'a{b_idx}'] = 2**p
    for row in range(-b,1):
        p = -2*row
        b_idx = bit_indices[3*b + row]
        iadd[f'a{b_idx}'] = 2**p
    # Assign the negative 'b' terms.
    for row in range(b+1):
        for col in range(2*b):
            p = -2*b + row + col%b
            b1_idx = bit_indices[col]
            b2_idx = bit_indices[2*b + row]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**abs(p) * -1
    # Assign the right triangle.
    for col in range(b):
        for row in range(b-col):
            p = 2*(b - col) - row
            b1_idx = bit_indices[2*b + col]
            b2_idx = bit_indices[2*b + col + row + 1]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Assign the top triangle.
    for row in range(1,2*b):
        for col in range(row):
            p = (2*b - row%b) - 1 - col%b
            b1_idx = bit_indices[col]
            b2_idx = bit_indices[row]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Return the QUBO
    return iadd


# Perform the operation 'a + b = c' where 'a' 'b' and 'c' are (b)-bit
# integers. Overflow solutions have nonzero enrgy, making the only
# valid final states those which do not overflow.
# Exactly (3*b) indices must be provided to this routine, the
# number of bits is inferred.
def int_add(*bit_indices):
    # Compute and verify the number of bits.
    if (len(bit_indices) % 3 != 0):
        raise(UsageError("Exactly 3*b bits must be provided for b-bit addition."))
    b = len(bit_indices) // 3
    # Initialize a QUBO to store the addition operator.
    iadd = QUBO()
    # Assign the 'a' terms.
    for row in range(3*b):
        p = 2*(b - 1 - row%b)
        b_idx = bit_indices[row]
        iadd[f'a{b_idx}'] = 2**abs(p)
    # Assign the negative 'b' terms.
    for row in range(b):
        for col in range(2*b):
            p = -2*b + 1 + row + col%b
            b1_idx = col + 1
            b2_idx = 2*b + row + 1
            iadd[f'b{b1_idx}b{b2_idx}'] = -2**abs(p)
    # Assign the right triangle.
    for col in range(b-1):
        for row in range(b-1-col):
            p = 2*(b-1) - 2*col - row
            b1_idx = bit_indices[2*b + col]
            b2_idx = bit_indices[2*b + col + row + 1]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Assign the top triangle.
    for row in range(1,2*b):
        for col in range(row):
            p = (2*b - row%b) - 1 - col%b
            b1_idx = bit_indices[col]
            b2_idx = bit_indices[row]
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**p
    # Return the QUBO
    return iadd


# Perform the operation 'q + r = s' where 'q' and 'r' are (n)-bit 
# integers, and 's' is a (n+1)-bit integer. Each module can have '3*b+2' 
# or '3*b+1' bits that are fully connected. Exactly (3*n + ceil(n/b)) 
# indices must be provided to this routine.
def int_add_modular(n, b, *bit_indices):
    from math import ceil
    # Compute and verify the number of bits.
    num_modules = ceil(n/b)
    num_qubits = 3*n + num_modules
    if num_qubits != len(bit_indices):
        raise(UsageError("Exactly 3*n+ceil(n/b) bits must be provided for n-bit addition with module size b."))
    # Return int_half_add() if num_modules = 1.
    if num_modules==1:
        return int_half_add(*bit_indices)
    # If num_modules > 1 :
    # Initialize a QUBO to store the addition operator.
    iadd = QUBO()
    # Add QUBO for right module - size is always b.
    iadd += int_half_add(*(bit_indices[n-b:n] + bit_indices[2*n-b:2*n]
                           + bit_indices[-1:] + bit_indices[3*n+1-b:3*n+1]))
    # Add QUBO for left module - size can be less than b.
    iadd += int_full_add(*(bit_indices[:n-(num_modules-1)*b] 
                           + bit_indices[n:2*n-(num_modules-1)*b] 
                           + bit_indices[3*n+1:3*n+2] 
                           + bit_indices[2*n:3*n-(num_modules-1)*b+1]))
    # Add QUBO for other modules - size is always b.
    for i in range(1,num_modules-1):
        iadd += int_full_add(*(bit_indices[n-(i+1)*b:n-i*b] + bit_indices[2*n-(i+1)*b:2*n-i*b]
                                  + bit_indices[3*n+num_modules-i:3*n+num_modules-i+1]
                                  + bit_indices[3*n+num_modules-i-1:3*n+num_modules-i] 
                                  + bit_indices[3*n-(i+1)*b+1:3*n-i*b+1]))
    # Return the QUBO.
    return iadd


# Perform the operation 'x1+x2+...+xm=s' where each xi is a b-bit signed int 
# and s is a (m+b-1)-bit signed int. Exactly mb+m+b-1 indices must be 
# provided to this routine.
def multi_int_add(m, b, *bit_indices):
    # Verify that m>1 ,b>0
    if m<=1 or b<=0:
        raise(UsageError("m>1, b>0 is expected for m-int b-bit addition."))
    num_qubits = m*b + m + b -1
    # Compute and verify the number of bits.
    if len(bit_indices) != num_qubits:
        raise(UsageError("Exactly m*b+m+b-1 bits must be provided for m-int b-bit addition."))
    # Compute coefficients in addition equation.
    eq_coeffs = [0 for i in range(num_qubits)]
    pos = 0
    for i in range(b-1,0,-1):
        for j in range(m):
            eq_coeffs[j*b+i] = 2**pos
        pos += 1
    temp1 = 2**(b-1)
    temp2 = 2**b
    eq_coeffs[0] = temp1
    eq_coeffs[b] = temp1
    for j in range(2,m):
        eq_coeffs[j*b] = temp1 + temp2*(2**(j-1)-1)
    pos = 0
    for i in range(num_qubits-1, m*b-1, -1):
        eq_coeffs[i] = -2**pos
        pos += 1
    # Initialize a QUBO to store the addition operator.
    iadd = QUBO()
    # Square the equation to compute the qubo coefficients.
    for i in range(num_qubits):
        iadd[f'a{bit_indices[i]}'] = eq_coeffs[i]**2
    for i in range(num_qubits-1):
        for j in range(i+1, num_qubits):
            iadd[f'b{bit_indices[i]}b{bit_indices[j]}'] = 2*eq_coeffs[i]*eq_coeffs[j]
    return iadd
        

# Performs the operation x * y = p where x and y are b-bit uints,
# and p is a 2b-bit uint. Exactly 4b+b^2 bits are required, where
# the first b bits contain x, bits b+1 through 2b contain y, bits
# 2b+1 through 4b contain p, and the final b^2 bits are ancillary
# bits containing the values for all combinations of x_i y_j.
def int_full_mult(*bit_indices):
    import math
    # Get number of bits.
    b = int((2*int(math.sqrt(4+len(bit_indices)))-4)/2)
    print(b)
    if(len(bit_indices) != 4*b + b*b):
        raise(UsageError("Exactly b^2+4b bits must be provided for b-bit multiplication."))
    # Initialize a QUBO to store the multiplication operator.
    imult = QUBO()
    # Assign the b^2 ancilla bits: anc_{b*i+j} = x_i && y_j.
    for i in range(4*b,4*b+b*b):
        # Weights for an AND gate.
        imult[f'a{bit_indices[i]}'] = 3
        imult[f'b{bit_indices[(i-4*b)//b]}b{bit_indices[b+(i-4*b)%b]}'] = 1
        imult[f'b{bit_indices[i]}b{bit_indices[(i-4*b)//b]}'] = -2
        imult[f'b{bit_indices[i]}b{bit_indices[b+(i-4*b)%b]}'] = -2
    # Assign the connections and weights to the ancillary bits.
    for i in range(4*b,4*b+b*b):
        imult[f'a{bit_indices[i]}'] += 2**(2*((i-4*b)//b + (i-4*b)%b)) # Increment.
        for j in range(i+1,4*b+b*b):
            imult[f'b{bit_indices[i]}b{bit_indices[j]}'] = 2**((i-4*b)//b + (i-4*b)%b + (j-4*b)//b + (j-4*b)%b + 1)
    # Assign the connections between p and the ancillary bits.
    for i in range(2*b,4*b):
        for j in range(4*b,4*b+b*b):
            imult[f'b{bit_indices[i]}b{bit_indices[j]}'] = -2**((i-2*b) + (j-4*b)//b + (j-4*b)%b + 1)
    # Assign the connections and weights to p.
    for i in range(2*b,4*b):
        imult[f'a{bit_indices[i]}'] = 2**(2*(i-2*b))
        for j in range(i+1,4*b):
            imult[f'b{bit_indices[i]}b{bit_indices[j]}'] = 2**((j-2*b) + (i-2*b) + 1)
    # Return the QUBO.
    return imult


if __name__ == "__main__":
    # These are the QUBO solutions to addition with 1, 2, and 3 bits.
    from qubo import QUBO, run_qubo

    DEMONSTRATE_INT_MIN = False
    if DEMONSTRATE_INT_MIN:
        b = 3
        print("-"*70)
        print("Minimizing the value of a signed integer:")
        out = run_qubo(**int_min(*list(range(1,b+1))), min_only=False)
        print()
        print("Minimizing the absolute value of a signed integer:")
        out = run_qubo(**int_abs_min(*list(range(1,b+1))), min_only=False)
        print()
        print("Minimizing the value of an unsigned integer:")
        out = run_qubo(**uint_min(*list(range(1,b+1))), min_only=False)

    DEMONSTRATE_UINT_MULT = False
    if DEMONSTRATE_UINT_MULT:
        uint_mult_two =   {'b1b2': 1, 'a1': 0, 'a2': 0, 'a3': 2, 'b3b4': -1, 'b1b4': -2, 'b2b4': -2, 'a4': 3, 'b2b3': 0, 'b1b3': 0}
        uint_mult_three = {}
        print("2-bit unsigned integer multiplication:")
        sol = run_qubo(**QUBO(uint_mult_two), display=True)
        from truth import int_mult_table
        print("Passed:", sol == int_mult_table(n_bits=1, signed=False, full=True))
        print()
        print("Finding 2-bit multiplication QUBO")
        from solve import find_qubo, find_int_qubo
        truth_table = int_mult_table(n_bits=2, signed=False, full=True)
        q = find_qubo(truth_table, gap=.01, random=False)
        sol = run_qubo(**q)
        # q = find_int_qubo(int_mult_table(n_bits=2, signed=False, full=True))
        print("Passed:", sol == truth_table)
        int_q = find_int_qubo(truth_table, display=False)
        print("Integer solution:")
        print(int_q)



    DEMONSTRATE_INT_ADD = False
    if DEMONSTRATE_INT_ADD:
        int_add_one =   {'a1': 1, 'a2': 1, 'a3': 1, 'b1b3': -2, 'b2b3': -2, 'b1b2': 2}
        int_add_two =   {'a1': 4, 'a3': 4, 'b1b6': -4, 'b3b6': -4, 'b5b6': 4, 'b2b5': -4, 'b1b2': 4, 'b2b3': 4, 'b4b5': -4, 'b1b4': 4, 'b3b4': 4, 'a5': 4, 'b1b5': -8, 'b3b5': -8, 'b1b3': 8, 'b2b4': 2, 'b2b6': -2, 'b4b6': -2, 'a2': 1, 'a4': 1, 'a6': 1}
        int_add_three = {'a1': 16, 'a4': 16, 'a7': 16, 'b1b7': -32, 'b4b7': -32, 'b2b7': -16, 'b5b7': -16, 'b2b4': 16, 'b4b5': 16, 'b1b4': 32, 'b1b2': 16, 'b1b5': 16, 'b1b8': -16, 'b7b8': 16, 'b4b8': -16, 'b5b8': -8, 'b2b8': -8, 'b2b5': 8, 'b1b9': -8, 'b4b9': -8, 'b7b9': 8, 'b6b7': -8, 'b1b6': 8, 'b4b6': 8, 'a8': 4, 'a2': 4, 'a5': 4, 'b2b6': 4, 'b2b9': -4, 'b5b6': 4, 'b6b8': -4, 'b5b9': -4, 'b8b9': 4, 'b3b5': 4, 'b3b8': -4, 'b2b3': 4, 'b3b7': -8, 'b1b3': 8, 'b3b4': 8, 'b3b6': 2, 'b6b9': -2, 'b3b9': -2, 'a3': 1, 'a6': 1, 'a9': 1}
        int_add_four =   {'b1b2': 64, 'b2b9': -64, 'b9b10': 64, 'b1b10': -64, 'b5b10': -64, 'b2b5': 64, 'a9': 64, 'b5b11': -32, 'b1b11': -32, 'b9b11': 32, 'b2b10': -32, 'b6b10': -32, 'b2b6': 32, 'b5b6': 64, 'b6b9': -64, 'b1b6': 64, 'a10': 16, 'a2': 16, 'a6': 16, 'b6b11': -16, 'b2b11': -16, 'b10b11': 16, 'b9b12': 16, 'b5b12': -16, 'b1b12': -16, 'b1b8': 16, 'b8b9': -16, 'b5b8': 16, 'b2b12': -8, 'b6b8': 8, 'b8b10': -8, 'b2b8': 8, 'b10b12': 8, 'b6b12': -8, 'b2b4': 8, 'b4b10': -8, 'b4b6': 8, 'b4b9': -16, 'b4b5': 16, 'b1b4': 16, 'b7b11': -8, 'b3b11': -8, 'b3b7': 8, 'b1b9': -128, 'a1': 64, 'b1b5': 128, 'b5b9': -128, 'a5': 64, 'b3b8': 4, 'b3b4': 4, 'b3b12': -4, 'b7b8': 4, 'b7b12': -4, 'b4b7': 4, 'b8b11': -4, 'b11b12': 4, 'b6b7': 16, 'b3b6': 16, 'a7': 4, 'a3': 4, 'a11': 4, 'b2b7': 16, 'b5b7': 32, 'b7b9': -32, 'b1b7': 32, 'b4b11': -4, 'b7b10': -16, 'b2b3': 16, 'b1b3': 32, 'b3b5': 32, 'b3b9': -32, 'b3b10': -16, 'b4b8': 2, 'b8b12': -2, 'b4b12': -2, 'a8': 1, 'a4': 1, 'a12': 1}

        print('-'*70)
        print()
        print("1-bit integer addition:")
        print(QUBO(int_add_one))
        print()
        print("2-bit integer addition:")
        print(QUBO(int_add_two))
        print()
        print("3-bit integer addition:")
        print(QUBO(int_add_three))
        print()

        # Verify the correctness of the generated integer adders.
        print("Verifying QUBO correctness..")
        from truth import int_add_table
        for b in range(1,6):
            q = int_add(*list(range(1,b*3+1)))
            sol = run_qubo(**q, display=False)
            out = int_add_table(n_bits=b, signed=False, carry=False)
            print(b, sol == out)


    DEMONSTRATE_INT_HALF_ADD = False
    if DEMONSTRATE_INT_HALF_ADD:
        int_add_one =  {'a1': 1, 'a2': 1, 'a3': 4, 'b1b3': -4, 'b3b4': 4, 'b2b3': -4, 'b1b2': 2, 'a4': 1, 'b1b4': -2, 'b2b4': -2}
        int_add_two =  {'a1': 4, 'a3': 4, 'b4b5': -8, 'b2b5': -8, 'b5b7': 8, 'b3b4': 4, 'b3b7': -4, 'b2b3': 4, 'b1b5': -16, 'b5b6': 16, 'b1b3': 8, 'b6b7': 4, 'b2b6': -4, 'b4b6': -4, 'a5': 16, 'b3b6': -8, 'a6': 4, 'b1b4': 4, 'b1b7': -4, 'b1b2': 4, 'b1b6': -8, 'b3b5': -16, 'b2b4': 2, 'b4b7': -2, 'b2b7': -2, 'a2': 1, 'a4': 1, 'a7': 1}
        int_add_three =  {'a1': 16, 'a4': 16, 'b1b2': 16, 'b7b9': 32, 'b7b10': 16, 'b4b5': 16, 'b2b4': 16, 'b1b5': 16, 'b5b8': -16, 'b2b8': -16, 'b1b4': 32, 'b1b8': -32, 'a8': 16, 'b4b8': -32, 'b4b9': -16, 'b8b9': 16, 'b1b9': -16, 'b7b8': 64, 'b2b7': -32, 'b5b7': -32, 'a7': 64, 'b1b7': -64, 'b4b7': -64, 'b3b7': -16, 'b6b7': -16, 'b1b3': 8, 'b1b10': -8, 'b4b6': 8, 'b1b6': 8, 'b4b10': -8, 'b3b4': 8, 'b3b8': -8, 'b6b8': -8, 'b8b10': 8, 'b5b9': -8, 'b2b9': -8, 'b2b5': 8, 'a5': 4, 'a2': 4, 'a9': 4, 'b5b6': 4, 'b3b9': -4, 'b6b9': -4, 'b2b10': -4, 'b3b5': 4, 'b5b10': -4, 'b2b6': 4, 'b9b10': 4, 'b2b3': 4, 'b3b6': 2, 'b6b10': -2, 'b3b10': -2, 'a3': 1, 'a6': 1, 'a10': 1}
        int_add_four = {'a1': 64, 'a5': 64, 'b1b6': 64, 'b2b5': 64, 'b1b2': 64, 'b5b6': 64, 'b9b11': 128, 'b2b10': -64, 'b6b10': -64, 'a10': 64, 'b1b10': -128, 'b5b10': -128, 'b1b5': 128, 'b9b12': 64, 'b5b11': -64, 'b10b11': 64, 'b1b11': -64, 'b1b9': -256, 'b2b9': -128, 'a9': 256, 'b6b9': -128, 'b9b10': 256, 'b5b9': -256, 'b7b9': -64, 'b3b9': -64, 'b7b10': -32, 'b5b7': 32, 'b3b5': 32, 'b3b10': -32, 'b10b12': 32, 'b1b7': 32, 'b5b12': -32, 'b1b3': 32, 'b1b12': -32, 'b4b9': -32, 'b2b6': 32, 'b2b11': -32, 'b6b11': -32, 'a6': 16, 'a2': 16, 'a11': 16, 'b3b11': -16, 'b4b10': -16, 'b2b3': 16, 'b7b11': -16, 'b2b7': 16, 'b1b4': 16, 'b3b6': 16, 'b4b5': 16, 'b6b12': -16, 'b6b7': 16, 'b2b12': -16, 'b11b12': 16, 'b8b10': -16, 'b1b8': 16, 'b5b8': 16, 'b8b9': -32, 'b5b13': -16, 'b10b13': 16, 'b9b13': 32, 'b1b13': -16, 'b2b13': -8, 'b2b4': 8, 'b4b11': -8, 'b6b8': 8, 'b4b6': 8, 'b6b13': -8, 'b11b13': 8, 'b2b8': 8, 'b8b11': -8, 'b3b7': 8, 'b7b12': -8, 'b3b12': -8, 'a7': 4, 'a12': 4, 'a3': 4, 'b4b12': -4, 'b7b8': 4, 'b7b13': -4, 'b8b12': -4, 'b12b13': 4, 'b4b7': 4, 'b3b4': 4, 'b3b8': 4, 'b3b13': -4, 'b4b8': 2, 'b8b13': -2, 'b4b13': -2, 'a4': 1, 'a8': 1, 'a13': 1}

        print('-'*70)
        print()
        print("1-bit integer half-adder addition:")
        print(QUBO(int_add_one))
        print()
        print("2-bit integer half-adder addition:")
        print(QUBO(int_add_two))
        print()
        print("3-bit integer half-adder addition:")
        print(QUBO(int_add_three))
        print()

        # Verify the correctness of the generated integer adders.
        print("Verifying QUBO correctness..")
        from truth import int_add_table
        for b in range(1,6):
            q = int_half_add(*list(range(1,b*3+1+1)))
            sol = run_qubo(**q, display=False)
            print(b, sol == int_add_table(n_bits=b, signed=False))


    DEMONSTRATE_INT_FULL_ADD = False
    if DEMONSTRATE_INT_FULL_ADD:
        solutions = {
            1 : {'a4': 4, 'a2': 1, 'a3': 1, 'a1': 1, 'b1b4': -4, 'b2b4': -4, 'b1b2': 2, 'b4b5': 4, 'a5': 1, 'b1b5': -2, 'b2b5': -2, 'b3b5': -2, 'b3b4': -4, 'b1b3': 2, 'b2b3': 2},
            2 : {'a1': 4, 'a3': 4, 'b5b6': -8, 'a6': 16, 'b3b5': 4, 'b3b6': -16, 'b2b3': 4, 'b2b6': -8, 'b3b8': -4, 'b6b8': 8, 'b3b4': 4, 'b4b6': -8, 'b4b7': -4, 'b7b8': 4, 'a7': 4, 'b5b7': -4, 'b2b7': -4, 'b1b7': -8, 'b3b7': -8, 'b1b4': 4, 'b1b8': -4, 'b1b6': -16, 'b6b7': 16, 'b1b3': 8, 'b1b5': 4, 'b1b2': 4, 'b2b8': -2, 'b4b5': 2, 'b4b8': -2, 'b2b5': 2, 'b5b8': -2, 'b2b4': 2, 'a4': 1, 'a5': 1, 'a8': 1, 'a2': 1},
            3 : {'a1': 16, 'a2': 4, 'a3': 1, 'a4': 16, 'a5': 4, 'a6': 1, 'a7': 1, 'a8': 64, 'a9': 16, 'a10': 4, 'a11': 1, 'b1b2': 16, 'b1b3': 8, 'b1b4': 32, 'b1b5': 16, 'b1b6': 8, 'b1b7': 8, 'b1b8': -64, 'b1b9': -32, 'b1b10': -16, 'b1b11': -8, 'b2b3': 4, 'b2b4': 16, 'b2b5': 8, 'b2b6': 4, 'b2b7': 4, 'b2b8': -32, 'b2b9': -16, 'b2b10': -8, 'b2b11': -4, 'b3b4': 8, 'b3b5': 4, 'b3b6': 2, 'b3b7': 2, 'b3b8': -16, 'b3b9': -8, 'b3b10': -4, 'b3b11': -2, 'b4b5': 16, 'b4b6': 8, 'b4b7': 8, 'b4b8': -64, 'b4b9': -32, 'b4b10': -16, 'b4b11': -8, 'b5b6': 4, 'b5b7': 4, 'b5b8': -32, 'b5b9': -16, 'b5b10': -8, 'b5b11': -4, 'b6b7': 2, 'b6b8': -16, 'b6b9': -8, 'b6b10': -4, 'b6b11': -2, 'b7b8': -16, 'b7b9': -8, 'b7b10': -4, 'b7b11': -2, 'b8b9': 64, 'b8b10': 32, 'b8b11': 16, 'b9b10': 16, 'b9b11': 8, 'b10b11': 4}
        }

        print('-'*70)
        print()
        for b in range(1,len(solutions)+1):
            print(f"{b}-bit integer full-adder addition:")
            print(QUBO(solutions[b]))
            print()

        # Verify the correctness of the generated integer adders.
        print("Verifying QUBO correctness..")
        from truth import int_full_add_table
        for b in range(1,6):
            q = int_full_add(*list(range(1,b*3+2+1)))
            sol = run_qubo(**q, display=False)
            print(b, sol == int_full_add_table(n_bits=b))
            
    DEMONSTRATE_INT_MULT = False
    if DEMONSTRATE_INT_MULT:
        b = 2
        q = int_full_mult(*list(range(1, b*4+b*b + 1)))
        print("-"*70)
        print(f"{b}-bit unsigned integer multiplication:")
        sol = run_qubo(**q, min_only=True)

            
    DEMONSTRATE_INT_ADD_MODULAR = False
    if DEMONSTRATE_INT_ADD_MODULAR:
        from math import ceil
        n, b = 5, 2
        print("-"*70)
        print(f"{n}-bit integer addition with {b}-bit modules:")
        q = int_add_modular(n, b, *list(range(1, 3*n + ceil(n/b) + 1)))
        sol = [i[:3*n+1] for i in run_qubo(**q, display=False)]
        print("Verifying QUBO correctness..")
        from truth import int_add_table
        print(sol == int_add_table(n_bits=n, signed=False))
        
    
    DEMONSTRATE_MULTI_INT_ADD = False
    if DEMONSTRATE_MULTI_INT_ADD:
        m, b = 2, 1
        print("-"*70)
        print (f"{m}-int {b}-bit signed addition:")
        q = multi_int_add(m, b, *list(range(1, m*b+m+b)))
        sol = run_qubo(**q, min_only=True)
        print("Verifying QUBO correctness..")
        from truth import multi_int_add_table
        print(sol == multi_int_add_table(n_bits=b, n_ints=m))
