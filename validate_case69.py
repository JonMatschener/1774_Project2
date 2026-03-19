from circuit import Circuit

c = Circuit("Case 6.9")

# -----------------
# Add 5 Buses
# -----------------
c.addbus("One", 15.0)
c.addbus("Two", 345.0)
c.addbus("Three", 15.0)
c.addbus("Four", 345.0)
c.addbus("Five", 345.0)

# -----------------
# Add 2 Transformers
# -----------------
c.addtransformer("T1", "One", "Five", 0.0015, 0.02)
c.addtransformer("T2", "Four", "Three", 0.00075, 0.01)

# -----------------
# Add 3 Transmission Lines
# -----------------
c.addtransmissionline("L1", "Five", "Four", 0.00225, 0.025, 0.00, 0.44)
c.addtransmissionline("L2", "Five", "Two", 0.0045, 0.05, 0.00, 0.88)
c.addtransmissionline("L3", "Four", "Two", 0.009, 0.1, 0.00, 1.72)

# -----------------
# Compute Ybus
# -----------------
c.calc_ybus()
print(c.ybus.to_string())
print(c.transmissionlines["L2"].r)