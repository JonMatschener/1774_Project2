from circuit import Circuit
from powerflow import PowerFlow

c = Circuit("2-Bus Fault Case (Diagram Match)")

# -----------------
# BUSSING (2-bus equivalent system)
# -----------------
c.addbus("Bus 1", 13.8, "Slack", 1.0, 0.0)   # Generator side
c.addbus("Bus 2", 13.8, "PQ", 1.0, 0.0)      # Fault + load side

# -----------------
# GENERATORS (subtransient reactance included in fault model)
# -----------------
c.addgenerator("G1", "Bus 1", 1.0, 0.0, xdp=0.15)
c.addgenerator("G2", "Bus 2", 1.0, 0.0, xdp=0.20)

# -----------------
# TRANSFORMERS (T1 + T2 lumped into equivalent)
# -----------------
c.addtransformer("T1", "Bus 1", "Bus 2", 0.0, 0.10)
c.addtransformer("T2", "Bus 1", "Bus 2", 0.0, 0.10)

# -----------------
# TRANSMISSION LINE (20 ohm → pu)
# -----------------
c.addtransmissionline("Line", "Bus 1", "Bus 2", 0.0, 0.105, 0.0, 0.0)

# -----------------
# LOAD (motor equivalent at Bus 2)
# -----------------
c.addload("Load", "Bus 2", 0.8, 0.28)

# -----------------
# BUILD NETWORK
# -----------------
c.calc_ybus()

# -----------------
# FAULT SOLVER
# -----------------
pf = PowerFlow()

result = pf.solve(
    c,
    mode="fault",
    fault_bus="Bus 2"
)

# -----------------
# OUTPUT
# -----------------
print("\nFault Current:")
print(result["Ifault"])

print("\nPost-Fault Voltages:")
for name, v in zip(result["bus_names"], result["V_post"]):
    print(f"{name}: {v}")