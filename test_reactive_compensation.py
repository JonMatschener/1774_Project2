from circuit import Circuit
from powerflow import PowerFlow


def build_case69():
    c = Circuit("Case 6.9")

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

    c.addgenerator("G1", "One", 1.0, 0.0, xdp=0.2)
    c.addgenerator("G2", "Three", 1.05, 520.0, xdp=0.2)

    c.addload("Load2", "Two", 800.0, 280.0)
    c.addload("Load3", "Three", 80.0, 40.0)

    return c


def run_case(c):
    c.calc_ybus()
    pf = PowerFlow(sbase=100.0)
    return pf.solve(c, mode="powerflow", tol=0.001, max_iter=50)


base_case = build_case69()
base_results = run_case(base_case)

cap_case = build_case69()
cap_case.addshunt("Capacitor_Two", "Two", 100.0)
cap_results = run_case(cap_case)

reactor_case = build_case69()
reactor_case.addshunt("Reactor_Two", "Two", -100.0)
reactor_results = run_case(reactor_case)

bus_names = base_results["bus_names"]
bus_two_index = bus_names.index("Two")

v_base = base_results["V"][bus_two_index]
v_cap = cap_results["V"][bus_two_index]
v_reactor = reactor_results["V"][bus_two_index]

print("Reactive Compensation Test Results")
print()

print("Base Case:")
for i, name in enumerate(base_results["bus_names"]):
    print(f"{name}: V = {base_results['V'][i]:.6f} pu, angle = {base_results['delta_deg'][i]:.6f} deg")

print()

print("With 100 Mvar Capacitor at Bus Two:")
for i, name in enumerate(cap_results["bus_names"]):
    print(f"{name}: V = {cap_results['V'][i]:.6f} pu, angle = {cap_results['delta_deg'][i]:.6f} deg")

print()

print("With 100 Mvar Reactor at Bus Two:")
for i, name in enumerate(reactor_results["bus_names"]):
    print(f"{name}: V = {reactor_results['V'][i]:.6f} pu, angle = {reactor_results['delta_deg'][i]:.6f} deg")

print()

print("Bus Two Voltage Comparison:")
print(f"Base:      {v_base:.6f} pu")
print(f"Capacitor: {v_cap:.6f} pu")
print(f"Reactor:   {v_reactor:.6f} pu")

assert cap_results["converged"] is True
assert reactor_results["converged"] is True
assert v_cap > v_base
assert v_reactor < v_base

print()
print("All reactive compensation tests passed.")