# Generate truth tables for different operations.
from binary import int_to_binary

# Generate the truth table for signed integer addition.
def int_add_table(n_bits=2, signed=True, carry=True, wrap=False):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            # Compute the binary output of the operation.
            full_output = int_to_binary(i1+i2,signed=signed)
            output_val = int_to_binary(i1+i2,n_bits+carry,signed=signed,wrap=wrap)
            # If the full output requires too many bits, skip.
            if len(full_output) > n_bits+carry: continue
            # Add the entry to the truth table.
            truth_table.append((
                int_to_binary(i1,n_bits,signed=signed) +
                int_to_binary(i2,n_bits,signed=signed) +
                output_val ))
    return sorted(truth_table)

# Generate the truth table for unsigned integer addition.
def uint_add_table(**kwargs):
    kwargs["signed"] = False
    return int_add_table(**kwargs)

# Generate the truth table for unsigned integer multiplication.
def int_mult_table(n_bits=2, signed=True, wrap=False):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            # Add the entry to the truth table.
            truth_table.append((
                int_to_binary(i1,n_bits,signed=signed) +
                int_to_binary(i2,n_bits,signed=signed) +
                int_to_binary(i1*i2,n_bits,signed=signed,wrap=wrap) ))
    return sorted(truth_table)

# Generate the truth table for a unsigned integer multiplication.
def uint_mult_table(**kwargs):
    kwargs["signed"] = False
    return int_mult_table(**kwargs)


# Define an add circuit that has a carry-in bit.
def int_full_add_table(n_bits=2):
    truth_table = []
    for i in (0,1):
        for i1 in range(2**n_bits):
            for i2 in range(2**n_bits):
                # Add the entry to the truth table.
                truth_table.append((
                    int_to_binary(i1,n_bits,signed=False) +
                    int_to_binary(i2,n_bits,signed=False) + [i] + 
                    int_to_binary(i1+i2+i,n_bits+1,signed=False)))
    return sorted(truth_table)


# Given an arbitrary number of bits, generate the full set of bit
# combinations where each individual bit index satisfies an and gate.
def and_truth_table(num_bits):
    # Store the valid "AND" gate combinations.
    valid_ands = [
        [0, 0, 0],
        [0, 1, 0],
        [1, 0, 0],
        [1, 1, 1]
    ]
    truth_table = []
    for i in range(2**(3*num_bits)):
        bits = int_to_binary(i, bits=3*num_bits, signed=False)
        for b in range(num_bits):
            if (bits[b::num_bits] not in valid_ands): break
        else:
            # If we hit the "else" case, then all bit combinations
            # were valid and we should append this to the truth table.
            truth_table.append( bits )
            continue
        # We must have hit a "break", meaning this bits combo is invalid.
    # Return the constructed truth table.
    return truth_table



