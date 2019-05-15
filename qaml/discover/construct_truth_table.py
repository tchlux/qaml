# Generate truth tables for different operations.
from qaml.binary import int_to_binary

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

# Generate the truth table for signed multi-integer addition.
def multi_int_add_table(n_bits, n_ints):
    # Generate all possible combinations of inputs
    max_abs_inp = 2**(n_bits-1) 
    all_inp_ints = range(-max_abs_inp, max_abs_inp)
    level = 1
    prev_combs = [[i] for i in all_inp_ints] # possible combinations of {level} integers.
    while level<n_ints:
        new_combs = []
        for prev_comb in prev_combs:
            for i in all_inp_ints:
                new_combs.append(prev_comb+[i])
        level += 1
        prev_combs = new_combs.copy()
    # Generate a row for each input combination.
    truth_table = []
    for inp_comb in prev_combs:
        curr_sum = sum(inp_comb)
        curr_row = []
        for i in inp_comb:
            curr_row = curr_row + int_to_binary(i, bits=n_bits)
        print (inp_comb, curr_row)
        curr_row = curr_row + int_to_binary(curr_sum, bits=n_bits+n_ints-1)
        truth_table.append(curr_row.copy())
    return sorted(truth_table)

# Generate the truth table for unsigned integer addition.
def uint_add_table(**kwargs):
    kwargs["signed"] = False
    return int_add_table(**kwargs)

# Generate the truth table for unsigned integer multiplication.
def int_mult_table(n_bits=2, signed=True, wrap=False, full=False):
    truth_table = []
    for i1 in range(2**n_bits):
        if signed: i1 -= 2**(n_bits-1)
        for i2 in range(2**n_bits):
            if signed: i2 -= 2**(n_bits-1)
            if full: res = int_to_binary(i1*i2,2*n_bits,signed=signed,wrap=wrap)
            else:    res = int_to_binary(i1*i2,n_bits,signed=signed,wrap=wrap)
            # Add the entry to the truth table.
            truth_table.append((
                int_to_binary(i1,n_bits,signed=signed) +
                int_to_binary(i2,n_bits,signed=signed) + res ))
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


