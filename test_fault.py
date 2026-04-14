from circuit import Circuit
from powerflow import PowerFlow

c = Circuit("Fault Test")

# Add buses
c.addbus("Bus 1", 230)
c.addbus("Bus 2", 230)
c.addbus("Bus 3", 230)

# Set types
c.buses["Bus 1"].bus_type = "Slack"
c.buses["Bus 2"].bus_type = "PQ"
c.buses["Bus 3"].bus_type = "PQ"

# Add network
c.addtransformer("T1", "Bus 1", "Bus 2", 0.01, 0.1)
c.addtransmissionline("L1", "Bus 2", "Bus 3", 0.02, 0.25, 0, 0.04)

# Generator with X''
c.addgenerator("G1", "Bus 1", 1.05, 100, xdp=0.2)

# Build Ybus
c.calc_ybus()

# Solve fault
pf = PowerFlow()

result = pf.solve(c, mode="fault", fault_bus="Bus 2")

print("\nFault Current:")
print(result["Ifault"])

print("\nPost-Fault Voltages:")
print(result["V_post"])