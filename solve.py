# Python 3 functions for converting a truth table into a QUBO.
# Use the function 'find_qubo'.
from qubo import QUBO

# Find the optimal QUBO for the given truth table. Steadily add ancilla bits,
# trying every combination of ancilla bits, until a solution is found.
#
# Input: table should be a python list of lists, containing "valid" rows
#        for the truth table. I.e., for an OR gate (q1 OR q2 = q3)
#        table = [[0,0,0], [1,0,0], [0,1,0], [1,1,1]].
# Output: returns a QUBO object. If the table cannot be solved, 
#         ancilla bits are appended until it can.
def find_qubo(truth_table, max_attempts=float('inf'), random=True,
              ancilla=True, qubo=QUBO(), gap=0.0, verbose=False):
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
    q, ierr = solve_qubo(num_bits, eq_min, gt_min, min_energy, qubo,
                         gap=gap, verbose=verbose)
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
        if random: generator = random_range(1,2**(num_entries*i)-1,count=max_attempts)
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
            try:
                # Try to find a solution with no ancilla bits.
                q, ierr = solve_qubo(num_bits+i, eq_min, gt_min,
                                     min_energy, qubo, gap=gap, verbose=verbose)
                if ierr == 0:
                    print(" "*70, end="\r", flush=True)    
                    return q
            except Exception as exc:
                if verbose: print("Failed:", exc)
    # If no successful solution was found, raise an error.
    class FailedToFindQUBO(Exception): pass
    raise(FailedToFindQUBO("Could not find QUBO for given truth table."))


# Generate a QUBO from a truth table by solving a linear programming problem.
def solve_qubo(num_bits, eq_min, gt_min, min_energy, qubo=QUBO(),
               gap=0.0, verbose=False):
    from exceptions import UnsolvableSystem
    from scipy.optimize import linprog
    # Capture the standard output and error of linprog.
    # Allocate input arrays.
    gt_min_bits = []
    eq_min_bits = []
    gt_min_values = []
    eq_min_values = []
    # The "objective function" is flat for this linear program,
    # because we are only interested in solving the constraints.
    obj_func = [0.0,]*int(num_bits*(num_bits+1)/2)

    # Sort the terms reasonably for printouts if we are verbose.
    if verbose:
        eq_min = sorted(sorted(t) for t in eq_min)
        eq_min.sort(key = lambda i: len(i))
        print('-'*70)
        print("Equality constraints:")

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
            if verbose: print("",f"{energy: .2f}","=", " + ".join([qubo.get(t, t) for t in sorted(terms)]))
            # Add this set of bits and energy to the equality constraints.
            eq_min_bits.append( bits )
            eq_min_values.append( energy )

    # Sort the terms reasonably for printouts if we are verbose.
    if verbose:
        print()
        print("Inquality constraints:")
        gt_min = sorted(sorted(t) for t in gt_min)
        gt_min.sort(key = lambda i: len(i))

    # Cycle through an construct the inequality constraints.
    for terms in gt_min:
        # Initialize the energy to the minimum value and all bits to 0.
        energy = -min_energy-gap
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
            # If so, then keep the larger (negative) of the two constraint energies.
            index = gt_min_bits.index(bits)
            gt_min_values[index] = min(gt_min_values[index], energy)
        else:
            if verbose:
                print("", f"{-energy: .2f}","<", " + ".join([qubo.get(t, t) for t in sorted(terms)]))
            # Add this set of bits and energy to the equality constraints.
            gt_min_bits.append( bits )
            gt_min_values.append( energy )
    if verbose: print('-'*70)

    # Check to make sure we weren't provided a solved system.
    if (len(eq_min_bits) == 0) and (len(gt_min_bits) == 0): return qubo, 0
    # Compute the answer with scipy.linprog.
    try:
        if verbose: print()
        res = linprog(obj_func, A_ub=gt_min_bits, b_ub=gt_min_values, 
                      A_eq=eq_min_bits, b_eq=eq_min_values,
                      bounds=(None,None), method="interior-point")
        if verbose:
            print()
            print(res)
            print()
    except Exception as exc:
        # Print out more helpful information about the failure.
        if verbose:
            print()
            print("ERROR: Failed linprog with equality and inequality constraints:")
            eq_str = "  " + "  \n".join(map(lambda p: f"{p[0]}  {p[1]}", zip(eq_min_bits,eq_min_values)))
            print(eq_str)
            print()
            gt_str = "  " + "  \n".join(map(lambda p: f"{p[0]}  {p[1]}", zip(gt_min_bits,gt_min_values)))
            print(gt_str)
            print()
        # Continue raising the exception.
        raise(exc)
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



