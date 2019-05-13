from qaml.qubo import QUBO, run_qubo
from qaml.circuit import Circuit

DEMONSTRATE_PINNING = True
if DEMONSTRATE_PINNING:
    num_bits = 1
    c = Circuit()
    a = c.Number(num_bits)
    b = c.Number(num_bits)
    # Define a circuit that adds "a" and "b".
    c.add( a + b )
    # Pin "b" to one by adding an equation that is minimized at 1.
    c.add( b - 1 )
    # Assemble the equations into a least squares energy function QUBO.
    q = c.assemble()
    # Run the QUBO to demonstrate that the minimum energy solution has b=0.
    run_qubo(**q, min_only=False)
