# The return type for the "System.samples" method.
class Sample(list):
    _bits = None
    _energy = None
    _chain_break_fraction = None
    _occurrence = 1

    # Protect the "bits" property as a tuple.
    @property
    def bits(self): return self._bits
    @bits.setter
    def bits(self, value): self._bits = tuple(value)

    # Protect the "energy" property as a float.
    @property
    def energy(self): return self._energy
    @energy.setter
    def energy(self, value): self._energy = float(value)

    # Protect the "chain_break_fraction" property as a float.
    @property
    def chain_break_fraction(self): return self._chain_break_fraction
    @chain_break_fraction.setter
    def chain_break_fraction(self, value): self._chain_break_fraction = float(value)

    # Protect the "occurrence" property as an integer.
    @property
    def occurrence(self): return self._occurrence
    @occurrence.setter
    def occurrence(self, value): self._occurrence = int(value)

    # Iterate over the three values that can be stored in this Sample.
    def __iter__(self):
        yield self._bits
        yield self._energy
        yield self._chain_break_fraction

# Base class for producing samples from a quantum system.
class System():
    # Initialize this ExhaustiveSearch with the provided coefficients.
    def __init__(self, coefficients, constant=0):
        from qaml.qubo import make_dwave_qubo
        self.coefficients = make_dwave_qubo(**coefficients)
        self.num_bits = max(map(max, self.coefficients)) + 1
        self.constant = constant

    # Given a set of bits, compute the energy of that set of bits and return it.
    def energy(self, bits):
        if (len(bits) != self.num_bits):
            from qaml.exceptions import UsageError
            raise(UsageError(f"Expected {self.num_bits}, but received {len(bits)}."))
        energy = 0.0
        for (i1, i2) in self.coefficients:
            if (bits[i1] and bits[i2]):
                energy += self.coefficients[(i1,i2)]
        return energy + self.constant

    # Generate samples from the system, yield bits and energy.
    def samples(self):
        from qaml.exceptions import UsageError
        raise(UsageError("The sample method has not been defined for this System."))

# This is a simple brute force quantum annealer base class, designed
# to be subclassed by more advanced techniques.
class ExhaustiveSearch(System):
    # Generate samples from the system, yield bits and energy.
    def samples(self, num_samples=1000):
        from qaml.qubo import number_to_bits
        from qaml.rand import random_range
        for number in random_range(2**self.num_bits, count=num_samples):
            bits = number_to_bits(number, self.num_bits)
            output = Sample()
            output.bits = bits
            output.energy = self.energy(bits)
            yield output

# A wrapper for the crappy provided solver by QBSolv, this defines a
# more readable interface for QBSolv, the built-in simulator.
class QBSolve(System):
    # Do the pecuiliar steps necessary to generate samples from QBSolv.
    def samples(self, num_samples=20):
        from dwave_qbsolv import QBSolv
        for i in range(num_samples):
            system = QBSolv().sample_qubo(self.coefficients)
            for out in system.samples(1): pass
            # Construct a "Sample" output and return it.
            output = Sample()
            output.bits = (out[b] for b in sorted(out))
            output.energy = system.data_vectors["energy"][0] + self.constant
            # Yield the output.
            yield output

