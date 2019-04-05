# Python 3 functions for converting a truth table into a QUBO.
# Use the function 'find_qubo'.


# Find the optimal QUBO for the given truth table. Steadily add ancilla bits,
# trying every combination of ancilla bits, until a solution is found.
#
# Input: table should be a python list of lists, containing "valid" rows
#        for the truth table. I.e., for an OR gate (q1 OR q2 = q3)
#        table = [[0,0,0], [1,0,0], [0,1,0], [1,1,1]].
# Output: returns a QUBO object. If the table cannot be solved, 
#         ancilla bits are appended until it can.
def find_qubo(truth_table, max_attempts=float('inf'), random=True,
              ancilla=True, qubo={}):
    from rand import random_range
    from binary import int_to_binary
    from exceptions import UnsolvableSystem
    # Get the number of bits in this problem.
    num_bits = len(truth_table[0])
    # Generate equality and inequality constraints from that truth table.
    eq_min, gt_min, min_energy = get_constraints(truth_table)
    # Reduce the set of constraints as much as possible.
    eq_min, gt_min = reduce_constraints(eq_min, gt_min)
    # Try to find a solution with no ancilla bits.
    q, ierr = solve_qubo(num_bits, eq_min, gt_min, min_energy, qubo)
    if (ierr == 0):     return q
    elif (not ancilla): raise(UnsolvableSystem(f"Could not find a solution, error code {ierr}."))
    # No solution was found. Get meta data about table.
    num_entries = len(truth_table)
    # Add ancilla bits until a solution is found.
    for i in range(1, num_entries+1):
        # Append zeros to truth table.
        for j in range(0, num_entries): truth_table[j].append(0)
        to_add = [0]*num_entries*i
        # Loop through all combinations of ancilla bits.
        max_attempts = min(2**(num_entries*i), max_attempts)
        # Construct the ancillary bit value generator.
        if random: generator = random_range(1,2**(n*i)-1,count=max_attempts)
        else:      generator = range(1,2**(num_entries*i)-1)
        # Cycle through different ancillary bit values.
        for step,j in enumerate(generator):
            # Add one to the binary digit.
            to_add = int_to_binary(j, bits=num_entries*i, signed=False)
            # Map binary number onto table.
            for l in range(0, num_entries):
                for k in range(0, i):
                    truth_table[l][num_bits+k] = to_add[l+k*i]
            # Finally, attempt to solve the problem using this
            # combination of ancilla bits.
            print(f"Trying {i} ancillary bit{'s' if i > 1 else ''}.. ({step+1}:{max_attempts}) {to_add}", end="\r", flush=True)
            # Generate a truth table for correct solutions.
            # Generate equality and inequality constraints from that truth table.
            eq_min, gt_min, min_energy = get_constraints(truth_table)
            # Reduce the set of constraints as much as possible.
            eq_min, gt_min = reduce_constraints(eq_min, gt_min)
            # Try to find a solution with no ancilla bits.
            q, ierr = solve_qubo(num_bits+i, eq_min, gt_min, min_energy, qubo)
            if ierr == 0:
                print(" "*70, end="\r", flush=True)    
                return q
    # If no successful solution was found, raise an error.
    class FailedToFindQUBO(Exception): pass
    raise(FailedToFindQUBO("Could not find QUBO for given truth table."))


