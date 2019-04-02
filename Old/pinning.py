from qubo import run_qubo

# --------------------------------------------------------------------
# Try combining gates in the most trivial way I can imagine.

print("-"*70)
print("NOT (a AND b)")
run_qubo(
    # AND gate plus pin
    a3=3+1,
    b12=1, b13=-2, b23=-2,
    
    # # pin
    # a3=+1,
    # a4=+1,
    b34=-2,

    # NOT gate plus pin
    a4=-1+1,
    a5=-1,
    b45=2,
    c = 1
)

print("-"*70)
print("NOT (a OR b)")
run_qubo(
    # OR gate plus pin
    a1=1, a2=1, a3=1+1,
    b12=1, b13=-2, b23=-2,
    
    # # pin
    # a3=+1,
    # a4=+1,
    b34=-2,

    # NOT gate plus pin
    a4=-1+1,
    a5=-1,
    b45=2,

    c = 1
)

print("-"*70)
print("c AND (a OR b)")
run_qubo(
    # OR gate plus pin
    a1=1, a2=1, a3=1+1,
    b12=1, b13=-2, b23=-2,
    
    # # pin
    # a1=+1,
    # a2=+1,
    # b12=-2,
    b34=-2,

    # AND gate plus pin
    a6=3, a4=1,
    b45=1, b46=-2, b56=-2,
)
