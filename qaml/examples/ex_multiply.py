
from qaml import Circuit

num_bits = 2
c = Circuit()
a = c.Number(bits=num_bits, exponent=0, signed=False)
b = c.Number(bits=num_bits, exponent=-1, signed=False)

# Compute the energy function (a*b - 5)^2, forcing a*b to equal 5.
c.add( a * b - 5 )

# Run the circuit.
c.run(min_only=False)

#                         SAMPLE OUTPUT
# ____________________________________________________________________
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
# a 	b   	and breaks	Energy	
#  3	 1.5	     50.0%	  0.25	
#  2	 1.5	     50.0%	   4.0	
#  3	 1.0	     50.0%	   4.0	
#  2	 1.0	     50.0%	   9.0	
#  1	 1.5	     50.0%	 12.25	
#  3	 0.5	     50.0%	 12.25	
#  1	 1.0	     50.0%	  16.0	
#  2	 0.5	     50.0%	  16.0	
#  1	 0.5	     50.0%	 20.25	
#  0	 0.0	     50.0%	  25.0	
#  0	 0.5	     50.0%	  25.0	
#  0	 1.0	     50.0%	  25.0	
#  0	 1.5	     50.0%	  25.0	
#  1	 0.0	     50.0%	  25.0	
#  2	 0.0	     50.0%	  25.0	
#  3	 0.0	     50.0%	  25.0	
# ____________________________________________________________________
# 
# COMMENTARY:
#   Notice that since we are using an exhaustive brute-force search
#   over all possible bit patterns, 50% of those bit patterns cause
#   the AND gates to be in a failing state. The Circuit automatically
#   fixes those and gates and computes the correct energy value.
