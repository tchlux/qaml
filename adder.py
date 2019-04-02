from qubo import QUBO
from qubo import run_qubo


# Given four bit indices (integers), generate a QUBO for x+y=s+2c.
def half_adder(x=1, y=2, s=3, c=4):
    return QUBO({f"a{x}" : 1, f"a{y}" : 1, f"a{s}" : 1, f"a{c}" : 4,
                 f"b{x}b{y}" : 2, f"b{x}b{s}" : -2, f"b{x}b{c}" : -4,
                 f"b{y}b{s}" : -2, f"b{y}b{c}" : -4, f"b{s}b{c}" : 4,
                 })

# Given five bit indices (integers), generate a QUBO for x+y+z=s+2c.
def full_adder(x=1, y=2, z=3, s=4, c=5):
    return QUBO({f"a{x}" : 1, f"a{y}" : 1, f"a{z}" : 1, 
                 f"a{s}" : 1, f"a{c}" : 4,
                 f"b{x}b{y}" : 2, f"b{x}b{z}" : 2,
                 f"b{x}b{s}" : -2, f"b{x}b{c}" : -4,
                 f"b{y}b{z}" : 2, f"b{y}b{s}" : -2, f"b{y}b{c}" : -4, 
                 f"b{z}b{s}" : -2, f"b{z}b{c}" : -4,
                 f"b{s}b{c}" : 4,
                 })
    
if __name__=='__main__':
    print ('=====half-adder')
    run_qubo(**half_adder())
    print ('=====full-adder')
    run_qubo(**full_adder())

