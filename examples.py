if __name__ == "__main__":
    from logic import not_gate, and_gate, or_gate, xor_gate
    from qubo import run_qubo

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
    run_qubo(**(and_gate(1,2,3) + not_gate(3,4)))
    print()

    print("-"*70)
    print("NOT (a OR b)")
    run_qubo(**(or_gate(1,2,3) + not_gate(3,4)))
    print()

    print("-"*70)
    print("(a OR b) AND c")
    run_qubo(**(or_gate(1,2,3) + and_gate(3,4,5)))
