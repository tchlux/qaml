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
