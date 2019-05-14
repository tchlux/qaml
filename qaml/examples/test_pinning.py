
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