# When this annealer is used, the program is actually run on the real
# hardware. The results are returned. This sampler provides the
# following keyword arguments when using the "sample" method:
# 
#    num_samples           -- (integer) The number of samples to run
#                             on the hardware.
#    embedding_attempts    -- (integer) The number of embedding attempts
#                             used to find QUBO embedding.
#    chain_strength [None] -- (float) The relative strength of chains,
#                             is 1/2 max Ising magnitude by default.
#    verbose [True]        -- (bool) True shows descriptive printouts.
#    fix_chains [False]    -- (bool) True uses manual chain fixing,
#                             WARNING: outputs are less varied when True.
# 
# Returns a generator of ([bit values], energy) pairs.
# 
class QuantumAnnealer(System):
    # Do the pecuiliar steps necessary to generate samples from QBSolv.
    def samples(self, num_samples=20, embedding_attempts=5, 
                chain_strength=(1/2), verbose=True, fix_chains=False):
        # Import required local modules.
        from qaml.qubo import qubo_ising_rescale_factor
        from qaml.setup import token
        # Construct a sampler over a real quantum annealer.
        from dwave.system.samplers import DWaveSampler
        from minorminer import find_embedding
        sampler = DWaveSampler(token=token)
        # Construct an automatic embedding over the machine architecture.
        _, edgelist, adjacency = sampler.structure
        # Attempt to embed multiple times (with seeds for
        # repeatability), and take the best embedding found.
        best_embedding = None
        smallest_max_len = float('inf')
        # Construct a QUBO with no 0-valued coefficients in it.
        qubo_no_zeros = {c:self.coefficients[c] for c in self.coefficients
                         if (self.coefficients[c] != 0)}
        # Cycle embedding attempts.
        for i in range(embedding_attempts):
            embedding = find_embedding(qubo_no_zeros, edgelist, random_seed=i)
            # Count the number of chains of each length.
            lens = list(map(len, embedding.values()))
            # Check to see if this is the best embedding yet.
            if (len(lens) > 0) and (max(lens) < smallest_max_len):
                smallest_max_len = max(lens)
                best_embedding = embedding
        # Verify that there were embeddings discovered.
        if (type(best_embedding) == type(None)):
            from qaml.exceptions import UnsolvableSystem
            raise(UnsolvableSystem("No physical embeddings could be discovered for the provided QUBO."))
        # Use the best embedding found.
        embedding = best_embedding
        lens = list(map(len, embedding.values()))
        if verbose:
            print()
            print("Max chain length of", max(lens))
            print("Chain length distribution:")
            for i in range(1,max(lens)+1):
                if i not in lens: continue
                count = lens.count(i)
                print("", i, "chain --", "#"*count)
            print()
            print(f"Using embedding with {sum(lens[k] for k in lens)} qubits:")
            for i in sorted(embedding):
                print("", i, embedding[i])
            print()
        # Automatically set the chain strength based on the rescale
        # factor that will be applied to the Ising model.
        rescale_factor = qubo_ising_rescale_factor(self.coefficients)
        chain_strength *= rescale_factor
        if verbose:
            print(f"Ising rescale factor: {rescale_factor}")
            print(f"Using chain strength: {chain_strength}")
            print()
        if fix_chains:
            # Pick the method for fixing broken chains.
            from dwave.embedding.chain_breaks import \
                majority_vote, weighted_random, MinimizeEnergy
            method = majority_vote
            # Submit the job via an embedded BinaryQuadraticModel.
            import dimod
            from dimod import BinaryQuadraticModel as BQM
            from dwave.embedding import embed_bqm, unembed_sampleset
            # Generate a BQM from the QUBO.
            q = BQM.from_qubo(qubo_no_zeros)
            # Embed the BQM onto the target structure.
            embedded_q = embed_bqm(q, embedding, adjacency,
                                   chain_strength=chain_strength,
                                   smear_vartype=dimod.SPIN)
            # Collect the sample output.
            response = unembed_sampleset(
                sampler.sample(embedded_q, num_reads=num_samples),
                embedding, q, chain_break_method=method,
                chain_break_fraction=True)
        else:
            # Use a FixedEmbeddingComposite if we don't care about chains.
            from dwave.system.composites import FixedEmbeddingComposite
            system_composite = FixedEmbeddingComposite(
                sampler, embedding)
            response = system_composite.sample_qubo(
                qubo_no_zeros, num_reads=num_samples, chain_strength=chain_strength)
        # Cycle through the results and yield them to the caller.
        for out in response.data():
            # Get the output from the data.
            output = Sample()
            output.bits = (out.sample[b] for b in sorted(out.sample))
            output.energy = out.energy + self.constant
            output.chain_break_fraction = out.chain_break_fraction
            output.occurrence = out.num_occurrences
            # Yield the output.
            yield output



