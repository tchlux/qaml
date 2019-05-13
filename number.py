from qubo import QUBO
from itertools import combinations, product


# Create a "Number" that is fixed point, by default a standard integer.
# This number supports operations with other number objects and Python
# integers and floats.
class Number:
    def __init__(self, circuit, bit_indices, exponent, signed, constant=0):
        # Store the provided parameters.
        self.circuit     = circuit
        self.bit_indices = bit_indices
        self.exponent    = exponent
        self.signed      = signed
        self.bits        = QUBO()
        self.constant    = constant
        # Initialize the number coefficients itself.
        bits = len(bit_indices)
        for i in range(bits - int(signed)):
            bit = self.bit_indices[i]
            self.bits[bit] = 2**(i + exponent)
        if signed:
            bit = self.bit_indices[bits-1]
            self.bits[bit] = -2**(bits-1 + exponent)
        # Store which values are one-local.
        self.one_locals = set(self.bit_indices)
        
    # Print out information about this number.
    def __str__(self):
        string  = "Number:\n"
        string += f"  bit_indices: {self.bit_indices}\n"
        string += f"  exponent:    {self.exponent}\n"
        string += f"  signed:      {self.signed}\n"
        string += f"  bits:        {dict(self.bits)}\n"
        string += f"  constant:    {self.constant}\n"
        string += f"  one_locals:  {self.one_locals}\n"
        max_len_line = max(map(len, string.split("\n")))
        page_break = '-'*max_len_line+"\n"
        return  page_break + string + page_break

    # Support addition of another number.
    def __add__(self, num):
        # Verify correct usage.
        assert(type(num) in {type(self), int, float})
        # Initialize a new Number object to be returned.
        new_num = Number(self.circuit, self.bit_indices,
                         self.exponent, self.signed, self.constant)
        new_num.bits = self.bits.copy()
        new_num.one_locals = self.one_locals.copy()
        # Generate a new number that is a copy of this one with a
        # different constant term added on.
        if (type(num) in {int, float}):
            new_num.constant += num
        # Perform the addition between the qubits in the QUBO.
        elif (type(num) == type(self)):
            # Add together the coefficients of the two QUBO's for each number.
            for coef in num.bits:
                new_num.bits[coef] = new_num.bits.get(coef, 0) + num.bits[coef]
            # Update the one-local terms track for the new number.
            new_num.one_locals = new_num.one_locals.union(num.one_locals)
        # Return the new number.
        return new_num

    # Support subtraction of another number.
    def __sub__(self, num): return self + num.__neg__()

    # Support negation of a number.
    def __neg__(self):
        # Initialize a new Number object to be returned.
        new_num = Number(self.circuit, self.bit_indices,
                         self.exponent, self.signed, -self.constant)
        # Make the QUBO the negation of all values in this QUBO.
        new_num.bits = QUBO({coef:-self.bits[coef] for coef in self.bits})
        new_num.one_locals = self.one_locals.copy()
        return new_num

    # Raise this to a power.
    def __pow__(self, exponent):
        num = 1
        for i in range(exponent): num = self * num
        return num

    # Support multiplication with another number.
    def __mul__(self, num):
        # Verify correct usage.
        assert(type(num) in {type(self), int, float})
        # Initialize a new Number object to be returned.
        new_num = Number(self.circuit, self.bit_indices,
                         self.exponent, self.signed, self.constant)
        new_num.bits = self.bits.copy()
        new_num.one_locals = self.one_locals.copy()
        # Generate a new number that is a copy of this one with a
        # different constant term multiplied on, also multiply QUBO.
        if (type(num) in {int, float}):
            new_num.constant *= num
            for coef in new_num.bits: new_num.bits[coef] *= num
        # Perform the multiplication between the qubits in the QUBO.
        elif (type(num) == type(self)):
            print("self: ",self)
            print("num:  ",num)
            # Multiply the values that are shared between the two.
            shared_terms = num.one_locals.intersection(self.one_locals)
            for coef in shared_terms: new_num.bits[coef] *= num.bits[coef]
            # Generate ancillary bits to make all 2-locals into 1-locals.
            unique_pairs = {(min(c1,c2), max(c1,c2)) for (c1,c2) in product(
                self.one_locals, num.one_locals) if (c1 != c2)}
            ancillary_bits = self.circuit.allocate(len(unique_pairs))
            # Construct the and gates to make new one-local terms.
            for (c1, c2), a in zip(unique_pairs,ancillary_bits):
                self.circuit.and_gates.append(
                    QUBO({a:3, (c1,c2):1, (c1,a):-2, (c2,a):-2}) )
                # Assign the value of the new ancillary bit as their multiplication.
                if (c1 in self.bits) and (c2 in num.bits):
                    new_num.bits[a] = self.bits[c1] * num.bits[c2]
                if (c2 in self.bits) and (c1 in num.bits):
                    if (a in new_num.bits): new_num.bits[a] *= 2
                    else: new_num.bits[a] = self.bits[c2] * num.bits[c1]
            # Update the now one-local terms in the new number.
            new_num.one_locals = shared_terms.union(ancillary_bits)
            # Multiply "my" terms by "num" constant.
            for coef in self.one_locals:
                new_num.bits[coef] = new_num.bits.get(coef,1) * num.constant
            # Multiply "num" terms by "my" constant.
            for coef in num.one_locals:
                new_num.bits[coef] = new_num.bits.get(coef,1) * self.constant
            # Multiply the constants together.
            new_num.constant = self.constant * num.constant
            print("new_num: ",new_num)
        # Return the new number.
        return new_num

    # Generate the squared value energy function QUBO for this number.
    @property
    def squared(self):
        qubo = QUBO()
        print(self)
        # Square all the one-local terms (including constant interactions).
        for coef in self.one_locals:
            qubo[coef] = self.bits[coef]**2 + self.bits[coef]*2*self.constant
        # Add the interactions for the squared (now two-local) terms.
        for (c1, c2) in combinations(sorted(self.one_locals), 2):
            qubo[(c1,c2)] = 2 * self.bits[c1] * self.bits[c2]
        # Add constant term to QUBO (for squared correctness).
        qubo["c"] = self.constant**2
        return qubo


