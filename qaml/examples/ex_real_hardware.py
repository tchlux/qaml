
from qaml import Circuit, QuantumAnnealer

num_bits = 2
c = Circuit()
a = c.Number(bits=num_bits, exponent=0, signed=False)
b = c.Number(bits=num_bits, exponent=-1, signed=False)

# Compute the energy function (a*b - 5)^2, forcing a*b to equal 5.
c.add( a * b - 5 )

# Run the circuit on the real quantum annealing hardware.
c.run(min_only=False, system=QuantumAnnealer,
      and_strength=1/2, chain_strength=1/2)
# 
#     ^^ "and_strength" controls the relative strength of AND
#        gates in the circuit. If you see them break a lot in the
#        output, then consider increasing this value.
#    
#                        ^^ The same goes for chain strength with breaks.


#                 SAMPLE OUTPUT ON REAL HARDWARE
# __________________________________________________________________
# 
# Using and gate scale 2.75.
# 
#  QUBO with 8 bits in range [-7.75, 4].
#    {'a8': 3.5, 'b1b3': 2.75, 'b1b8': -5.5, 'b3b8': -5.5, 'a7': -7.75, 'b2b4': 2.75, 'b2b7': -5.5, 'b4b7': -5.5, 'a6': -0.75, 'b1b4': 2.75, 'b1b6': -5.5, 'b4b6': -5.5, 'a5': -0.75, 'b2b3': 2.75, 'b2b5': -5.5, 'b3b5': -5.5, 'b5b6': 2.0, 'b5b7': 4.0, 'b5b8': 1.0, 'b6b7': 4, 'b6b8': 1.0, 'b7b8': 2.0, 'c': 25, 'a3': 0.0, 'a4': 0, 'a1': 0, 'a2': 0}
#  --------------------------------------------------------
#     0  
#     0      0  
#    2.75   2.75   0.00
#    2.75   2.75    0      0  
#     0    -5.50  -5.50    0    -0.75
#   -5.50    0      0    -5.50   2.00  -0.75
#     0    -5.50    0    -5.50   4.00    4    -7.75
#   -5.50    0    -5.50    0     1.00   1.00   2.00   3.50
#  --------------------------------------------------------
#
#
# Max chain length of 3
# Chain length distribution:
#  2 chain -- ##
#  3 chain -- ######
# 
# Using embedding with 22 qubits:
#  0 [1489, 1361, 1492]
#  1 [1491, 1363, 1495]
#  2 [1488, 1360]
#  3 [1356, 1364, 1352]
#  4 [1490, 1362, 1494]
#  5 [1358, 1366, 1355]
#  6 [1357, 1365, 1354]
#  7 [1359, 1367]
# 
# Max Ising weight:      1.0
# Min Ising weight:     -4.1
# Using chain strength:  2.1
# 
# a 	b   	and breaks	chain breaks	Energy	
#  3	 1.5	      0.1%	        0.0%	  0.25	
# __________________________________________________________________
#
# COMMENTARY:
#   Notice that the real hardware requires an embedding, the logical
#   QUBO does not map perfectly to the D-Wave Chimera graph structure,
#   so a graph embedding with chains (of duplicated qubits) is
#   necessary. Notice that only one unique solution is seen from the
#   hardware in this example, but there were more solutions returned 
#   that violated and gates, so they were corrected and their energies
#   recalculated before the printout above.