# Generate a QUBO from a truth table by solving a linear programming problem.
def solve_qubo(num_bits, eq_min, gt_min, min_energy, qubo={}):
    from exceptions import UnsolvableSystem
    from scipy.optimize import linprog
    # Allocate input arrays.
    gt_min_bits = []
    eq_min_bits = []
    gt_min_values = []
    eq_min_values = []
    # The "objective function" is flat for this linear program,
    # because we are only interested in solving the constraints.
    obj_func = [0.0,]*int(num_bits*(num_bits+1)/2)
    # Cycle through an construct the equality constraints.
    for terms in eq_min:
        # Initialize the energy to the minimum value and all bits to 0.
        energy = min_energy
        bits = [0]*(num_bits * (num_bits+1) // 2)
        for coef in terms:
            if coef in qubo: energy -= qubo[coef]
            else:            bits[coef_to_index(coef, num_bits)] = 1
        # Check for an unsolvable or empty system.
        if (sum(bits) == 0):
            if (energy != min_energy):
                raise(UnsolvableSystem("The provided system has a contradictory equality constraint."))
            # Skip the addition of this row because it has no values.
            continue
        # Check to see if this row already exists in the set of rows.
        if bits in eq_min_bits:
            index = eq_min_bits.index(bits)
            if (energy != eq_min_values[index]):
                raise(UnsolvableSystem("The provided system has contradicting equality constraints."))
        else:
            # Add this set of bits and energy to the equality constraints.
            eq_min_bits.append( bits )
            eq_min_values.append( energy )
    # Cycle through an construct the inequality constraints.
    for terms in gt_min:
        # Initialize the energy to the minimum value and all bits to 0.
        energy = -min_energy
        bits = [0]*(num_bits * (num_bits+1) // 2)
        for coef in terms:
            if coef in qubo: energy += qubo[coef]
            else:            bits[coef_to_index(coef, num_bits)] = -1
        # Check for an unsolvable or empty system.
        if (sum(bits) == 0):
            if (energy < 0):
                raise(UnsolvableSystem("The provided system has a contradictory inequality constraint."))
            # Skip the addition of this row because it has no values.
            continue
        # Check to see if this row already exists in the set of rows.
        if bits in gt_min_bits:
            # If so, then keep the larger of the two constraint energies.
            index = gt_min_bits.index(bits)
            gt_min_values[index] = min(gt_min_values[index], energy)
        else:
            # Add this set of bits and energy to the equality constraints.
            gt_min_bits.append( bits )
            gt_min_values.append( energy )
    # Compute the answer with scipy.linprog.
    res = linprog(obj_func, A_ub=gt_min_bits, b_ub=gt_min_values, 
                  A_eq=eq_min_bits, b_eq=eq_min_values,
                  bounds=(None,None), method='interior-point')
    # Get the solution QUBO.
    q = weights_to_qubo(num_bits, res.x)
    # Transfer the provided weights back into the solution QUBO.
    q.update(qubo)
    # Return the solution and status.
    return q, res.status


# Given a coefficient in mathematical terms "a1", "b2b3", convert it
# to an index in an array stored as [a1, a2, ... , b1b2, b1b3, ...].
def coef_to_index(coef, num_bits):
    from exceptions import UsageError
    if coef[0] == "a":
        return int(coef[1:]) - 1
    elif coef[0] == "b":
        i1, i2 = map(int, coef[1:].split('b'))
        i1, i2 = i1-1, i2-1
        index = num_bits-1
        for i in range(num_bits-1):
            for j in range(i+1,num_bits):
                index += 1
                if (i == i1) and (j == i2):
                    return index
        else:
            raise(UsageError(f"Index for '{coef}' out of expected {num_bits} bit range."))
    raise(UsageError(f"Unrecognized coefficient '{coef}'."))


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


# Given a list of sets, where each set looks like {a#, ..., b#b#},
# remove all subsets from each other.
def reduce_constraints(eq_min, gt_min):
    changed = True
    while changed:
        changed = False
        # Remove all empty sets from the zero rows.
        while (set() in eq_min): eq_min.remove(set())
        # Cycle through all master sets and subsets, removing "0"s.
        for i,group in enumerate(eq_min):
            for j,other_group in enumerate(eq_min):
                if (i == j): continue
                if group.issuperset( other_group ):
                    changed = True
                    # Remove all elements of "other group" from "group",
                    # since their sum is equal to zero.
                    for v in other_group: group.remove(v)
    equal_constraints = sorted(eq_min)
    for ineq_group in gt_min:
        for eq_group in equal_constraints:
            if ineq_group.issuperset( eq_group ):
                # Remove all elements of "other group" from "group",
                # since their sum is equal to zero.
                for v in eq_group: ineq_group.remove(v)
    return eq_min, gt_min


# Generate a constraint set for a QUBO from a truth table.
# Table should be a python list whose rows are valid entries in the truth table.
def get_constraints(table):
    # Get meta data about table.
    num_bits = len(table[0])
    # Allocate input arrays.
    gt_min = []
    eq_min = []
    # Initialize search array.
    entry = [0,]*num_bits
    # Minimum energy must be 0 if the "0" entry is in the table.
    if entry in table: min_energy = 0
    # Minimum energy must be less than 0 (WLOG, set to -1).
    else:              min_energy = -1
    # Process truth table to generate constraint equations.
    for i in range(1, 2**num_bits):
        # Increment the entry to search for.
        entry[0] += 1
        # Count up in binary.
        for j in range(0, num_bits):
            if entry[j] > 1:
                entry[j] = 0
                entry[j+1] += 1
        # Initialize next set in list, containing all active terms.
        next_set = set()
        # Fill in all a_j values.
        for j in range(0, num_bits):
            if entry[j] == 1:
                next_set.add('a'+str(j+1))
        # Fill in all b_jk values.
        for j in range(0, num_bits): 
            for k in range(j+1, num_bits):
                if entry[j]*entry[k] == 1:
                    next_set.add('b'+str(j+1)+'b'+str(k+1))
        # Add the constraint sets to the appropriate lists.
        if entry in table:  eq_min.append(next_set)
        else:               gt_min.append(next_set)
    # Return the sets.
    return eq_min, gt_min, min_energy