# Holder for a Quantum Annealing circuit in QUBO form. Keeps track of
# the bits that have been utilized. Produces the squared error energy
# function for numeric operations.
class Circuit:
    def __init__(self):
        self.bits = []
        self.equations = []
        self.and_gates = []
        self.largest_exponent = 1

    # Generate a collection of bits to be used as ancillary bits.
    def allocate(self, bits):
        if len(self.bits) == 0: self.bits += list(range(bits))
        else: self.bits += list(range(self.bits[-1]+1, self.bits[-1]+1+bits))
        return self.bits[-bits:]

    # Generate a 'Number' object with memory allocated in this circuit.
    def Number(self, bits, exponent=0, signed=False):
        self.largest_exponent = max(bits+exponent+1, self.largest_exponent)
        return Number(self, self.allocate(bits), exponent, signed)

    # Add a number that represents an equation to the set of equations.
    def add(self, number):
        self.equations.append( number )

    # Generate the squared value energy function QUBO for this number.
    def assemble(self, and_rescale=None):
        if (type(and_rescale) == type(None)):
            and_rescale = 2**self.largest_exponent
        # Generate a qubo for the squared value function.
        # This is where the computation of the AND gates happens.
        q = QUBO()
        for n in self.equations:
            q += n.squared
        for gate in self.and_gates:
            q += gate * and_rescale
        return q
        

circ = Circuit()
a = circ.Number(3)
b = circ.Number(2)

circ.add( a*b - 21 )
circ.add( a + b - 10 )
q = circ.assemble()

from qubo import run_qubo
run_qubo(**q, min_only=False)


exit()



# a = Number(bits=2, exponent=0, signed=False)
# b = Number(bits=3, exponent=-1, signed=False)
# c = Number(bits=2, exponent=0)
# d = Number(bits=2, exponent=0)
# 
# exp = a
# exp += b
# exp *= c
# exp -= d
# 
#  --->  exp = [ (a + b)*c - d ]^2

