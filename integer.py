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


# Perform the operation 'a + b = c' where 'a' and 'b' are (b)-bit
# integers and 'c' is a (b+1)-bit integer. Exactly (3*b + 1) indices
# must be provided to this routine, the number of bits is inferred.
def int_add(*bit_indices):
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
        iadd[f'a{b_idx}'] = 2**abs(p) * (-1 if p < 0 else 1)
    for row in range(-b,1):
        p = -2*row
        b_idx = bit_indices[3*b + row]
        iadd[f'a{b_idx}'] = 2**abs(p) * (-1 if p < 0 else 1)
    # Assign the negative 'b' terms.
    for row in range(b+1):
        for col in range(2*b):
            p = -2*b + row + col%b
            b1_idx = col + 1
            b2_idx = 2*b + row + 1
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**abs(p) * (-1 if p < 0 else 1)
    # Assign the right triangle.
    for col in range(b):
        for row in range(b-col):
            p = 2*(b - col) - row
            b1_idx = 2*b + col + 1
            b2_idx = 2*b + col + row + 2
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**abs(p) * (-1 if p < 0 else 1)
    # Assign the top triangle.
    for row in range(1,2*b):
        for col in range(row):
            p = (2*b - row%b) - 1 - col%b
            b1_idx = col + 1
            b2_idx = row + 1
            iadd[f'b{b1_idx}b{b2_idx}'] = 2**abs(p) * (-1 if p < 0 else 1)
    # Return the QUBO
    return iadd




if __name__ == "__main__":
    # These are the QUBO solutions to addition with 1, 2, and 3 bits.
    from qubo import QUBO
    iadd_one =  {'a1': 1, 'a2': 1, 'a3': 4, 'b1b3': -4, 'b3b4': 4, 'b2b3': -4, 'b1b2': 2, 'a4': 1, 'b1b4': -2, 'b2b4': -2}
    iadd_two =  {'a1': 4, 'a3': 4, 'b4b5': -8, 'b2b5': -8, 'b5b7': 8, 'b3b4': 4, 'b3b7': -4, 'b2b3': 4, 'b1b5': -16, 'b5b6': 16, 'b1b3': 8, 'b6b7': 4, 'b2b6': -4, 'b4b6': -4, 'a5': 16, 'b3b6': -8, 'a6': 4, 'b1b4': 4, 'b1b7': -4, 'b1b2': 4, 'b1b6': -8, 'b3b5': -16, 'b2b4': 2, 'b4b7': -2, 'b2b7': -2, 'a2': 1, 'a4': 1, 'a7': 1}
    iadd_three =  {'a1': 16, 'a4': 16, 'b1b2': 16, 'b7b9': 32, 'b7b10': 16, 'b4b5': 16, 'b2b4': 16, 'b1b5': 16, 'b5b8': -16, 'b2b8': -16, 'b1b4': 32, 'b1b8': -32, 'a8': 16, 'b4b8': -32, 'b4b9': -16, 'b8b9': 16, 'b1b9': -16, 'b7b8': 64, 'b2b7': -32, 'b5b7': -32, 'a7': 64, 'b1b7': -64, 'b4b7': -64, 'b3b7': -16, 'b6b7': -16, 'b1b3': 8, 'b1b10': -8, 'b4b6': 8, 'b1b6': 8, 'b4b10': -8, 'b3b4': 8, 'b3b8': -8, 'b6b8': -8, 'b8b10': 8, 'b5b9': -8, 'b2b9': -8, 'b2b5': 8, 'a5': 4, 'a2': 4, 'a9': 4, 'b5b6': 4, 'b3b9': -4, 'b6b9': -4, 'b2b10': -4, 'b3b5': 4, 'b5b10': -4, 'b2b6': 4, 'b9b10': 4, 'b2b3': 4, 'b3b6': 2, 'b6b10': -2, 'b3b10': -2, 'a3': 1, 'a6': 1, 'a10': 1}
    iadd_four = {'a1': 64, 'a5': 64, 'b1b6': 64, 'b2b5': 64, 'b1b2': 64, 'b5b6': 64, 'b9b11': 128, 'b2b10': -64, 'b6b10': -64, 'a10': 64, 'b1b10': -128, 'b5b10': -128, 'b1b5': 128, 'b9b12': 64, 'b5b11': -64, 'b10b11': 64, 'b1b11': -64, 'b1b9': -256, 'b2b9': -128, 'a9': 256, 'b6b9': -128, 'b9b10': 256, 'b5b9': -256, 'b7b9': -64, 'b3b9': -64, 'b7b10': -32, 'b5b7': 32, 'b3b5': 32, 'b3b10': -32, 'b10b12': 32, 'b1b7': 32, 'b5b12': -32, 'b1b3': 32, 'b1b12': -32, 'b4b9': -32, 'b2b6': 32, 'b2b11': -32, 'b6b11': -32, 'a6': 16, 'a2': 16, 'a11': 16, 'b3b11': -16, 'b4b10': -16, 'b2b3': 16, 'b7b11': -16, 'b2b7': 16, 'b1b4': 16, 'b3b6': 16, 'b4b5': 16, 'b6b12': -16, 'b6b7': 16, 'b2b12': -16, 'b11b12': 16, 'b8b10': -16, 'b1b8': 16, 'b5b8': 16, 'b8b9': -32, 'b5b13': -16, 'b10b13': 16, 'b9b13': 32, 'b1b13': -16, 'b2b13': -8, 'b2b4': 8, 'b4b11': -8, 'b6b8': 8, 'b4b6': 8, 'b6b13': -8, 'b11b13': 8, 'b2b8': 8, 'b8b11': -8, 'b3b7': 8, 'b7b12': -8, 'b3b12': -8, 'a7': 4, 'a12': 4, 'a3': 4, 'b4b12': -4, 'b7b8': 4, 'b7b13': -4, 'b8b12': -4, 'b12b13': 4, 'b4b7': 4, 'b3b4': 4, 'b3b8': 4, 'b3b13': -4, 'b4b8': 2, 'b8b13': -2, 'b4b13': -2, 'a4': 1, 'a8': 1, 'a13': 1}

    print("1-bit integer addition:")
    print(QUBO(iadd_one))
    print()
    print("2-bit integer addition:")
    print(QUBO(iadd_two))
    print()
    print("3-bit integer addition:")
    print(QUBO(iadd_three))
    print()
    print("4-bit integer addition:")
    print(QUBO(iadd_four))
    print()

    b = 4
    print(int_add(*range(1,b*3+1+1)))
