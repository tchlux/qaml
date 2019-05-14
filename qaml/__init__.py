# Get the version number from the setup file
import os

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
ABOUT_DIR = os.path.join(DIRECTORY, "about")
__version__ = open(os.path.join(ABOUT_DIR,"version.txt")).read().strip()

# Make the major useful pieces of code available at the package level.
from qaml.circuit import Circuit
from qaml.qubo import QUBO, run_qubo
from qaml.systems import ExhaustiveSearch, QBSolve, QuantumAnnealer
