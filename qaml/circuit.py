from itertools import combinations, product
from qaml.qubo import QUBO

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
        self.constant    = constant
        self.bits        = QUBO()
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

    # Addition from the right is the same.
    def __radd__(self, num): return self._add__(num)
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
            # First compute all the 1-local terms that require no anicillary bits.
            shared_terms = num.one_locals.intersection(self.one_locals)
            all_terms = self.one_locals.union(num.one_locals)
            for coef in all_terms:
                value = 0
                if coef in self.one_locals: value += self.bits[coef] * num.constant
                if coef in num.one_locals:  value += num.bits[coef]  * self.constant
                if coef in shared_terms:    value += self.bits[coef] * num.bits[coef]
                new_num.bits[coef] = value
            # Generate ancillary bits to make all 2-locals into 1-locals.
            unique_pairs = {(min(c1,c2), max(c1,c2)) for (c1,c2) in product(
                self.one_locals, num.one_locals) if (c1 != c2)}
            ancillary_bits = self.circuit.allocate(len(unique_pairs))
            # Construct the and gates to make new one-local terms.
            for (c1, c2), a in zip(unique_pairs,ancillary_bits):
                self.circuit.add_and(c1, c2, a)
                # Assign the value of the new ancillary bit as their multiplication.
                if (c1 in self.bits) and (c2 in num.bits):
                    new_num.bits[a] = self.bits[c1] * num.bits[c2]
                if (c2 in self.bits) and (c1 in num.bits):
                    if (a in new_num.bits): new_num.bits[a] *= 2
                    else: new_num.bits[a] = self.bits[c2] * num.bits[c1]
            # Update the now one-local terms in the new number.
            new_num.one_locals = shared_terms.union(ancillary_bits)
            # Multiply the constants together.
            new_num.constant = self.constant * num.constant
        # Return the new number.
        return new_num

    # Multiplication from the right is the same.
    def __rmul__(self, num): return self.__mul__(num)

    # Generate the squared value energy function QUBO for this number.
    def squared(self):
        qubo = QUBO()
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
        self.numbers = []
        self.equations = []
        self.and_gates = []

    # Generate a collection of bits to be used as ancillary bits.
    def allocate(self, bits):
        if len(self.bits) == 0: self.bits += list(range(bits))
        else: self.bits += list(range(self.bits[-1]+1, self.bits[-1]+1+bits))
        return self.bits[len(self.bits)-bits:]

    # Generate a 'Number' object with memory allocated in this circuit.
    def Number(self, bits, exponent=0, signed=False):
        self.numbers.append( Number(self, self.allocate(bits), exponent, signed) )
        return self.numbers[-1]


    # Add a number that represents an equation to the set of equations.
    def add(self, *args, **kwargs): return self.square(*args, **kwargs)
    def square(self, number):
        self.equations.append( number )

    # Construct an "and" gate over two input terms "c1" and "c2" and
    # an output term "a". Store that and gate for later evaluation.
    def add_and(self, c1, c2, a):
        self.and_gates.append(
            QUBO({a:3, (c1,c2):1, (c1,a):-2, (c2,a):-2}) )

    # Generate the squared value energy function QUBO for this number.
    def assemble(self, and_strength, verbose=True):
        from qaml.qubo import qubo_ising_rescale_factor
        # Compute the qubo without the and-gate rescale.
        q = QUBO()
        for n in self.equations:
            q += n.squared()
        # Set the rescale to the max Ising weight.
        and_strength *= qubo_ising_rescale_factor(q)
        if (len(self.and_gates) > 0) and verbose:
            print(f"\nUsing and strength {and_strength:.2f}.")

        # Generate a qubo for the squared value function.
        # This is where the computation of the AND gates happens.
        q = QUBO()
        # Add 0 times all numbers to ensure all coefficients are included.
        for n in self.numbers:
            q += 0 * n.bits
        # Add all of the squared equations.
        for n in self.equations:
            q += n.squared()
        # Add all of the and gates with the specified strength.
        for gate in self.and_gates:
            q += gate * and_strength
        return q

    # Get the names of the Number objects in the user function that
    # called this circuit (but not this function directly).
    def _num_names(self):
        import inspect
        names = []
        user_locals = inspect.currentframe().f_back.f_back.f_locals
        # Cycle all the Number objects in this circuit.
        for i in range(len(self.numbers)):
            num = self.numbers[i]
            names.append( ([str(i)]+[name for name in user_locals
                                     if user_locals[name] is num])[-1] )
        return names

    # Given a string of bits that represents a state of this circuit,
    # decode that string into the corresponding numbers (resolving
    # logical conflicts like broken and gates if appropriate).
    def decode(self, bits):
        # Check to see if length of the bit sequence is valid.
        if (len(bits) != len(self.bits)):
            raise(IndexError(f"The provided bits have length {len(bits)}, but this circuit has {len(self.bits)} bits."))
        # Compute the decoded values.
        values = []
        # Cycle through the numbers and get their values (in order).
        for i in range(len(self.numbers)):
            num = self.numbers[i]
            num_len = len(num.bit_indices)
            # Compute the value of the number (encode it back into decimal).
            value = sum(bits[idx] * 2**(j+num.exponent) for j, idx
                        in enumerate(num.bit_indices[:num_len-num.signed]))
            if num.signed: value -= bits[-1] * 2**(num_len-1+num.exponent)
            value += num.constant
            # Record the (name, value, and percentage of failed and gates).
            values.append( value )
        # Fix all of the failed and gates and track the number failed.
        failed_and_gates = 0
        for ag in self.and_gates:
            # Get all involved terms in this AND gate.
            inputs = set()
            output = None
            for coef in ag:
                if coef[0] == "a": output = int(coef[1:])
                else: inputs.update(map(int,coef[1:].split('b')))
            inputs.remove(output)
            # Convert the inputs into proper indices.
            c1, c2 = [i-1 for i in inputs]
            a = output - 1
            # Check to see if the gate was violated.
            if (int(bits[c1] and bits[c2]) != bits[a]):
                failed_and_gates += 1
                # Fix the gate if it was violated.
                bits[a] = int(bits[c1] and bits[c2])
        and_failures = (None if (len(self.and_gates) == 0) else 
                        100 * failed_and_gates / len(self.and_gates))
        # Return the (list of values, and the % of and-gates broken).
        return values, and_failures
                
    # Run this circuit as if executing on a quantum annealer. Most
    # importantly, turn the binary representations back into
    # interpretable results and resolve any logical inconsistencies.
    # Also, attempt to name the numbers with the variable names from
    # the scope of the caller of this function.
    # 
    # See documentation for "qaml.run_qubo" for full list of available
    # keyword arguments to this function.
    # 
    # If you are using a custom System, then the keywork arguments for
    # the "System.samples" function could also be passed in here.
    # 
    def run(self, and_strength=1/2, min_only=True, display=True, **run_qubo_kwargs):
        from qaml import run_qubo
        from qaml.systems import System
        qubo = self.assemble(and_strength=and_strength, verbose=display)
        system = System(qubo, constant=qubo.get('c',0))
        if display: print("\n"+str(qubo)+"\n")
        results = run_qubo(qubo, min_only=False, display=False, **run_qubo_kwargs)
        # Capture all the outputs for each number.
        outputs = {}
        info_names = []
        for bits in results:
            bits_info = results.info[tuple(bits)][1:]
            # Implicitly correct and gates, count failures, get numeric values.
            values, and_fails = self.decode( bits )
            if (type(and_fails) == type(None)): and_fails = tuple()
            else:
                and_fails = (and_fails,)
                if ("and breaks" not in info_names): info_names += ["and breaks"]
            if (len(bits_info) > 1) and ("chain breaks" not in info_names):
                info_names += ["chain breaks"]
            # Compute the energy of the (corrected) set of bits.
            energy = system.energy(bits)
            # Store the information about AND failure rates and info if available.
            key = (energy,) + tuple(values)
            outputs[key] = outputs.get(key, []) + [and_fails + bits_info[:-1]] * bits_info[-1]

        # Reduce to only the minimum energy outputs if that was requested.
        # Notice this is done *after* correcting the AND gates.
        if min_only:
            min_energy = min(outputs, key=lambda k: k[0])[0]
            for k in list(outputs):
                if (k[0] > min_energy): outputs.pop(k)
        solutions = []
        # Get the names of the Number objects (for tracking / displaying).
        num_names = self._num_names()
        # Print out all of the outputs.
        printout = [num_names + info_names + ["Energy"]]
        for key in sorted(outputs):
            energy, values = key[0], key[1:]
            solutions.append(values)
            # Convert info into percentages.
            info = [sum(row[i] for row in outputs[key]) / len(outputs[key])
                    for i in range(len(info_names))]
            info = [f"{val: 5.1f}%" for val in info]
            printout += [list(map(str, values)) + info + [str(energy)]]
        # If "display", then convert the printout into a table.
        if display:
            spacer = "\t"
            # First, shift all values so they have a leading space.
            for row in printout[1:]:
                for i in range(len(row)): row[i] = " " + row[i]
            # Now find the largest width column.
            col_widths = [max(len(row[i]) for row in printout)
                          for i in range(len(printout[0]))]
            # Print the header.
            for val,width in zip(printout.pop(0), col_widths):
                print(f"{val:<{width}s}", end=spacer)
            print()
            # Print all of the rows.
            for row in printout:
                for val,width in zip(row, col_widths):
                    print(f"{val:>{width}s}", end=spacer)
                print()
        # Return the list of values that achieved desired energy performance.
        return solutions

