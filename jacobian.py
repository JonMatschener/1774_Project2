import numpy as np


class Jacobian:

    def __init__(self):
        self.matrix = None


    def calc_jacobian(self, buses, ybus, voltages):

        ordered = sorted(buses.values(), key=lambda b: b.index)

        Y = ybus
        G = Y.real
        B = Y.imag

        pq_buses = []
        pv_buses = []

        for bus in ordered:
            if bus.bus_type == "PQ":
                pq_buses.append(bus)
            elif bus.bus_type == "PV":
                pv_buses.append(bus)

        angle_buses = [b for b in ordered if b.bus_type != "Slack"]
        voltage_buses = pq_buses

        nP = len(angle_buses)
        nQ = len(voltage_buses)

        J1 = np.zeros((nP, nP))
        J2 = np.zeros((nP, nQ))
        J3 = np.zeros((nQ, nP))
        J4 = np.zeros((nQ, nQ))

        for i, bus_i in enumerate(angle_buses):

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])

            for j, bus_j in enumerate(angle_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:

                    sum_term = 0

                    for k in range(len(voltages)):

                        Vk = abs(voltages[k])
                        deltak = np.angle(voltages[k])

                        sum_term += Vi * Vk * (
                            -G[bus_i.index, k] * np.sin(deltai - deltak)
                            + B[bus_i.index, k] * np.cos(deltai - deltak)
                        )

                    J1[i, j] = sum_term

                else:

                    J1[i, j] = Vi * Vj * (
                        G[bus_i.index, bus_j.index]
                        * np.sin(deltai - deltaj)
                        - B[bus_i.index, bus_j.index]
                        * np.cos(deltai - deltaj)
                    )

        for i, bus_i in enumerate(angle_buses):

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])

            for j, bus_j in enumerate(voltage_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:

                    sum_term = 0

                    for k in range(len(voltages)):

                        Vk = abs(voltages[k])
                        deltak = np.angle(voltages[k])

                        sum_term += Vk * (
                            G[bus_i.index, k] * np.cos(deltai - deltak)
                            + B[bus_i.index, k] * np.sin(deltai - deltak)
                        )

                    J2[i, j] = sum_term * 2 * Vi

                else:

                    J2[i, j] = Vi * (
                        G[bus_i.index, bus_j.index]
                        * np.cos(deltai - deltaj)
                        + B[bus_i.index, bus_j.index]
                        * np.sin(deltai - deltaj)
                    )

        for i, bus_i in enumerate(voltage_buses):

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])

            for j, bus_j in enumerate(angle_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:

                    sum_term = 0

                    for k in range(len(voltages)):

                        Vk = abs(voltages[k])
                        deltak = np.angle(voltages[k])

                        sum_term += Vi * Vk * (
                            G[bus_i.index, k] * np.cos(deltai - deltak)
                            + B[bus_i.index, k] * np.sin(deltai - deltak)
                        )

                    J3[i, j] = -sum_term

                else:

                    J3[i, j] = -Vi * Vj * (
                        G[bus_i.index, bus_j.index]
                        * np.cos(deltai - deltaj)
                        + B[bus_i.index, bus_j.index]
                        * np.sin(deltai - deltaj)
                    )

        for i, bus_i in enumerate(voltage_buses):

            Vi = abs(voltages[bus_i.index])
            deltai = np.angle(voltages[bus_i.index])

            for j, bus_j in enumerate(voltage_buses):

                Vj = abs(voltages[bus_j.index])
                deltaj = np.angle(voltages[bus_j.index])

                if bus_i.index == bus_j.index:

                    sum_term = 0

                    for k in range(len(voltages)):

                        Vk = abs(voltages[k])
                        deltak = np.angle(voltages[k])

                        sum_term += Vk * (
                            G[bus_i.index, k] * np.sin(deltai - deltak)
                            - B[bus_i.index, k] * np.cos(deltai - deltak)
                        )

                    J4[i, j] = -2 * Vi * sum_term

                else:

                    J4[i, j] = Vi * (
                        G[bus_i.index, bus_j.index]
                        * np.sin(deltai - deltaj)
                        - B[bus_i.index, bus_j.index]
                        * np.cos(deltai - deltaj)
                    )

        top = np.hstack((J1, J2))
        bottom = np.hstack((J3, J4))

        self.matrix = np.vstack((top, bottom))

        return self.matrix