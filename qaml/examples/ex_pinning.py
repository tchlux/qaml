
from qaml import Circuit

# Create a circuit and allocate a signed fixed point "number"
#  with 3 bits of precision and a starting exponent of -1.
# 
#    a  =  (  a0 * 2^[-1]  +  a1 * 2^[0]  -  a2 * 2^[1]  )
# 
# If "a" were an unsigned number than the term ^^^^^ would be "+".
# 
c = Circuit()
a = c.Number(bits=3, exponent=-1, signed=True)

# Add the equation (a - 1)^2 to the system to pin "a" to the value 1.
c.add( a - 1 )

# Run the circuit, disable "min_only" to show the full output, instead
# of only showing the minimum energy solution.
c.run(min_only=False)


#                         SAMPLE OUTPUT
# ____________________________________________________________________
# 
#
#  QUBO with 3 bits in range [-4, 8].
#    {'a1': -0.75, 'a2': -1, 'a3': 8, 'b1b2': 1.0, 'b1b3': -2.0, 'b2b3': -4, 'c': 1}
#  --------------
#   -0.75
#    1.00  -1
#   -2.00  -4  8
#  --------------
# 
# a    	Energy	
#   1.0	   0.0	
#   0.5	  0.25	
#   1.5	  0.25	
#   0.0	   1.0	
#  -0.5	  2.25	
#  -1.0	   4.0	
#  -1.5	  6.25	
#  -2.0	   9.0	

