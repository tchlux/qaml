<p align="center">
  <img src="./qaml-dark.svg">
  <h1 align="center">Quantum Annealing Math Library</h1>
</p>

  A package for programming general least squares problems on Quantum annealers.

## INSTALLATION:

    $ pip install git+https://github.com/tchlux/qaml.git

## USAGE:

### Python

  This module makes the construction of least-squares energy
  landscapes for a quantum annealing framework easily accessible. See
  `qaml/examples` for demonstrations of how to setup and solve
  fixed-point least squares problems.

  In order to construct arbitrary least squares circuits, this module
  provides a `qaml.Circuit` object that allows the allocations of
  numbers via the function `Circuit.Number`. The `Number` objects can
  be added, subtracted, multiplied, and exponentiated in standard
  Python syntax.

  After manipulating (a sequence of) `Number`(s) into an equation, use
  `Circuit.add( <Number> )`. Multiple equations can be added to the
  same circuit. Once ready to minimize, construct and run the circuit
  with `Circuit.run()`.

  This will produce a QUBO whose energy function is the summed squared
  value of all equations provided. That squared-value QUBO will be
  executed on the selected quantum annealing system (could be a
  simulator like `QBSolve` or real D-Wave hardware). After execution,
  the results will be post-processed for logical consistency and
  presented in a human-readable format.

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

## Additional Information

This code is associated with a research paper that is currently
under review by Springer [Quantum Information Processing](https://link.springer.com/journal/11128).

Please create an *issue* for usage questions and bug reporting.
