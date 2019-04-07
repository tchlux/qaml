# Generate truth tables for different operations.
from binary import int_to_binary

# Generate the truth table for signed integer addition.
def int_add_table(n_bits=2, wrap=False, signed=True):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            truth_table.append((
                int_to_binary(i1,n_bits,signed=signed) +
                int_to_binary(i2,n_bits,signed=signed) +
                int_to_binary(i1+i2,n_bits+1,signed=signed) ))
    return truth_table

# Generate the truth table for unsigned integer addition.
def uint_add_table(n_bits=2, wrap=False):
    return int_add_table(n_bits, wrap, signed=False)

# Generate the truth table for unsigned integer multiplication.
def int_mult_table(n_bits=2, wrap=False, signed=True):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            truth_table.append((
                int_to_binary(i1,n_bits,signed=signed) +
                int_to_binary(i2,n_bits,signed=signed) +
                int_to_binary(i1*i2,2*n_bits,signed=signed) ))
    return truth_table

# Generate the truth table for a unsigned integer multiplication.
def uint_mult_table(n_bits=2, wrap=False):
    return int_mult_table(n_bits, wrap, signed=False)




if __name__ == "__main__":

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


    TEST_FIND_QUBO_FOR_TT = True
    if TEST_FIND_QUBO_FOR_TT:
        # Find the solution QUBO and print it out.
        from solve import find_qubo, find_int_qubo
        from qubo import run_qubo, QUBO
        # Find the truth table for a specific arithmatic operation.
        tt = int_add_table(n_bits=4, signed=False)
        print()
        for row in tt: print(row)
        print()
        from qubo import run_qubo, QUBO
        q = find_int_qubo(tt)
        out = run_qubo(**q)


