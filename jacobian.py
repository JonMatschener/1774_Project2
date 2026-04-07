import numpy as np

class Jacobian:
    """
    Builds the Newton-Raphson Jacobian matrix.

    Structure:
        J = [J1  J2
             J3  J4]

    J1 = dP/dδ
    J2 = dP/dV
    J3 = dQ/dδ
    J4 = dQ/dV
    """

    def calc_jacobian(self, buses, ybus, voltages, settings):

        # -------------------------
        # Step 1: Sort buses by index
        # -------------------------
        ordered = sorted(buses.values(), key=lambda b: b.index)

        # -------------------------
        # Step 2: Extract Ybus
        # -------------------------
        Y = ybus.values if hasattr(ybus, "values") else ybus
        G = Y.real
        B = Y.imag

        # -------------------------
        # Step 3: Build variable lists
        # -------------------------
        angle_buses = []     # δ variables (all except slack)
        voltage_buses = []   # V variables (only PQ)

        for bus in ordered:
            if bus.bus_type != "Slack":
                angle_buses.append(bus)
            if bus.bus_type == "PQ":
                voltage_buses.append(bus)

        # -------------------------
        # Step 4: Create Jacobian matrix
        # -------------------------
        n = len(angle_buses) + len(voltage_buses)
        J = np.zeros((n, n))

        # Helper function
        def get_PQ(bus):
            return settings.compute_power_injection(bus, ybus, voltages)

        # =========================
        # Step 5: Fill J1 and J2
        # =========================
        for i, bus_i in enumerate(angle_buses):

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])
            Pi, Qi = get_PQ(bus_i)

            # ---------- J1: dP/dδ ----------
            for j, bus_j in enumerate(angle_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if i == j:
                    # Diagonal
                    J[i, j] = -Qi - B[bus_i.index, bus_i.index] * Vi**2
                else:
                    # Off-diagonal
                    J[i, j] = Vi * Vj * (
                        G[bus_i.index, bus_j.index]*np.sin(deltai - deltaj)
                        - B[bus_i.index, bus_j.index]*np.cos(deltai - deltaj)
                    )

            # ---------- J2: dP/dV ----------
            for j, bus_j in enumerate(voltage_buses):

                col = len(angle_buses) + j
                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:
                    # Diagonal
                    J[i, col] = (Pi / Vi) + G[bus_i.index, bus_i.index]*Vi
                else:
                    # Off-diagonal
                    J[i, col] = Vi * (
                        G[bus_i.index, bus_j.index]*np.cos(deltai - deltaj)
                        + B[bus_i.index, bus_j.index]*np.sin(deltai - deltaj)
                    )

        # =========================
        # Step 6: Fill J3 and J4
        # (ONLY PQ buses)
        # =========================
        for i, bus_i in enumerate(voltage_buses):

            row = len(angle_buses) + i

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])
            Pi, Qi = get_PQ(bus_i)

            # ---------- J3: dQ/dδ ----------
            for j, bus_j in enumerate(angle_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:
                    J[row, j] = Pi - G[bus_i.index, bus_i.index]*Vi**2
                else:
                    J[row, j] = -Vi * Vj * (
                        G[bus_i.index, bus_j.index]*np.cos(deltai - deltaj)
                        + B[bus_i.index, bus_j.index]*np.sin(deltai - deltaj)
                    )

            # ---------- J4: dQ/dV ----------
            for j, bus_j in enumerate(voltage_buses):

                col = len(angle_buses) + j

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:
                    J[row, col] = (Qi / Vi) - B[bus_i.index, bus_i.index]*Vi
                else:
                    J[row, col] = Vi * (
                        G[bus_i.index, bus_j.index]*np.sin(deltai - deltaj)
                        - B[bus_i.index, bus_j.index]*np.cos(deltai - deltaj)
                    )

        return J

    def pretty_print(self, J, buses):
        """
        Prints Jacobian in labeled 4-quadrant format
        """

        ordered = sorted(buses.values(), key=lambda b: b.index)

        # Build variable lists again (same logic as calc)
        angle_buses = []
        voltage_buses = []

        for bus in ordered:
            if bus.bus_type != "Slack":
                angle_buses.append(bus)
            if bus.bus_type == "PQ":
                voltage_buses.append(bus)

        # Labels
        angle_labels = [f"δ_{b.name}" for b in angle_buses]
        voltage_labels = [f"V_{b.name}" for b in voltage_buses]

        col_labels = angle_labels + voltage_labels

        row_labels = []
        for b in angle_buses:
            row_labels.append(f"dP_{b.name}")
        for b in voltage_buses:
            row_labels.append(f"dQ_{b.name}")

        n_angle = len(angle_buses)

        print("\n=========== JACOBIAN MATRIX ===========\n")

        # Header
        header = " " * 12 + "| "
        for label in angle_labels:
            header += f"{label:>10} "
        header += "| "
        for label in voltage_labels:
            header += f"{label:>10} "
        print(header)

        print("-" * len(header))

        # Rows
        for i, row_label in enumerate(row_labels):

            row_str = f"{row_label:<12}| "

            # Left block (J1 or J3)
            for j in range(n_angle):
                row_str += f"{J[i, j]:10.4f} "

            row_str += "| "

            # Right block (J2 or J4)
            for j in range(n_angle, J.shape[1]):
                row_str += f"{J[i, j]:10.4f} "

            print(row_str)

            # Divider between P and Q blocks
            if i == n_angle - 1:
                print("-" * len(header))

        print("\n(J1 = dP/dδ, J2 = dP/dV, J3 = dQ/dδ, J4 = dQ/dV)\n")

# Test Case

    if __name__ == "__main__":
        from circuit import Circuit
        from bus import Bus
        from settings import settings
        from jacobian import Jacobian

        import numpy as np

        # Reset indexing (IMPORTANT)
        Bus.bus_index = 0

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
        # Assign bus types + initial guesses
        # -----------------
        c.buses["One"].bus_type = "Slack"
        c.buses["One"].vpu = 1.00
        c.buses["One"].delta = 0.0

        c.buses["Two"].bus_type = "PQ"
        c.buses["Two"].vpu = 1.00
        c.buses["Two"].delta = 0.0

        c.buses["Three"].bus_type = "PV"
        c.buses["Three"].vpu = 1.05
        c.buses["Three"].delta = 0.0

        c.buses["Four"].bus_type = "PQ"
        c.buses["Four"].vpu = 1.00
        c.buses["Four"].delta = 0.0

        c.buses["Five"].bus_type = "PQ"
        c.buses["Five"].vpu = 1.00
        c.buses["Five"].delta = 0.0

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
        # Add Generator
        # -----------------
        c.addgenerator("G1", "Three", 1.05, 520.0)

        # -----------------
        # Add Loads
        # -----------------
        c.addload("Load2", "Two", 800.0, 280.0)
        c.addload("Load3", "Three", 80.0, 40.0)

        # -----------------
        # Compute Ybus
        # -----------------
        c.calc_ybus()

        print("\nYbus Matrix:")
        print(c.ybus.to_string())

        # -----------------
        # Settings
        # -----------------
        s = settings(60.0, 100.0)

        # -----------------
        # Voltage vector
        # -----------------
        V = s.initialize_voltages(c.buses)

        print("\nInitial Voltage Vector:")
        print(V)

        # -----------------
        # Power Injections
        # -----------------
        print("\nCalculated Injections:")
        for bus in sorted(c.buses.values(), key=lambda b: b.index):
            P_calc, Q_calc = s.compute_power_injection(bus, c.ybus, V)
            print(f"{bus.name}: {P_calc * 100:.2f} MW, {Q_calc * 100:.2f} Mvar")

        # -----------------
        # Mismatch
        # -----------------
        mismatch, labels = s.compute_power_mismatch(c.buses, c.ybus, V, c)

        print("\nMismatch Vector:")
        for label, value in zip(labels, mismatch):
            if label.startswith("dP"):
                print(f"{label} = {value * 100:.2f} MW")
            else:
                print(f"{label} = {value * 100:.2f} Mvar")

        # -----------------
        # Jacobian
        # -----------------
        jac = Jacobian()
        J = jac.calc_jacobian(c.buses, c.ybus, V, s)

        print("\nJacobian Matrix:")
        jac.pretty_print(J, c.buses)

        # -----------------
        # Dimension Check
        # -----------------
        print("\nChecks:")
        print("Jacobian shape:", J.shape)
        print("Mismatch length:", len(mismatch))

        # -----------------
        # Newton Step
        # -----------------
        dx = np.linalg.solve(J, mismatch)

        print("\nNewton Step (dx):")
        print(dx)