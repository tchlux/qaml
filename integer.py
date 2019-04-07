from qubo import QUBO

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



if __name__ == "__main__":
    # These are the QUBO solutions to addition with 1, 2, and 3 bits.
    from qubo import QUBO
    iadd_one =  {'a1': 1, 'a2': 1, 'a3': 4, 'b1b3': -4, 'b3b4': 4, 'b2b3': -4, 'b1b2': 2, 'a4': 1, 'b1b4': -2, 'b2b4': -2}
    iadd_two =  {'a1': 4, 'a3': 4, 'b4b5': -8, 'b2b5': -8, 'b5b7': 8, 'b3b4': 4, 'b3b7': -4, 'b2b3': 4, 'b1b5': -16, 'b5b6': 16, 'b1b3': 8, 'b6b7': 4, 'b2b6': -4, 'b4b6': -4, 'a5': 16, 'b3b6': -8, 'a6': 4, 'b1b4': 4, 'b1b7': -4, 'b1b2': 4, 'b1b6': -8, 'b3b5': -16, 'b2b4': 2, 'b4b7': -2, 'b2b7': -2, 'a2': 1, 'a4': 1, 'a7': 1}
    iadd_three =  {'a1': 16, 'a4': 16, 'b1b2': 16, 'b7b9': 32, 'b7b10': 16, 'b4b5': 16, 'b2b4': 16, 'b1b5': 16, 'b5b8': -16, 'b2b8': -16, 'b1b4': 32, 'b1b8': -32, 'a8': 16, 'b4b8': -32, 'b4b9': -16, 'b8b9': 16, 'b1b9': -16, 'b7b8': 64, 'b2b7': -32, 'b5b7': -32, 'a7': 64, 'b1b7': -64, 'b4b7': -64, 'b3b7': -16, 'b6b7': -16, 'b1b3': 8, 'b1b10': -8, 'b4b6': 8, 'b1b6': 8, 'b4b10': -8, 'b3b4': 8, 'b3b8': -8, 'b6b8': -8, 'b8b10': 8, 'b5b9': -8, 'b2b9': -8, 'b2b5': 8, 'a5': 4, 'a2': 4, 'a9': 4, 'b5b6': 4, 'b3b9': -4, 'b6b9': -4, 'b2b10': -4, 'b3b5': 4, 'b5b10': -4, 'b2b6': 4, 'b9b10': 4, 'b2b3': 4, 'b3b6': 2, 'b6b10': -2, 'b3b10': -2, 'a3': 1, 'a6': 1, 'a10': 1}

    
    print("1-bit integer addition:")
    print(QUBO(iadd_one))
    print()
    print("2-bit integer addition:")
    print(QUBO(iadd_two))
    print()
    print("3-bit integer addition:")
    print(QUBO(iadd_three))
