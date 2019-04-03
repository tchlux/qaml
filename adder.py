from qubo import QUBO
from qubo import run_qubo
from exceptions import UsageError
from logic import full_adder, half_adder


# Given bit indices x1,x2,..,xn,y1,y2,...yn,s1,s2,...sn,c1,c2,...cn
# Generate a QUBO for x, y, s, c.
# Each of x, y, s, c is n bits wide.
# Uses 4n qubits, qubo derived by adding qubos for 
# 1 half-adder and n-1 full adders
def two_int_adder_4n(*bit_indices):
    if len(bit_indices)%4!=0:
        raise UsageError('No. of input indices should be a multiple of 4.')
    n = len(bit_indices) // 4
#    full_qubo = half_adder(bit_indices[n-1], bit_indices[2*n-1], 
#                           bit_indices[3*n-1], bit_indices[4*n-1])
#    for i in range(n-1): 
#        full_qubo += full_adder(bit_indices[i], bit_indices[i+n], 
#                                bit_indices[i+3*n+1], #carry bit
#                                bit_indices[i+2*n], bit_indices[i+3*n])
#    return full_qubo
    qubo_rep = dict()
    for i in range(n):
        qubo_rep[f"a{bit_indices[i]}"] = 1
        qubo_rep[f"a{bit_indices[i+n]}"] = 1
        qubo_rep[f"a{bit_indices[i+2*n]}"] = 1
        qubo_rep[f"a{bit_indices[i+3*n]}"] = 5 #adjusted later for c1
        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+n]}"] = 2
        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+2*n]}"] = -2
        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+3*n]}"] = -4
        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+2*n]}"] = -2
        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+3*n]}"] = -4
        qubo_rep[f"b{bit_indices[i+2*n]}b{bit_indices[i+3*n]}"] = 4
    qubo_rep[f"a{bit_indices[3*n]}"] = 4
    for i in range(n-1):
        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+1+3*n]}"] = 2
        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+1+3*n]}"] = 2
        qubo_rep[f"b{bit_indices[i+2*n]}b{bit_indices[i+1+3*n]}"] = -2
        qubo_rep[f"b{bit_indices[i+3*n]}b{bit_indices[i+1+3*n]}"] = -4
    return QUBO(qubo_rep)
    
    
if __name__=='__main__':
    print ('=====half-adder')
    run_qubo(**half_adder())
    print ('=====full-adder')
    run_qubo(**full_adder())
    print ('=====two n-bit integer addition with 4n qubits')
    bit_indices = list(range(1,4*2+1))
    run_qubo(**two_int_adder_4n(*bit_indices))

