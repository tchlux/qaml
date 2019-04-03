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


