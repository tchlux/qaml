from qubo import QUBO

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

# Given four bit indices (integers), generate a QUBO for x+y=s+2c.
def half_adder(x=1, y=2, s=3, c=4):
    return QUBO({f"a{x}" : 1, f"a{y}" : 1, f"a{s}" : 1, f"a{c}" : 4,
                 f"b{x}b{y}" : 2, f"b{x}b{s}" : -2, f"b{x}b{c}" : -4,
                 f"b{y}b{s}" : -2, f"b{y}b{c}" : -4, f"b{s}b{c}" : 4,
                 })

# Given five bit indices (integers), generate a QUBO for x+y+z=s+2c.
def full_adder(x=1, y=2, z=3, s=4, c=5):
    return QUBO({f"a{x}" : 1, f"a{y}" : 1, f"a{z}" : 1, 
                 f"a{s}" : 1, f"a{c}" : 4,
                 f"b{x}b{y}" : 2, f"b{x}b{z}" : 2,
                 f"b{x}b{s}" : -2, f"b{x}b{c}" : -4,
                 f"b{y}b{z}" : 2, f"b{y}b{s}" : -2, f"b{y}b{c}" : -4, 
                 f"b{z}b{s}" : -2, f"b{z}b{c}" : -4,
                 f"b{s}b{c}" : 4,
                 })
