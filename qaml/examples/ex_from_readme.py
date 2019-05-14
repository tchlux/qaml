
import qaml

# Construct a circuit with two signed 4-bit fixed precision numbers.
#   a  =  (  a0 * 2^[-1]  +  a1 * 2^[0]  +  a2 * 2^[1]  -  a3 * 2^[2]
circ = qaml.Circuit()
a = circ.Number(bits=4, exponent=-1, signed=True)
b = circ.Number(bits=4, exponent=-1, signed=True)

# Add the equations:
#     ( a + b - 6 )^2
#   + ( a - 2 )^2
circ.add( a + b - 6 )
circ.add( a - 2 )
circ.run( min_only=False, display=True )
#         ^^ Show all results, not just minimum solutions.

# ____________________________________________________________________
# 
#  QUBO with 8 bits in range [-32, 96].
#  -------------------------------------------------
#   -7.50
#    2.00   -14 
#    4.00    8     -24 
#   -8.00   -16    -32    96  
#    0.50   1.00   2.00  -4.00  -5.75
#    1.00    2      4     -8     1.00  -11
#    2.00    4      8     -16    2.00   4   -20
#   -4.00   -8     -16    32    -4.00  -8   -16  64
#  -------------------------------------------------
# 
# a    	b    	Energy 	
#   2.0	  3.5	   0.25	
#   2.5	  3.5	   0.25	
#   2.5	  3.0	    0.5	
#   2.0	  3.0	    1.0	
#   3.0	  3.0	    1.0	
#    .     .         .
#    .     .         .
#    .     .         .
