
from qaml import Circuit

num_bits = 2
c = Circuit()
a = c.Number(bits=num_bits, exponent=0, signed=False)
b = c.Number(bits=num_bits, exponent=-1, signed=False)

# Compute the energy function (a*b - 5)^2, forcing a*b to equal 5.
c.add( a * b - 5 )

# Run the circuit.
c.run(min_only=False)


# # EXTRA: (uncomment to extend this test to real hardware)
# # Run the circuit on the real quantum annealing hardware.
# 
# from qaml import QuantumAnnealer
# c.run(min_only=False, system=QuantumAnnealer,
#       and_strength=1/2, chain_strength=1/2)
# 
# #     ^^ "and_strength" controls the relative strength of AND
# #        gates in the circuit. If you see them break a lot in the
# #        output, then consider increasing this value.
# #    
# #                        ^^ The same goes for chain strength with breaks.
