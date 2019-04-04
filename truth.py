# Generate truth tables for different operations.

from binary import int_to_binary

# Generate the truth table for a unsigned integer multiplication.
def uint_add_table(n_bits=2, wrap=False):
    truth_table = []
    for i1 in range(2**n_bits):
        for i2 in range(2**n_bits):
            row = int_to_binary(i1,n_bits) + int_to_binary(i2,n_bits) + int_to_binary(i1+i2,n_bits,signed=False)
            truth_table.append(row)
    return truth_table

# Generate the truth table for a unsigned integer multiplication.
def int_add_table(n_bits=2, wrap=False):
    truth_table = []
    for i1 in range(-2**(n_bits-1), 2**(n_bits-1)):
        for i2 in range(-2**(n_bits-1), 2**(n_bits-1)):
            row = int_to_binary(i1,n_bits) + int_to_binary(i2,n_bits) + int_to_binary(i1+i2,n_bits)
            truth_table.append(row)
    return truth_table

if __name__ == "__main__":
    # Test the generation of a truth table for addition.
    print('-'*70)    
    t = int_add_table(n_bits=2)
    print()
    for row in t: print(row)
    print()
    # Solve for the correct QUBO that satisfies this truth table.
    from solve import find_qubo
    q = find_qubo(t)#, max_attempts=10)
    # Run the QUBO and verify its correctness.
    from qubo import run_qubo
    run_qubo(**q)
