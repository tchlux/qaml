from qubo import QUBO
from logic import half_adder, full_adder
from exceptions import UsageError


# Given an arbitrary number of bit indices, assume they represent a
# big-endian integer. Generate a QUBO that minimizes this integer.
def uint_min(*bit_indices):
    return QUBO({f"a{b}" : 2**(len(bit_indices)-i-1)
                 for i,b in enumerate(bit_indices)})

# Given bit indices x1,x2,..,xn,y1,y2,...yn,s1,s2,...sn,c1,c2,...cn
# Generate a QUBO for x = y = s + 2c. Each of x, y, s, c is n bits wide.
# Uses 4n qubits, qubo derived by adding qubos for 1 half-adder and n-1 full-adders.
def uint_add(*bit_indices):
    if len(bit_indices)%4!=0:
        raise UsageError('No. of input indices should be a multiple of 4.')
    n = len(bit_indices) // 4
    full_qubo = half_adder(bit_indices[n-1], bit_indices[2*n-1], 
                           bit_indices[3*n-1], bit_indices[4*n-1])
    for i in range(n-1): 
        full_qubo += full_adder(bit_indices[i], bit_indices[i+n], 
                                bit_indices[i+3*n+1], #carry bit
                                bit_indices[i+2*n], bit_indices[i+3*n])
    return full_qubo

