from circuit import Circuit
from powerflow import PowerFlow

c = Circuit("Case 6.9 - Breaker Open")

# SAME DATA
c.addbus("One", 15.0, "Slack", 1.0, 0.0)
c.addbus("Two", 345.0, "PQ", 1.0, 0.0)
c.addbus("Three", 15.0, "PV", 1.05, 0.0)
c.addbus("Four", 345.0, "PQ", 1.0, 0.0)
c.addbus("Five", 345.0, "PQ", 1.0, 0.0)

c.addtransformer("T1", "One", "Five", 0.0015, 0.02)
c.addtransformer("T2", "Four", "Three", 0.00075, 0.01)

c.addtransmissionline("L1", "Five", "Four", 0.00225, 0.025, 0.0, 0.44)
c.addtransmissionline("L2", "Five", "Two", 0.0045, 0.05, 0.0, 0.88)
c.addtransmissionline("L3", "Four", "Two", 0.009, 0.1, 0.0, 1.72)

c.addgenerator("G1", "One", 1.0, 0.0)
c.addgenerator("G2", "Three", 1.05, 520.0)

c.addload("Load2", "Two", 800.0, 280.0)
c.addload("Load3", "Three", 80.0, 40.0)

# OPEN BREAKER
c.open_line("L1")

c.calc_ybus()

pf = PowerFlow(sbase=100.0)
results = pf.solve(c)

print("=== BREAKER OPEN (L1) ===")
for i, name in enumerate(results["bus_names"]):
    print(f"{name}: V={results['V'][i]:.4f}, delta={results['delta_deg'][i]:.4f}")