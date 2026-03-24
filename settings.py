import numpy as np

class settings:
    """
    Stores system-wide settings for per-unit calculations.
    """

    def __init__(self, freq=60.0, sbase=100.0):
        self.freq = float(freq)      # System frequency (Hz)
        self.sbase = float(sbase)    # Base power (MVA)

    def __repr__(self):
        return f"settings(freq={self.freq}, sbase={self.sbase})"

    def initialize_voltages(self, buses):
        """
        Build the initial complex voltage vector from each bus's
        per-unit magnitude and angle.
        """
        ordered_buses = sorted(buses.values(), key=lambda b: b.index)
        V = np.zeros(len(ordered_buses), dtype=complex)

        for bus in ordered_buses:
            angle_rad = np.radians(bus.delta)
            V[bus.index] = bus.vpu * (np.cos(angle_rad) + 1j * np.sin(angle_rad))

        return V

    def compute_power_injection(self, bus, ybus, voltages):
        """
        Compute calculated real and reactive power injection at one bus.
        Returns (P_i, Q_i) in per-unit.
        """
        i = bus.index

        if hasattr(ybus, "values"):
            Y = ybus.values
        else:
            Y = ybus

        G = Y.real
        B = Y.imag

        Vi = abs(voltages[i])
        delta_i = np.angle(voltages[i])

        P_i = 0.0
        Q_i = 0.0

        for j in range(len(voltages)):
            Vj = abs(voltages[j])
            delta_j = np.angle(voltages[j])
            delta_ij = delta_i - delta_j

            P_i += Vi * Vj * (G[i, j] * np.cos(delta_ij) + B[i, j] * np.sin(delta_ij))
            Q_i += Vi * Vj * (G[i, j] * np.sin(delta_ij) - B[i, j] * np.cos(delta_ij))

        return P_i, Q_i

    def compute_power_mismatch(self, buses, ybus, voltages, circuit):
        """
        Build the Newton-Raphson mismatch vector.

        Slack bus: no mismatch terms
        PV bus: only dP
        PQ bus: dP and dQ
        """
        ordered_buses = sorted(buses.values(), key=lambda b: b.index)

        mismatch_vector = []
        mismatch_labels = []

        for bus in ordered_buses:
            P_calc, Q_calc = self.compute_power_injection(bus, ybus, voltages)

            P_spec = 0.0
            Q_spec = 0.0

            for gen in circuit.generators.values():
                if gen.bus1_name == bus.name:
                    P_spec += gen.calc_p(self.sbase)

            for load in circuit.loads.values():
                if load.bus1_name == bus.name:
                    P_spec -= load.calc_p(self.sbase)
                    Q_spec -= load.calc_q(self.sbase)

            if bus.bus_type == "Slack":
                continue

            dP = P_spec - P_calc
            mismatch_vector.append(dP)
            mismatch_labels.append(f"dP_{bus.name}")

            if bus.bus_type == "PQ":
                dQ = Q_spec - Q_calc
                mismatch_vector.append(dQ)
                mismatch_labels.append(f"dQ_{bus.name}")

        return np.array(mismatch_vector, dtype=float), mismatch_labels


if __name__ == "__main__":
    from bus import Bus
    from circuit import Circuit

    Bus.bus_index = 0

    c = Circuit("Milestone 6 Test")

    c.addbus("Bus 1", 230.0)
    c.addbus("Bus 2", 230.0)
    c.addbus("Bus 3", 230.0)

    c.buses["Bus 1"].bus_type = "Slack"
    c.buses["Bus 1"].vpu = 1.05
    c.buses["Bus 1"].delta = 0.0

    c.buses["Bus 2"].bus_type = "PV"
    c.buses["Bus 2"].vpu = 1.02
    c.buses["Bus 2"].delta = 0.0

    c.buses["Bus 3"].bus_type = "PQ"
    c.buses["Bus 3"].vpu = 1.00
    c.buses["Bus 3"].delta = 0.0

    c.addtransformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    c.addtransmissionline("L1", "Bus 2", "Bus 3", 0.02, 0.25, 0.0, 0.04)

    c.addgenerator("G1", "Bus 2", 1.02, 100.0)
    c.addload("Load1", "Bus 3", 90.0, 30.0)

    c.calc_ybus()

    s = settings(60.0, 100.0)

    V = s.initialize_voltages(c.buses)
    print("Initial voltage vector:")
    print(V)
    print()

    for bus in sorted(c.buses.values(), key=lambda b: b.index):
        P_calc, Q_calc = s.compute_power_injection(bus, c.ybus, V)
        print(bus.name, P_calc, Q_calc)

    print()

    mismatch, labels = s.compute_power_mismatch(c.buses, c.ybus, V, c)
    print("Mismatch vector:")
    for label, value in zip(labels, mismatch):
        print(label, value)

if __name__ == "__main__":
        s = settings()
        print("\nDefault Settings:", s)

        s2 = settings(freq=50, sbase=200)
        print("Custom Settings:", s2)