if __name__ == "__main__":
    
    FIND_INT_FULL_ADD_QUBO = True
    if FIND_INT_FULL_ADD_QUBO:
        # Find the solution QUBO and print it out.
        from solve import find_qubo, find_int_qubo
        from qubo import run_qubo, QUBO
        # Find the truth table for a specific arithmatic operation.
        b = 1
        tt = int_full_add_table(n_bits=b)
        print()
        for row in tt: print("",row)
        print()

        # Initial seed QUBO
        qubo = QUBO(a1=4**(b-1))
        # Solution energy gap.
        gap = 0.0
        print()
        print("Finding feasible solution..")
        # First find a real-valued solution to the problem.
        q = find_qubo(tt, random=False, gap=gap, qubo=qubo)
        print(q)
        print("Verifying solution..")
        sol = run_qubo(**q, display=False)
        if sol == tt:
            tt = sol
            print('-'*70)
            print("Using the following truth table to find integer solution:")
            for i,row in enumerate(tt): print("", row)
            # Find the integer form of the QUBO next.
            import math
            from utilities import round_pow_2
            q = find_int_qubo(tt, gap=gap, display=False, qubo=qubo, round=round_pow_2)
            # Check to make sure the outputs are correct.
            out = run_qubo(**q, display=False)
            if out == tt:
                print()
                print("Successfully found working integer QUBO!")
                print()
                # Print out the full table to the user.
                run_qubo(**q)
        else:
            print("Failed to match..")
            exit()
            sol = run_qubo(**q, min_only=False)


    TEST_CHECK_TT_FOR_MULT = False
    if TEST_CHECK_TT_FOR_MULT:
        b = 2
        # Generate the full truth table for "b" bit multiplication.
        tt = list(map(tuple,uint_mult_table(n_bits=b, carry=False)))
        print()
        print("Multplication truth table:")
        for row in tt: print("",row)
        # Generate the full truth table for "b" independent "and" gates.
        and_tt = list(map(tuple,and_truth_table(b)))
        # Find the cases that are in the truth table but violate "AND"
        need_to_zero = sorted(set(tt).difference(set(and_tt)))
        print()
        print("Rows that need to be zero'd:")
        for row in need_to_zero: print("",row)
        # Find the cases that are not in the truth table but are zero.
        need_to_grow = sorted(set(and_tt).difference(set(tt)))
        print()
        print("Rows that need to be grown:")
        for row in need_to_grow: print("",row)


    TEST_FIND_MULT_QUBO_FROM_TT = False
    if TEST_FIND_MULT_QUBO_FROM_TT:
        # Find the solution QUBO and print it out.
        from solve import find_qubo, find_int_qubo
        from qubo import run_qubo, QUBO
        # Find the truth table for a specific arithmatic operation.
        b = 2
        tt = uint_mult_table(n_bits=b, carry=False)
        print()
        for row in tt: print("",row)
        print()

        TEST_GIVEN_QUBO = False
        if TEST_GIVEN_QUBO:
            solutions = {
                 1 : {'b1b2': 1, 'a1': 0, 'a2': 0, 'b2b3': -2, 'a3': 3, 'b1b3': -2}
                ,2 : {'a2': 0, 'a4': 0, 'a6': 12, 'b2b4': 4, 'b2b6': -8, 'b4b6': -8, 'a5': 9, 'a7': 15, 'a1': 0, 'a3': 0, 'b3b4': 0, 'b5b6': -1, 'b3b7': -4, 'b4b5': -2, 'b3b6': 3, 'b3b5': -6, 'b2b7': -8, 'b4b7': 4, 'b2b3': 1, 'b2b5': -4, 'b1b3': 10, 'b5b7': 8, 'b1b4': 1, 'b1b5': -8, 'b1b2': 5, 'b1b6': 0, 'b1b7': -12, 'b6b7': 3}
            }
            q = QUBO(solutions[b])
            sol = run_qubo(**q, display=True)
            # Compare to the truth table (ignoring extra bits on the end).
            print("Passes?", all((v1 == v2) for (r1,r2) in zip(tt,sol) for (v1,v2) in zip(r1,r2)))
            exit()

        ADD_ANCILLA = True
        if ADD_ANCILLA:
            if b == 2:
                for row in tt: row += [0]
                # tt[3][-1] = 1 # Set the "y2, y1 = (1, 1)" ancilla bit.
                # tt[6][-1] = 1 # Set the "x1, y2 = (1, 1)" ancilla bit.
                # tt[9][-1] = 1 # Set the "x2, y1 = (1, 1)" ancilla bit.
                tt[10][-1] = 1 # Set the "x2, x1 = (1, 1)" ancilla bit.
            elif b == 3:
                # Set "x2, x1 = (1, 1)" and
                #     "x3, x2, x1 = (1, 1, 1)" cases
                for row in tt:
                    row += [0,0]
                    if (row[1] == row[2] == 1) and (sum(row[3:6])==0):
                        row[-1] = 1
                    if (row[0] == row[1] == 1) and (sum(row[3:6])==0):
                        row[-2] = 1
                    print(row)

        qubo = QUBO()
        # Set values manually to make pretty QUBOs.
        if b == 2:
            qubo = QUBO(a2=0, a4=0, a6=12,
                        b24=4, b26=-8, b46=-8,
                        a5=9, a7=15,
            )

        gap = 0.1
        print()
        print("Finding feasible solution..")
        # First find a real-valued solution to the problem.
        q = find_qubo(tt, random=False, gap=gap, qubo=qubo)
        print(q)
        print("Verifying solution..")
        sol = run_qubo(**q, display=False)
        if sol == tt:
            tt = sol
            print('-'*70)
            print("Using the following truth table to find integer solution:")
            for i,row in enumerate(tt): print("", row)
            # Find the integer form of the QUBO next.
            import math
            q = find_int_qubo(tt, gap=gap, display=False, qubo=qubo)
            # Check to make sure the outputs are correct.
            out = run_qubo(**q, display=False)
            if out == tt:
                print()
                print("Successfully found working integer QUBO!")
                print()
                # Print out the full table to the user.
                run_qubo(**q)
        else:
            print("Failed to match..")
            exit()
            sol = run_qubo(**q, min_only=False)


    TEST_LARGE_ADDITION = False
    if TEST_LARGE_ADDITION:
        # Find the solution QUBO and print it out.
        from integer import int_add
        from qubo import run_qubo, QUBO
        # Find the truth table for a specific arithmatic operation.
        b = 5
        tt = int_add_table(n_bits=b, signed=False)
        q = int_add(*list(range(1,3*b+1+1)))
        out = run_qubo(**q, display=False)
        print(tt == out)


    TEST_CONSTRAINT_GENERATION = False
    if TEST_CONSTRAINT_GENERATION:
        from solve import get_constraints, reduce_constraints
        # Find the truth table for a specific arithmatic operation.
        tt = int_add_table(n_bits=1, signed=False)
        print("Truth table:")
        print()
        for row in tt: print(row)
        print()

        # Compute the list of constraints for this truth table.
        from solve import get_constraints
        eq_zero, gt_zero, min_energy = get_constraints(tt)
        reduce_constraints(eq_zero, gt_zero)

        # Print out the equality constraints (sorted by length then terms).
        print('-'*70)
        eq_zero = sorted(eq_zero,key=lambda k: tuple(sorted(k)))
        eq_zero = sorted(eq_zero,key=lambda k: len(k))
        for row in eq_zero:
            print("0 ="," + ".join(sorted(row)))
        print()

        # Print out the inequality constraints (sorted by length then terms).
        gt_zero = sorted(gt_zero,key=lambda k: tuple(sorted(k)))
        gt_zero = sorted(gt_zero,key=lambda k: len(k))
        for row in sorted(gt_zero,key=lambda k: len(k)):
            print("0 <"," + ".join(sorted(row)))
        print('-'*70)

