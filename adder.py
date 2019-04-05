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
    full_qubo = half_adder(bit_indices[n-1], bit_indices[2*n-1], 
                           bit_indices[3*n-1], bit_indices[4*n-1])
    for i in range(n-1): 
        full_qubo += full_adder(bit_indices[i], bit_indices[i+n], 
                                bit_indices[i+3*n+1], #carry bit
                                bit_indices[i+2*n], bit_indices[i+3*n])
    return full_qubo
 
    
# Given bit indices x1,x2,..,xn,y1,y2,...ym,s1,s2,...sn,c1,c2,...cn
# where n>m.
# Generate a QUBO for x, y, s, c such that x+y = c1,s
# Uses 3n+m qubits 
def skewed_two_int_adder(n,m,*bit_indices):
    if n<m: 
        raise UsageError('It is required that n>=m')
    elif len(bit_indices)!=3*n+m:
        raise UsageError('No. of input indices should be 3n+m.')
    final_qubo = half_adder(bit_indices[n-1], bit_indices[n-1+m],
                            bit_indices[2*n-1+m], bit_indices[3*n-1+m])
    for i in range(m-1):
        final_qubo += full_adder(bit_indices[n-m+i], bit_indices[n+i],
                                 bit_indices[3*n+i+1],
                                 bit_indices[2*n+i], bit_indices[3*n+i])
    for i in range(n-m):
        final_qubo += half_adder(bit_indices[i], bit_indices[2*n+m+i+1],
                                 bit_indices[n+m+i], bit_indices[2*n+m+i])
    return final_qubo
    

# Find the total no. of qubits required by m_int_adder() for given m,n
def num_qb_m_int_adder(m, n):
    pass
    

# Given bit indices 
# x11, x12, ..., x1n
# x21, x22, ..., x2n
# .
# .
# xm1, xm2, ..., xmn
# ...many ancilla bits...
# c1
def m_int_adder(m,n,*bit_indices):
    curr_anc_pos = m*n
    curr_sums = [(i,m) for i in range(n)] #(start, length)
    final_qubo = QUBO()
    while len(curr_sums)>1:
        new_sums = []
        for i in range(0,len(curr_sums)-1,2):
            s1, l1 = curr_sums[i]
            s2, l2 = curr_sums[i+1]
            final_qubo += skewed_two_int_adder(l1, l2, 
                                 *(bit_indices[s1:s1+l1]+bit_indices[s2:s2+l2]
                                 +bit_indices[curr_anc_pos+l1:curr_anc_pos+2*l1]
                                 +bit_indices[curr_anc_pos+l1-1:curr_anc_pos+l1] #MSC
                                 +bit_indices[curr_anc_pos:curr_anc_pos+l1-1]))    
            new_sums.append((curr_anc_pos,l1+1))
            curr_anc_pos += 2*l1
        if len(curr_sums)%2==1:
            new_sums.append(curr_sums[-1])
        curr_sums = new_sums.copy()
    return final_qubo


    


if __name__=='__main__':
    print ('=====half-adder')
    run_qubo(**half_adder())
    print ('=====full-adder')
    run_qubo(**full_adder())
    print ('=====two n-bit integer addition with 4n qubits')
    bit_indices = list(range(1,4*2+1))
    run_qubo(**two_int_adder_4n(*bit_indices))
    print ('=====two n,m bit integer addition with 3*n+m qubits')
    n,m = 2,2
    bit_indices = list(range(1,3*n+m+1))
    run_qubo(**skewed_two_int_adder(n,m,*bit_indices))
    



## alternate implementation of two_int_adder_4n unrolling the 
# addition of adders
#def two_int_adder_4n(*bit_indices):
#    qubo_rep = dict()
#    for i in range(n):
#        qubo_rep[f"a{bit_indices[i]}"] = 1
#        qubo_rep[f"a{bit_indices[i+n]}"] = 1
#        qubo_rep[f"a{bit_indices[i+2*n]}"] = 1
#        qubo_rep[f"a{bit_indices[i+3*n]}"] = 5 #adjusted later for c1
#        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+n]}"] = 2
#        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+2*n]}"] = -2
#        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+3*n]}"] = -4
#        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+2*n]}"] = -2
#        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+3*n]}"] = -4
#        qubo_rep[f"b{bit_indices[i+2*n]}b{bit_indices[i+3*n]}"] = 4
#    qubo_rep[f"a{bit_indices[3*n]}"] = 4
#    for i in range(n-1):
#        qubo_rep[f"b{bit_indices[i]}b{bit_indices[i+1+3*n]}"] = 2
#        qubo_rep[f"b{bit_indices[i+n]}b{bit_indices[i+1+3*n]}"] = 2
#        qubo_rep[f"b{bit_indices[i+2*n]}b{bit_indices[i+1+3*n]}"] = -2
#        qubo_rep[f"b{bit_indices[i+3*n]}b{bit_indices[i+1+3*n]}"] = -4
#    return QUBO(qubo_rep)
