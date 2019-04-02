from base import QUBO

# Given two bit indices (integers), generaate QUBO for (a, a).
def pin(a=1, b=2):
    return QUBO(f"a{a}" : 1,
                f"a{b}" : 1,
                f"b{a}b{b}" : -2)

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
    return QUBO()


if __name__ == "__main__":
    from base import run_qubo

    # Run NOT
    print("-"*70)
    print("NOT")
    run_qubo(**not_gate(), min_only=False)
    print()

    # Run AND
    print("-"*70)
    print("AND")
    run_qubo(**and_gate(), min_only=False)
    print()

    # Constraints based on entries in selection.
    # a2 == 0
    # a1 == 0
    # b12 + b13 + b23 + a3 == 0

    # Additional constant constraints over above values based on unselected.
    # a3 > 0

    # Additional pairwise constraints
    # b12 > 0
    # b13 + a3 > 0
    # b23 + a3 > 0

    # Correct coefficients:
    # a1 = 0
    # a2 = 0
    # a3 = 2
    # b12 = 1
    # b13 = -1.5
    # b23 = -1.5

    # Run OR
    print("-"*70)
    print("OR")
    run_qubo(**or_gate(), min_only=False)
    print()


    # Run XOR
    print("-"*70)
    print("XOR")
    run_qubo(**xor_gate())
    print()

    # ====================================================================
    #   Combine gates by making them share one of their bits.

    print("-"*70)
    print("NOT (a AND b)")
    run_qubo(**(and_gate(1,2,3) + not_gate(3, 4)))
    print()

    print("-"*70)
    print("NOT (a OR b)")
    run_qubo(**(or_gate(1,2,3) + not_gate(3,4)))
    print()

    print("-"*70)
    print("c AND (a OR b)")
    run_qubo(**(or_gate(1,2,3) + and_gate(3,4,5)))
