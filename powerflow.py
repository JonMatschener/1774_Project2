import numpy as np
import pandas as pd


class PowerFlow:
    def __init__(self, sbase=100.0):
        self.sbase = float(sbase)

    def solve(self, circuit, mode="powerflow", fault_bus=None, tol=0.001, max_iter=50):

        if mode == "powerflow":
            return self._solve_powerflow(circuit, tol=tol, max_iter=max_iter)

        elif mode == "fault":
            return self._solve_fault(circuit, fault_bus)

        else:
            raise ValueError("Invalid mode")

    def _solve_powerflow(self, circuit, tol=0.001, max_iter=50):
        if circuit.ybus is None:
            circuit.calc_ybus()

        ybus = circuit.ybus
        if isinstance(ybus, pd.DataFrame):
            Y = ybus.to_numpy(dtype=complex)
            ordered_bus_names = list(ybus.index)
        else:
            Y = np.array(ybus, dtype=complex)
            ordered_bus_names = list(circuit.buses.keys())

        ordered_buses = [circuit.buses[name] for name in ordered_bus_names]
        n = len(ordered_buses)

        name_to_idx = {name: i for i, name in enumerate(ordered_bus_names)}

        bus_types = []
        for bus in ordered_buses:
            bus_types.append(bus.bus_type)

        for gen in circuit.generators.values():
            idx = name_to_idx[gen.bus1_name]
            bus = ordered_buses[idx]
            if bus.bus_type != "Slack":
                bus.bus_type = "PV"
            bus.vpu = gen.voltage_setpoint

        V = np.ones(n, dtype=float)
        delta = np.zeros(n, dtype=float)

        for i, bus in enumerate(ordered_buses):
            if bus.bus_type == "Slack":
                V[i] = bus.vpu
                delta[i] = np.radians(bus.delta)
            elif bus.bus_type == "PV":
                V[i] = bus.vpu
                delta[i] = 0.0
            else:
                V[i] = 1.0
                delta[i] = 0.0

        P_spec = np.zeros(n, dtype=float)
        Q_spec = np.zeros(n, dtype=float)

        for gen in circuit.generators.values():
            idx = name_to_idx[gen.bus1_name]
            P_spec[idx] += gen.calc_p(self.sbase)

        for load in circuit.loads.values():
            idx = name_to_idx[load.bus1_name]
            P_spec[idx] -= load.calc_p(self.sbase)
            Q_spec[idx] -= load.calc_q(self.sbase)

        slack_idx = []
        pv_idx = []
        pq_idx = []

        for i, bus in enumerate(ordered_buses):
            if bus.bus_type == "Slack":
                slack_idx.append(i)
            elif bus.bus_type == "PV":
                pv_idx.append(i)
            else:
                pq_idx.append(i)

        angle_buses = pv_idx + pq_idx
        voltage_buses = pq_idx

        converged = False

        for iteration in range(1, max_iter + 1):
            P_calc, Q_calc = self._calc_power(Y, V, delta)
            mismatch = self._build_mismatch(P_spec, Q_spec, P_calc, Q_calc, angle_buses, voltage_buses)

            if np.max(np.abs(mismatch)) < tol:
                converged = True
                break

            J = self._build_jacobian(Y, V, delta, P_calc, Q_calc, angle_buses, voltage_buses)

            try:
                dx = np.linalg.solve(J, mismatch)
            except np.linalg.LinAlgError:
                raise ValueError("Jacobian is singular. Newton-Raphson failed.")

            nang = len(angle_buses)
            ddelta = dx[:nang]
            dV = dx[nang:]

            for k, i in enumerate(angle_buses):
                delta[i] += ddelta[k]

            for k, i in enumerate(voltage_buses):
                V[i] += dV[k]

        for i, bus in enumerate(ordered_buses):
            bus.vpu = V[i]
            bus.delta = np.degrees(delta[i])

        return {
            "converged": converged,
            "iterations": iteration,
            "V": V,
            "delta_deg": np.degrees(delta),
            "bus_names": ordered_bus_names
        }

    def _solve_fault(self, circuit, fault_bus):

        if circuit.ybus is None:
            circuit.calc_ybus()

        Ybus = circuit.ybus.to_numpy(dtype=complex)

        # -------------------------
        # STEP 1: Add generator subtransient admittance
        # -------------------------
        name_to_idx = {name: i for i, name in enumerate(circuit.ybus.index)}

        for gen in circuit.generators.values():
            idx = name_to_idx[gen.bus1_name]
            Ybus[idx, idx] += gen.get_admittance()

        # -------------------------
        # STEP 2: Build Zbus
        # -------------------------
        Zbus = np.linalg.inv(Ybus)

        # -------------------------
        # STEP 3: Fault location
        # -------------------------
        fault_idx = name_to_idx[fault_bus]

        # Assume prefault voltage = 1∠0
        V_prefault = np.ones(len(Ybus), dtype=complex)

        # -------------------------
        # STEP 4: Fault current
        # -------------------------
        Znn = Zbus[fault_idx, fault_idx]

        Ifault = V_prefault[fault_idx] / Znn

        # -------------------------
        # STEP 5: Post-fault voltages
        # -------------------------
        V_post = np.zeros_like(V_prefault, dtype=complex)

        for i in range(len(V_post)):
            V_post[i] = V_prefault[i] - Zbus[i, fault_idx] * Ifault

        return {
            "Ifault": Ifault,
            "V_post": V_post,
            "Zbus": Zbus,
            "bus_names": list(circuit.ybus.index)
        }

    def _calc_power(self, Y, V, delta):
        n = len(V)
        G = Y.real
        B = Y.imag

        P = np.zeros(n, dtype=float)
        Q = np.zeros(n, dtype=float)

        for i in range(n):
            for j in range(n):
                angle = delta[i] - delta[j]
                P[i] += V[i] * V[j] * (G[i, j] * np.cos(angle) + B[i, j] * np.sin(angle))
                Q[i] += V[i] * V[j] * (G[i, j] * np.sin(angle) - B[i, j] * np.cos(angle))

        return P, Q

    def _build_mismatch(self, P_spec, Q_spec, P_calc, Q_calc, angle_buses, voltage_buses):
        dP = []
        dQ = []

        for i in angle_buses:
            dP.append(P_spec[i] - P_calc[i])

        for i in voltage_buses:
            dQ.append(Q_spec[i] - Q_calc[i])

        return np.array(dP + dQ, dtype=float)

    def _build_jacobian(self, Y, V, delta, P_calc, Q_calc, angle_buses, voltage_buses):
        G = Y.real
        B = Y.imag

        npv_pq = len(angle_buses)
        npq = len(voltage_buses)

        J1 = np.zeros((npv_pq, npv_pq), dtype=float)
        J2 = np.zeros((npv_pq, npq), dtype=float)
        J3 = np.zeros((npq, npv_pq), dtype=float)
        J4 = np.zeros((npq, npq), dtype=float)

        for a, i in enumerate(angle_buses):
            for b, j in enumerate(angle_buses):
                if i == j:
                    J1[a, b] = -Q_calc[i] - B[i, i] * V[i] * V[i]
                else:
                    angle = delta[i] - delta[j]
                    J1[a, b] = V[i] * V[j] * (G[i, j] * np.sin(angle) - B[i, j] * np.cos(angle))

        for a, i in enumerate(angle_buses):
            for b, j in enumerate(voltage_buses):
                if i == j:
                    J2[a, b] = (P_calc[i] / V[i]) + G[i, i] * V[i]
                else:
                    angle = delta[i] - delta[j]
                    J2[a, b] = V[i] * (G[i, j] * np.cos(angle) + B[i, j] * np.sin(angle))

        for a, i in enumerate(voltage_buses):
            for b, j in enumerate(angle_buses):
                if i == j:
                    J3[a, b] = P_calc[i] - G[i, i] * V[i] * V[i]
                else:
                    angle = delta[i] - delta[j]
                    J3[a, b] = -V[i] * V[j] * (G[i, j] * np.cos(angle) + B[i, j] * np.sin(angle))

        for a, i in enumerate(voltage_buses):
            for b, j in enumerate(voltage_buses):
                if i == j:
                    J4[a, b] = (Q_calc[i] / V[i]) - B[i, i] * V[i]
                else:
                    angle = delta[i] - delta[j]
                    J4[a, b] = V[i] * (G[i, j] * np.sin(angle) - B[i, j] * np.cos(angle))

        top = np.hstack((J1, J2))
        bottom = np.hstack((J3, J4))
        return np.vstack((top, bottom))