if __name__ == "__main__":
    from bus import Bus
    from circuit import Circuit

    Bus.bus_index = 0

    c = Circuit("Case 6.9 Milestone 6 Validation")

    # -----------------
    # Add 5 Buses from validate_case69.py
    # -----------------
    c.addbus("One", 15.0)
    c.addbus("Two", 345.0)
    c.addbus("Three", 15.0)
    c.addbus("Four", 345.0)
    c.addbus("Five", 345.0)

    # -----------------
    # Assign bus types / initial guesses
    # Simple NR-ready setup using the Case 6.9 network
    # -----------------
    c.buses["One"].bus_type = "Slack"
    c.buses["One"].vpu = 1.05
    c.buses["One"].delta = 0.0

    c.buses["Two"].bus_type = "PV"
    c.buses["Two"].vpu = 1.01
    c.buses["Two"].delta = 0.0

    c.buses["Three"].bus_type = "PQ"
    c.buses["Three"].vpu = 1.00
    c.buses["Three"].delta = 0.0

    c.buses["Four"].bus_type = "PQ"
    c.buses["Four"].vpu = 1.00
    c.buses["Four"].delta = 0.0

    c.buses["Five"].bus_type = "PQ"
    c.buses["Five"].vpu = 1.00
    c.buses["Five"].delta = 0.0

    # -----------------
    # Add the exact Case 6.9 branch data from validate_case69.py
    # -----------------
    c.addtransformer("T1", "One", "Five", 0.0015, 0.02)
    c.addtransformer("T2", "Four", "Three", 0.00075, 0.01)

    c.addtransmissionline("L1", "Five", "Four", 0.00225, 0.025, 0.00, 0.44)
    c.addtransmissionline("L2", "Five", "Two", 0.0045, 0.05, 0.00, 0.88)
    c.addtransmissionline("L3", "Four", "Two", 0.009, 0.1, 0.00, 1.72)

    # -----------------
    # Add simple generation/load for mismatch testing
    # These are for Milestone 6 validation structure.
    # -----------------
    c.addgenerator("G1", "Two", 1.01, 100.0)

    c.addload("Load1", "Three", 90.0, 30.0)
    c.addload("Load2", "Four", 100.0, 35.0)
    c.addload("Load3", "Five", 125.0, 50.0)

    # -----------------
    # Build Ybus
    # -----------------
    c.calc_ybus()

    # -----------------
    # Settings object
    # -----------------
    s = settings(60.0, 100.0)

    # -----------------
    # Initial voltage vector
    # -----------------
    V = s.initialize_voltages(c.buses)
    print("Initial voltage vector:")
    print(V)
    print()

    # -----------------
    # Calculated injections at each bus
    # -----------------
    print("Calculated injections:")
    for bus in sorted(c.buses.values(), key=lambda b: b.index):
        P_calc, Q_calc = s.compute_power_injection(bus, c.ybus, V)
        print(f"{bus.name}: P_calc={P_calc:.6f}, Q_calc={Q_calc:.6f}")
    print()

    # -----------------
    # Newton-Raphson mismatch vector
    # -----------------
    mismatch, labels = s.compute_power_mismatch(c.buses, c.ybus, V, c)
    print("Mismatch vector:")
    for label, value in zip(labels, mismatch):
        print(f"{label} = {value:.6f}")

if __name__ == "__main__":
    from bus import Bus
    from circuit import Circuit

    Bus.bus_index = 0

    c = Circuit("Case 6.9 Milestone 6 Validation")

    c.addbus("One", 15.0)
    c.addbus("Two", 345.0)
    c.addbus("Three", 15.0)
    c.addbus("Four", 345.0)
    c.addbus("Five", 345.0)

    c.buses["One"].bus_type = "Slack"
    c.buses["One"].vpu = 1.05
    c.buses["One"].delta = 0.0

    c.buses["Two"].bus_type = "PQ"
    c.buses["Two"].vpu = 1.00
    c.buses["Two"].delta = 0.0

    c.buses["Three"].bus_type = "PV"
    c.buses["Three"].vpu = 1.04
    c.buses["Three"].delta = 0.0

    c.buses["Four"].bus_type = "PQ"
    c.buses["Four"].vpu = 1.00
    c.buses["Four"].delta = 0.0

    c.buses["Five"].bus_type = "PQ"
    c.buses["Five"].vpu = 1.00
    c.buses["Five"].delta = 0.0

    c.addtransformer("T1", "One", "Five", 0.0015, 0.02)
    c.addtransformer("T2", "Four", "Three", 0.00075, 0.01)

    c.addtransmissionline("L1", "Five", "Four", 0.00225, 0.025, 0.0, 0.44)
    c.addtransmissionline("L2", "Five", "Two", 0.0045, 0.05, 0.0, 0.88)
    c.addtransmissionline("L3", "Four", "Two", 0.009, 0.1, 0.0, 1.72)

    c.addgenerator("G1", "Three", 1.04, 400.85)

    c.addload("Load1", "Two", 800.0, 150.0)
    c.addload("Load2", "Four", -37.29, -605.20)
    c.addload("Load3", "Five", 0.0, -66.0)

    c.calc_ybus()

    s = settings(60.0, 100.0)

    V = s.initialize_voltages(c.buses)
    print("Initial voltage vector:")
    print(V)
    print()

    print("Calculated injections:")
    for bus in sorted(c.buses.values(), key=lambda b: b.index):
        P_calc, Q_calc = s.compute_power_injection(bus, c.ybus, V)
        print(f"{bus.name}: P_calc={P_calc:.6f}, Q_calc={Q_calc:.6f}")
    print()

    mismatch, labels = s.compute_power_mismatch(c.buses, c.ybus, V, c)
    print("Mismatch vector:")
    for label, value in zip(labels, mismatch):
        print(f"{label} = {value:.6f}")