# Python 3 functions for converting a truth table into a QUBO.
# Use the function table2qubo.

from rand import random_range
from binary import int_to_binary

# Find the optimal QUBO for the given truth table. Steadily add ancilla bits,
# trying every combination of ancilla bits, until a solution is found.
#
# Input: table should be a python list of lists, containing "valid" rows
#        for the truth table. I.e., for an OR gate (q1 OR q2 = q3)
#        table = [[0,0,0], [1,0,0], [0,1,0], [1,1,1]].
# Output: returns a list of weights [a1, ..., an, b12, ..., b1n, ..., bnn]
#         for generating the QUBO. If the table cannot be solved, ancilla
#         bits are appended until it can. On output, table shows the valid
#         values for those ancilla bits.
#
# Author: Tyler Chang
# Last Update: 4/3/19
def find_qubo(truth_table, max_attempts=float('inf')):
    # Make a copy / ensure the input is a python list.
    table = list(map(list, truth_table))
    # Try to find a solution with no ancilla bits.
    weights, ierr = solve_qubo(table)
    if ierr == 0: return weights_to_qubo(len(table[0]), weights)
    # No solution was found. Get meta data about table.
    n = len(table)
    m = len(table[0])
    # Add ancilla bits until a solution is found.
    for i in range(1, n+1):
        # Append zeros to truth table.
        for j in range(0, n): table[j].append(0)
        to_add = [0]*n*i
        # Loop through all combinations of ancilla bits.
        max_attempts = min(2**(n*i), max_attempts)
        for step,j in enumerate(random_range(1,2**(n*i)-1,count=max_attempts)):
            # Add one to the binary digit.
            to_add = int_to_binary(j, bits=n*i, signed=False)
            # Map binary number onto table.
            for l in range(0, n):
                for k in range(0, i):
                    table[l][m+k] = to_add[l+k*i]
            # Finally, attempt to solve the problem using this
            # combination of ancilla bits.
            print(f"Trying {i} ancillary bit{'s' if i > 1 else ''}.. ({step+1}:{max_attempts}) {to_add}", end="\r", flush=True)
            weights, ierr = solve_qubo(table)
            if ierr == 0:
                print(" "*70, end="\r", flush=True)    
                return weights_to_qubo(len(table[0]), weights)
    # If no successful solution was found, raise an error.
    class FailedToFindQUBO(Exception): pass
    raise(FailedToFindQUBO("Could not find QUBO for given truth table."))


# Given weights produced by "make_qubo", return a QUBO object
def weights_to_qubo(num_bits, weights):
    from itertools import combinations
    from qubo import QUBO
    weights = list(weights)
    q = QUBO()
    for i,w in zip(range(num_bits), weights):
        q[f"a{i+1}"] = w
    for (i1, i2), w in zip(combinations(range(num_bits),2), weights[num_bits:]):
        q[f"b{i1+1}b{i2+1}"] = w
    return q

# Generate a QUBO from a truth table by solving a linear programming problem.
# Table should be a python list whose rows are valid entries in the truth table.
# Private function to be referenced by table2qubo.
# Author: Tyler Chang
# Last Update: 4/3/19
def solve_qubo(table):
    from scipy.optimize import linprog
    # Get meta data about table.
    m = len(table[0])
    # Allocate input arrays.
    A = []
    E = []
    Ab = []
    Eb = []
    # The "objective function" is flat for this linear program,
    # because we are only interested in solving the constraints.
    c = [0.0,]*int(m*(m+1)/2)
    # Initialize search array.
    entry = [0.0,]*m
    # Minimum energy must be 0 if the "0" entry is in the table.
    if entry in table: minenergy = 0.0
    # Minimum energy must be less than 0 (WLOG, set to -1).
    else:              minenergy = -1.0
    # Process truth table to generate constraint equations.
    for i in range(1, 2**m):
        # Increment the entry to search for.
        entry[0] += 1.0
        # Count up in binary.
        for j in range(0, m): 
            if entry[j] > 1.0:
                entry[j] = 0.0
                entry[j+1] += 1.0
        # Initialize next 'row', holding 1's for all active terms in QUBO.
        next_row = [0.0,]*int(m*(m+1)/2)
        # Set all a_j values.
        next_row[0:m] = entry[0:m]
        # Initialize index.
        index = m
        # Set all b_jk values.
        for j in range(0, m): 
            for k in range(j+1, m):
                next_row[index] = entry[j]*entry[k]
                index += 1
        # Set the constraint appropriately.
        if entry in table:
            # If the user wants this case to have minimum energy...
            A.append([0.0,]*int(m*(m+1)/2))
            Ab.append(0.0)
            E.append(next_row)
            Eb.append(minenergy)
        else:
            # Otherwise the energy of this state must be >0.
            A.append(next_row)
            Ab.append(minenergy+1.0)
            E.append([0.0,]*int(m*(m+1)/2))
            Eb.append(0.0)
    # Flip all of the bound constraints on A and Ab to be negative.
    for i in range(0, len(A)):
        for j in range(0, len(A[i])): A[i][j] *= -1.0
    for i in range(0, len(Ab)): Ab[i] *= -1.0
    # Compute the answer with scipy.linprog.
    res = linprog(c, A_ub = A, b_ub = Ab, A_eq = E, b_eq = Eb,
                  bounds=(None,None), method='interior-point')
    # Return the solution and status.
    return res.x, res.status
