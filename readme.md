|             |                |
|-------------|----------------|
|**TITLE:**   | Quantum Annealing Math Library     |
|**PURPOSE:** | A general fixed point least squares solver using a Quantum annealer.      |
|**CORRESPONDING AUTHOR:**  | Thomas C.H. Lux  |
|**EMAIL:**   | tchlux@vt.edu |


## INSTALLATION:

    $ pip install git+https://github.com/tchlux/qaml.git

## USAGE:

### Python

  This module makes the construction of least-squares energy
  landscapes for a quantum annealing framework easily
  accessible. See `examples` for demonstrations of how to setup and
  solve fixed-point least squares problems.

  In order to construct arbitrary least squares circuits, this
  module provides a `qaml.Circuit` object that allows the
  allocations of numbers via `Circuit.Number` objects. The number
  objects can be added, subtracted, multiplied, and exponentiated in
  standard Python syntax.

  After manipulating (a sequence of) Number(s) into an equation, use
  `Circuit.add( <Number> )`. Multiple equations can be added to the
  same circuit. Once ready to minimize, construct the full QUBO with
  `Circuit.assemble()`.

  This will produce a QUBO whose energy landscape is the summed
  squared value of all equations provided.

    > import qaml
    > circ = qaml.Circuit()
    > a = circ.Number(bits=4, exponent=-1, signed=False)
    > b = circ.Number(bits=4, exponent=-1, signed=False)
    > circ.add( a + b - 6 )
    > circ.add( a - 2 )
    > qubo = circ.assemble()
    > qaml.run_qubo(qubo, min_only=False, display=True)

