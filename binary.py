

# Convert a binary list into an integer, the inverse of "int_to_binary".
def binary_to_int(bits, signed=True):
    # Perform two's compliment on the number.
    negative = False
    if (signed and (bits[0] == 1)):
        bits = [1-b for b in bits[1:]]
        negative = True
    # Convert the bits into an integer.
    integer = sum(b*2**(len(bits)-i-1) for (i,b) in enumerate(bits))
    # Return the correctly signed integer.
    return (integer+negative) * (-1)**negative

# Compute the number of bits required to represent an integer.
def num_bits(i):
    import math
    if   (i ==  0): needed_bits = 1
    elif (i == -1): needed_bits = 2
    elif (i  >  0): needed_bits = 1 + int(math.log(abs(i),2))
    else:           needed_bits = 2 + int(math.log(abs(i)-1,2))
    return needed_bits

# Given a nonnegative integer, generate the big-endian binary
# representation of that number with the fewest bits possible.
def int_to_binary(i, bits=None, signed=True, wrap=False):
    import math
    # Store some information about the number (with fewest bits possible).
    negative = (i < 0)
    # Compute the necessary number of bits to store this number.
    needed_bits = num_bits(i)
    # Modify the number if caller specified "bits" (and "wrap").
    if (bits != None):
        if wrap:
            # Convert negative numbers to positive interpretation.
            if negative: i += 2**max(bits,needed_bits)
            i = i % 2**bits
            if (i >= 2**(bits-1)): i -= 2 ** bits
            # Update "negative" status based on wrapped value.
            negative = (i < 0)
        else:
            # Reduce the value to its capped amount (for non-wrapping).
            i = (-1)**negative * min(abs(i), 2**(bits-signed)-(not negative))
        # Update the "needed bits" because we have capped that.
        needed_bits = bits
    # Convert negative numbers into their positive unsigned form.
    if negative: i = 2**(needed_bits-negative) - abs(i)
    # Generate the binary number for the positive version.
    if (i == 0): b = [0]
    else:
        b = []
        for power in range(int(math.log(i, 2)), -1, -1):
            num = 2**power
            if (i >= num): b.append(1)
            else:          b.append(0)
            i -= num*b[-1]
    # Make the number negative by adding the sign bit, otherwise pad with zeros.
    if negative: b = [1] + [0]*(needed_bits-len(b)-1) + b
    else:        b = [0]*(needed_bits-len(b)) + b
    # Return the binary number.
    return b


if __name__ == "__main__":
    # Test "int_to_binary" to see negative numbers working properly.
    print('-'*70)
    print(" Mapping signed integer to binary without wrapping:")
    print()
    for in_i in range(-10,10):
        b = int_to_binary(in_i, bits=4)
        out_i = binary_to_int(b)
        print(f"{in_i:2d}", b, f"{out_i:2d}")
    print()

    print('-'*70)
    print(" Mapping signed integer to binary with wrapping:")
    print()
    for in_i in range(-10,10):
        b = int_to_binary(in_i, bits=4, wrap=True)
        out_i = binary_to_int(b)
        print(f"{in_i:2d}", b, f"{out_i:2d}")
    print()

    print('-'*70)
    print(" Mapping unsigned integer to binary:")
    print()
    for in_i in range(16):
        b = int_to_binary(in_i, bits=4, signed=False)
        out_i = binary_to_int(b, signed=False)
        print(f"{in_i:2d}", b, f"{out_i:2d}")
    print()


    print('-'*70)
    print("Prevent wrapping on signed addition:")
    print()
    n_bits = 2
    signed = True
    for i1 in range(-2**(n_bits-1),2**(n_bits-1)):
        str_i1 = f"{i1:2d}"
        for i2 in range(-2**(n_bits-1),2**(n_bits-1)):
            str_i2 = f"{i2:2d}"
            b_i1 = int_to_binary(i1,n_bits, signed=signed)
            b_i2 = int_to_binary(i2,n_bits, signed=signed)
            b = int_to_binary(i1+i2,n_bits, signed=signed, wrap=False)
            str_i_out = f"%2d"%(binary_to_int(b, signed=signed))
            print(str_i1, "+", str_i2, "=", str_i_out, "  ", b_i1, "+", b_i2, "=", b)
    print()


    print('-'*70)
    print("Allow wrapping on signed addition:")
    print()
    n_bits = 2
    signed = True
    for i1 in range(-2**(n_bits-1),2**(n_bits-1)):
        str_i1 = f"{i1:2d}"
        for i2 in range(-2**(n_bits-1),2**(n_bits-1)):
            str_i2 = f"{i2:2d}"
            b_i1 = int_to_binary(i1,n_bits, signed=signed)
            b_i2 = int_to_binary(i2,n_bits, signed=signed)
            b = int_to_binary(i1+i2,n_bits, signed=signed, wrap=True)
            str_i_out = f"%2d"%(binary_to_int(b, signed=signed))
            print(str_i1, "+", str_i2, "=", str_i_out, "  ", b_i1, "+", b_i2, "=", b)
    print()

    print('-'*70)
    print("Prevent wrapping on unsigned addition:")
    print()
    n_bits = 2
    signed = False
    for i1 in range(2**(n_bits)):
        str_i1 = f"{i1:1d}"
        for i2 in range(2**(n_bits)):
            str_i2 = f"{i2:1d}"
            b_i1 = int_to_binary(i1,n_bits, signed=signed)
            b_i2 = int_to_binary(i2,n_bits, signed=signed)
            b = int_to_binary(i1+i2,n_bits, signed=signed, wrap=False)
            str_i_out = f"%1d"%(binary_to_int(b, signed=signed))
            print(str_i1, "+", str_i2, "=", str_i_out, "  ", b_i1, "+", b_i2, "=", b)
    print()


    print('-'*70)
    print("Allow wrapping on unsigned addition:")
    print()
    n_bits = 2
    signed = False
    for i1 in range(2**(n_bits)):
        str_i1 = f"{i1:1d}"
        for i2 in range(2**(n_bits)):
            str_i2 = f"{i2:1d}"
            b_i1 = int_to_binary(i1,n_bits, signed=signed)
            b_i2 = int_to_binary(i2,n_bits, signed=signed)
            b = int_to_binary(i1+i2,n_bits, signed=signed, wrap=True)
            str_i_out = f"%1d"%(binary_to_int(b, signed=signed))
            print(str_i1, "+", str_i2, "=", str_i_out, "  ", b_i1, "+", b_i2, "=", b)
    print()
