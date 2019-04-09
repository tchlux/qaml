# Generate truth tables for different operations.
from binary import int_to_binary

# Generate the truth table for signed integer addition.
def int_add_table(n_bits=2, signed=True, carry=True):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            # Compute the binary output of the operation.
            output_val = int_to_binary(i1+i2,n_bits+1,signed=signed)
            if carry or (output_val[signed] == 0):
                # Pop out the "carry" bit if it is not desired.
                if (not carry): output_val.pop(signed)
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
def int_mult_table(n_bits=2, signed=True, carry=False):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            # Compute the binary output of the operation.
            output_val = int_to_binary(i1*i2,1+n_bits,signed=signed)
            if carry or (output_val[signed] != 1):
                # Pop out the "carry" bit if it is not desired.
                if (not carry): output_val.pop(signed)
                # Add the entry to the truth table.
                truth_table.append((
                    int_to_binary(i1,n_bits,signed=signed) +
                    int_to_binary(i2,n_bits,signed=signed) +
                    output_val ))
    return sorted(truth_table)

# Generate the truth table for a unsigned integer multiplication.
def uint_mult_table(**kwargs):
    kwargs["signed"] = False
    return int_mult_table(**kwargs)


if __name__ == "__main__":
    
    TEST_FIND_QUBO_FOR_TT = True
    if TEST_FIND_QUBO_FOR_TT:
        # Find the solution QUBO and print it out.
        from solve import find_qubo, find_int_qubo
        from qubo import run_qubo, QUBO
        # Find the truth table for a specific arithmatic operation.
        tt = uint_mult_table(n_bits=1, carry=False)

        # int_mult_two = {'b1b2': 4, 'a1': 0, 'a2': 0, 'a3': 0, 'a4': 0, 'b3b4': 0, 'b3b6': 4, 'b5b6': 0, 'b4b5': -4, 'b1b3': 16, 'b5b7': 8, 'b1b7': -12, 'b4b6': -16, 'b3b7': -4, 'b3b5': -8, 'a7': 16, 'b2b7': -8, 'b2b6': -16, 'b4b7': 4, 'b6b7': 0, 'b1b5': -10, 'b2b4': 10, 'a6': 22, 'b2b5': -6, 'b1b6': 2, 'a5': 13, 'b1b4': 1, 'b2b3': 1}
        # # int_mult_two = {'b1b2': 8, 'a1': 0, 'a2': 0, 'a3': 0, 'a4': 0, 'b3b4': 0, 'b3b6': 8, 'b5b6': 0, 'b4b5': -8, 'b1b3': 32, 'b5b7': 16, 'b1b7': -24, 'b4b6': -32, 'b3b7': -8, 'b3b5': -16, 'a7': 32, 'b2b7': -16, 'b2b6': -32, 'b4b7': 8, 'b6b7': 0, 'b1b5': -20, 'b2b4': 20, 'a6': 44, 'b2b5': -12, 'b1b6': 4, 'a5': 26, 'b1b4': 2, 'b2b3': 2}
        # # Add the ancilla bit.
        # tt = [row + [0] for row in tt]
        # tt[-2][-1] = 1
        # # Generate the new QUBO.
        # new_q = find_int_qubo(tt, qubo=int_mult_two)
        # sol = run_qubo(**new_q, display=True)
        # print(sol == tt)
        # exit()

        print()
        for row in tt: print("",row)
        print()
        gap = 0.1

        int_mult_one = {'b1b2': 1, 'a1': 0, 'a2': 0, 'b3b4': -1, 'a3': 2, 'a4': 4, 'b2b3': 0, 'b1b3': 0, 'b1b4': -3, 'b2b4': -2}
        int_mult_two = {'b1b2': 16, 'a1': 0, 'a2': 0, 'a3': 0, 'a4': 0, 'b3b4': 0, 'b7b9': 48, 'a7': 112, 'b7b8': 64, 'a9': 96, 'b2b4': 128, 'b6b7': -48, 'b2b6': 64, 'b1b7': -32, 'b5b6': -32, 'b5b8': -256, 'b3b6': -176, 'b5b7': 104, 'a8': 408, 'b3b9': 176, 'b4b9': 144, 'b2b5': -8, 'b1b3': 56, 'b4b5': -72, 'b1b8': 8, 'b2b7': -88, 'b2b8': -264, 'b4b8': -272, 'b3b5': -208, 'b6b9': -48, 'a5': 576, 'b8b9': 24, 'a6': 284, 'b1b6': -164, 'b6b8': 92, 'b5b9': -164, 'b1b5': -132, 'b1b9': -54, 'b2b9': -58, 'b3b7': -26, 'b2b3': 2, 'b4b6': 74, 'b1b4': 1, 'b4b7': -81, 'b3b8': 17}
        int_mult_two =  {'b1b3': 32, 'a1': 0, 'a2': 0, 'a3': 0, 'a4': 0, 'b3b4': 0, 'b7b8': 96, 'b8b9': 32, 'b6b7': -64, 'b2b4': 160, 'b2b7': -128, 'b5b8': -288, 'b2b9': -96, 'b3b9': 224, 'a9': 128, 'a8': 480, 'b4b9': 160, 'b5b6': -64, 'b5b9': -160, 'b1b6': -128, 'b3b6': -192, 'a6': 288, 'b7b9': 96, 'b4b7': -112, 'b3b8': 16, 'b6b8': 80, 'b1b7': -48, 'b2b6': 64, 'b1b2': 48, 'b1b9': -80, 'b1b8': -16, 'b5b7': 144, 'b2b3': 2, 'b1b5': -138, 'b2b8': -342, 'b4b8': -298, 'b3b5': -188, 'b6b9': -52, 'b4b5': -71, 'a5': 559, 'b1b4': 14, 'a7': 146, 'b2b5': 30, 'b3b7': -20, 'b4b6': 84}

        print()
        print("Finding feasible solution..")
        # First find a real-valued solution to the problem.
        q = find_qubo(tt, random=False, gap=gap)
        print("Verifying solution..")
        sol = run_qubo(**q, display=False)
        if sol == tt:
            tt = sol
            print('-'*70)
            print("Using the following truth table to find integer solution:")
            for i,row in enumerate(tt): print("", row)
            # Find the integer form of the QUBO next.
            import math
            q = find_int_qubo(tt, gap=gap, display=False)
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

