from qaml import Circuit

# Create a circuit that is composed of two numbers with 3 bits of
# precision. Since we know the answer will be less than 1, we can
# place all of the precision on the fractional side of the decimal.
num_bits = 3
c = Circuit()
a = c.Number(num_bits, exponent=-num_bits, signed=False)
b = c.Number(num_bits, exponent=-num_bits, signed=False)

# Add polynomial equations to the circuit for a circle and a x=y line.
c.add( a**2 + b**2 - 1 )
c.add( a - b )

# Assemble the equations into a least squares energy function and
# execute using the default system (a brute-force exhaustive search).
q = c.run(min_only=False)
