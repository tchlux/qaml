

# Given a nonnegative integer, generate the big-endian binary
# representation of that number with the fewest bits possible.
def int_to_binary(i, bits=None, signed=True):
    import math
    # Store some information about the number (with fewest bits possible).
    negative = (i < 0)
    if (i == 0): pass
    elif (not negative):
        max_bits = 1 + int(math.log(abs(i),2))
    else:
        if (i == -1): max_bits = 2
        else:         max_bits = 2 + int(math.log(abs(i)-1,2))
        i = 2**(max_bits-1) - abs(i)
    # Generate the binary number for the positive version.
    if (i == 0): b = [0]
    else:
        b = []
        for power in range(int(math.log(i, 2)), -1, -1):
            num = 2**power
            if (i >= num): b.append(1)
            else:          b.append(0)
            i -= num*b[-1]
    # Convert to two's compliment if negative by using addition.
    if negative:
        pos_b = [0]*(max_bits-len(b)) + b
        b = [1] + [0]*(max_bits-1)
        for i in range(-1, -max_bits, -1):
            b[i-1] += (pos_b[i] + b[i]) >= 2
            b[i] = (pos_b[i] + b[i]) % 2
    # Add extra bits if appropriate.
    if (bits != None):
        # Pad on the left with 1's for negative, 0's for positive.
        if (negative): b = [1]*(bits-len(b)) + b
        else:          b = [0]*(bits-len(b)) + b
        # Handle overflow.
        if (len(b) > bits):
            if signed:
                if (b[0] == 1): b = [1] + [0]*(bits-1)
                else:           b = [0] + [1]*(bits-1)
            else: b = [1]*bits
    # Return the binary number.
    return b

if __name__ == "__main__":
    # Test "int_to_binary" to see negative numbers working properly.
    print('-'*70)
    print(" Mapping integer to binary:")
    for i in range(-8,8):
        b = int_to_binary(i, bits=4)
        print(f"{i:2d}", b)
    print()
