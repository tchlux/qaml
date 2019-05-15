# Discover QUBOs

  Given the truth table for a circuit, discover the optimal QUBO embedding
  using linear programming.

## USAGE:

### Python

  This submodule automates the discovery of optimal QUBOs for a truth
  table. The function `solve_truth_table.solve_qubo` accepts Python
  lists containing valid rows in the truth table (encoded as lists of
  binary values), and will generate a linear system to find a QUBO
  embedding. If no embedding exists, ancillary bits are added until an
  embedding can be found. Note that the computational complexity grows
  exponentially with each ancillary bit, so this function is only
  usable for small problems/circuits that require few ancillary bits.
  The function `solve_truth_table.solve_int_qubo` accepts similarly
  formatted truth tables, but rounds output weights to integer values,
  for human readability. `solve_truth_table.solve_int_qubo` will not
  attempt to add ancillary bits, so a solvable truth table must first
  be found using `solve_truth_table.solve_qubo`. See the `examples`
  subdirectory for demonstrations of this process.

  The module `solve_truth_tables.py` contains the functions for
  automatically constructing QUBOs, as described above. The module
  `construct_truth_tables.py` contains functions for automatically
  generating several common truth tables, for testing purposes.

```python
import qaml

# Construct a circuit with two signed 4-bit fixed precision numbers.
#   a = (  a0 * 2^[-1]  +  a1 * 2^[0]  +  a2 * 2^[1]  -  a3 * 2^[2]  )
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

#                         SAMPLE OUTPUT
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
```