# Given a truth table that is solvable without the addition of any
# ancilla bits, identify an integer-only set of coefficients.
def find_int_qubo(truth_table, qubo=QUBO(), display=False,
                  max_coef=1000, max_seed=2, gap=0.0, round=round):
    from utilities import primes_up_to, cycle_coefs
    from qubo import run_qubo
    from exceptions import UnsolvableSystem
    # Make sure the provided QUBO is not movified in place.
    qubo = qubo.copy()
    # Find the initial set of coefficients that solves this truth
    # table. Deliberately do not catch any errors!
    q = find_qubo(truth_table, ancilla=False, qubo=qubo, gap=gap)
    # Verify the solution by running through an exhaustive simulator.
    sol = run_qubo(**q, display=False)
    if (sol != truth_table):
        out_str = "\n".join(map(lambda pair: str(pair[0]) + "  " + str(pair[1]), zip(truth_table,sol)))
        raise(UnsolvableSystem(f"The computed QUBO does not produce expected output.\n\n{out_str}"))
    # Cycle reasonable seed coefficients if nothing was provided.
    if (len(qubo) == 0):
        print(q)
        # Cycle through coefficients in this QUBO.
        for coef in cycle_coefs(q, len(truth_table[0])):
            # Skip nonzero coefficients.
            if (q[coef] == 0): continue
            # Generate a list of reasonable starting values for 'a'.
            for val in primes_up_to(max_seed):
                # Find a value that is nonzero to round to 'val'.
                if   (q[coef] < 0):
                    qubo[coef] = -val
                elif (q[coef] > 0):
                    qubo[coef] = val
                # Print out to the user an update if desired.
                if display:
                    print("-"*70)
                    print(f" Trying to solve for integer QUBO with:")
                    print(f"    {coef} = {qubo[coef]}")
                # Try to solve the problem with this starting value for 'a'.
                try:
                    qubo = find_int_qubo(truth_table, qubo, display=display, 
                                         max_coef=max_coef, gap=gap, round=round)
                    if display: print("Sucess!\n")
                    return qubo
                except Exception as exc:
                    print(coef, val, exc)
                    # Remove the added coefficient because it must have failed.
                    qubo.pop(coef)
                if display: print()
        raise(UnsolvableSystem("Could not solve system after attempting all reasonable seed values."))
    # Loop trying to make other coefficients to integers.
    while (len(qubo) < len(q)):
        # Check to see that we don't have unreasonably large values.
        if (max(qubo.values()) >= max_coef):
            raise(UnsolvableSystem(f"Could not find a solution with all coefficients smaller than {max_coef}."))
        # Find the coefficient that is closest to being an integer.
        chosen_coef = None
        dist_to_int = float('inf')
        for coef in q: 
            # Skip coefficients that have already been set.
            if coef in qubo: continue
            dist = abs(round(q[coef]) - q[coef])
            # If this is a new nearest, store it.
            if dist < dist_to_int: chosen_coef, dist_to_int = coef, dist
        # Set that value to its nearest integer.
        qubo[chosen_coef] = int(round(q[chosen_coef]))
        # Check to see if this change works, if it does, then keep it.
        new_q = q.copy()
        new_q.update(qubo)
        sol = run_qubo(**new_q, display=False)
        if (sol == truth_table): continue
        # Otherwise, try and solve the system again with robust code.
        try:
            q = find_qubo(truth_table, ancilla=False, qubo=qubo, gap=gap)
            # Verify the solution by running through an exhaustive simulator.
            sol = run_qubo(**q, display=False)
            if (sol != truth_table):
                out_str = "\n".join(map(lambda pair: str(pair[0]) + "  " + str(pair[1]), zip(truth_table,sol)))
                raise(UnsolvableSystem(f"The computed QUBO does not produce expected output.\n\n{out_str}"))
        except Exception as exc:
            if display:
                print()
                print(q)
                print(f"Tried setting {chosen_coef} = {qubo[chosen_coef]}.")
                print("Failed.")
            # Remove the previously added coefficient.
            qubo.pop(chosen_coef)
            # Multiply all existing integers by 2.
            for coef in qubo: qubo[coef] *= 2
            # Find the new qubo values associated with these doubled constants.
            q = find_qubo(truth_table, ancilla=False, qubo=qubo, gap=gap)
            # Verify the solution by running through an exhaustive simulator.
            sol = run_qubo(**q, display=False)
            if (sol != truth_table):
                out_str = "\n".join(map(lambda pair: str(pair[0]) + "  " + str(pair[1]), zip(truth_table,sol)))
                raise(UnsolvableSystem(f"The doubled QUBO that previously succeeded failed.\n\n{out_str}"))
    # Return the all-integer valued qubo.
    return qubo
