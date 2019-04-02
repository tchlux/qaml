from qubo import QUBO
from exceptions import UsageError

# Given two bit indices (integers), generaate QUBO for (a, a).
def pin(a=1, b=2):
    return QUBO({f"a{a}" : 1,
                 f"a{b}" : 1,
                 f"b{a}b{b}" : -2})

# Given two bit indices (integers), generate a QUBO for (a, ~a).
def not_gate(a=1, not_a=2):
    return QUBO({f"a{a}" : -1,
                 f"a{not_a}" : -1,
                 f"b{a}b{not_a}" : 2,
                  "c" : 1})

# Given three bit indices (integers), generate a QUBO for (a, b, a^b).
def and_gate(a=1, b=2, a_and_b=3):
    return QUBO({f"a{a_and_b}" : 3,
                 f"b{a}b{b}" : 1,
                 f"b{a}b{a_and_b}" : -2,
                 f"b{b}b{a_and_b}" : -2})

# Given three bit indices (integers), generate a QUBO for (a, b, aVb).
def or_gate(a=1, b=2, a_or_b=3):
    return QUBO({f"a{a}" : 1,
                 f"a{b}" : 1,
                 f"a{a_or_b}" : 1,
                 f"b{a}b{b}" : 1,
                 f"b{a}b{a_or_b}" : -2,
                 f"b{b}b{a_or_b}" : -2})


# Given four bit indices (integers), generate a QUBO for (a, b, aXb, -).
def xor_gate(a=1, b=2, a_xor_b=3, ancilla=4):
    return QUBO({f"a{a}" : 1,
                 f"a{b}" : 1,
                 f"a{a_xor_b}" : 1,
                 f"a{ancilla}" : 4,
                 f"b{a}b{b}" : 2,
                 f"b{a}b{a_xor_b}" : 2,
                 f"b{a}b{ancilla}" : -4,
                 f"b{b}b{a_xor_b}" : 2,
                 f"b{b}b{ancilla}" : -4,
                 f"b{a_xor_b}b{ancilla}" : -4})

# Given an arbitrary number of bit indices, assume they represent a
# big-endian integer. Generate a QUBO that minimizes this integer.
def uint_min(*bit_indices):
    return QUBO({f"a{b}" : 2**(len(bit_indices)-i-1)
                 for i,b in enumerate(bit_indices)})

# Given an arbitrary number of bit indices, assume they represent a
# big-endian integer. Generate a QUBO that minimizes this integer.
def int_min(*bit_indices):
    return QUBO({f"a{b}" : (2**(len(bit_indices)-i-1) if i > 0 else 0)
                 for i,b in enumerate(bit_indices)})

# Given a pin bit and an arbitrary number of bit indices representing
# a signed integer, force the signed integer to be positive.
def abs_int(*bit_indices):
    return QUBO({f"a{bit_indices[0]}":2**(len(bit_indices)-1)})

# Given three signed integers (a,b,c) with equal number of bits, perform:
#    c = min(a, b)
def min_int(*bit_indices):
    if ((len(bit_indices) % 3) != 0):
        raise(UsageError("'min_int' takes three signed integers with equal number of bits."))
    int_size = len(bit_indices) // 3
    # Split up the bits into the three integers.
    a_bits = bit_indices[:int_size]
    b_bits = bit_indices[int_size:-int_size]
    out_bits = bit_indices[-int_size:]
    # Perform the minimization operation.
    # (a + b) / 2 - |a - b|
