# Python 3 functions for converting a truth table into a QUBO.
# Use the function table2qubo.

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
def table2qubo(table):
    # Try to find a solution with no ancilla bits.
    [weights,ierr] = findqubo(table)
    if ierr == 0:
        return weights
    # No solution was found. Get meta data about table.
    n = len(table)
    m = len(table[0])
    # Add ancilla bits until a solution is found.
    for i in range(1, n+1):
        # Append zeros to truth table.
        for j in range(0,n): table[j].append(0)
        to_add = [0]*n*i
        # Loop through all combinations of ancilla bits.
        for j in range(1,2**(n*i)-1):
            # Add one to the binary digit.
            to_add[0] += 1
            # Count up in binary.
            for k in range(0, n*i): 
                if to_add[k] > 1:
                    to_add[k] = 0
                    to_add[k+1] += 1
            # Map binary number onto table.
            for l in range(0, n):
                for k in range(0, i): table[l][m+k] = to_add[l+k*i]
            # Finally, attempt to solve the problem using this combination of
            # ancilla bits.
            [weights,ierr] = findqubo(table)
            if ierr == 0:
                return weights
    return -1

# Generate a QUBO from a truth table by solving a linear programming problem.
# Table should be a python list whose rows are valid entries in the truth table.
# Private function to be referenced by table2qubo.
# Author: Tyler Chang
# Last Update: 4/3/19
def findqubo(table):
    from scipy.optimize import linprog
    # Get meta data about table.
    n = len(table)
    m = len(table[0])
    # Allocate input arrays.
    A = []
    E = []
    Ab = []
    Eb = []
    c = [0.0,]*int(m*(m+1)/2)
    # Initialize search array.
    entry = [0.0,]*m
    # Initialize the minimum energy and allocate constraint arrays.
    if entry in table:
        # Minimum energy must be 0.
        minenergy = 0.0
    else:
        # Minimum energy must be less than 0 (WLOG, set to -1).
        minenergy = -1.0
    # Process truth table to generate constraint equations.
    for i in range(1, 2**m):
        # Increment the entry to search for.
        entry[0] += 1.0
        # Count up in binary.
        for j in range(0, m): 
            if entry[j] > 1.0:
                entry[j] = 0.0
                entry[j+1] += 1.0
        # Initialize next row.
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
            A.append([0.0,]*int(m*(m+1)/2))
            Ab.append(0.0)
            E.append(next_row)
            Eb.append(minenergy)
        else:
            A.append(next_row)
            Ab.append(minenergy+1.0)
            E.append([0.0,]*int(m*(m+1)/2))
            Eb.append(0.0)
    for i in range(0, len(A)):
        for j in range(0, len(A[i])): A[i][j] *= -1.0
    for i in range(0, len(Ab)): Ab[i] *= -1.0
    res = linprog(c, A_ub = A, b_ub = Ab, A_eq = E, b_eq = Eb, bounds=(None,None))
    return [res.x, res.status]
