from bus import Bus
from transformer import Transformer
from transmissionLine import TransmissionLine
from load import Load
from generator import Generator
from shunt import Shunt
import numpy as np
import pandas as pd

class Circuit:
    """
    Circuit class: container for a full power system network.
    """

    def __init__(self, name: str):
        self.name = name
        self.buses = {}
        self.transformers = {}
        self.transmissionlines = {}
        self.generators = {}
        self.loads = {}
        self.ybus = None
        self.shunts = {}

    def addbus(self, name: str, nominal_kv: float, bus_type="PQ", vpu=1.0, delta=0.0):
        if name in self.buses:
            raise ValueError(f"Bus with name '{name}' already exists.")
        self.buses[name] = Bus(name, nominal_kv, bus_type, vpu, delta)

    def addtransformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")
        self.transformers[name] = Transformer(name, bus1_name, bus2_name, r, x)

    def addtransmissionline(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float, g: float, b: float):
        if name in self.transmissionlines:
            raise ValueError(f"TransmissionLine with name '{name}' already exists.")
        self.transmissionlines[name] = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)

    def addgenerator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float, xdp=None):
        if name in self.generators:
            raise ValueError(f"Generator with name '{name}' already exists.")
        self.generators[name] = Generator(name, bus1_name, voltage_setpoint, mw_setpoint, xdp)

    def addload(self, name: str, bus1_name: str, mw: float, mvar: float):
        if name in self.loads:
            raise ValueError(f"Load with name '{name}' already exists.")
        self.loads[name] = Load(name, bus1_name, mw, mvar)

    def calc_ybus(self):
        bus_names = list(self.buses.keys())
        N = len(bus_names)

        if N == 0:
            raise ValueError("No buses in circuit. Add buses before calling calc_ybus().")

        name_to_idx = {}
        used = set()
        use_bus_index_attr = True

        for bn, bobj in self.buses.items():
            if not hasattr(bobj, "index"):
                use_bus_index_attr = False
                break

        if use_bus_index_attr:
            for bn, bobj in self.buses.items():
                if bobj.index in used:
                    use_bus_index_attr = False
                    break
                used.add(bobj.index)

        if use_bus_index_attr:
            ordered = sorted(self.buses.values(), key=lambda b: b.index)
            bus_names_ordered = [b.name for b in ordered]
            name_to_idx = {name: i for i, name in enumerate(bus_names_ordered)}
            bus_names = bus_names_ordered
        else:
            name_to_idx = {name: i for i, name in enumerate(bus_names)}

        Y = np.zeros((N, N), dtype=complex)

        def stamp_two_terminal(yprim_df: pd.DataFrame, bus1: str, bus2: str):
            if bus1 not in name_to_idx or bus2 not in name_to_idx:
                raise ValueError(f"Stamping error: bus '{bus1}' or '{bus2}' not found in circuit buses.")

            i = name_to_idx[bus1]
            j = name_to_idx[bus2]

            y11 = yprim_df.loc[bus1, bus1]
            y12 = yprim_df.loc[bus1, bus2]
            y21 = yprim_df.loc[bus2, bus1]
            y22 = yprim_df.loc[bus2, bus2]

            Y[i, i] += y11
            Y[i, j] += y12
            Y[j, i] += y21
            Y[j, j] += y22

        for t in self.transformers.values():
            yprim = t.calc_yprim()
            stamp_two_terminal(yprim, t.bus1_name, t.bus2_name)

        for line in self.transmissionlines.values():
            yprim = line.calc_yprim()
            stamp_two_terminal(yprim, line.bus1_name, line.bus2_name)

        for shunt in self.shunts.values():
            if shunt.bus1_name not in name_to_idx:
                raise ValueError(f"Shunt bus '{shunt.bus1_name}' not found in circuit buses.")

            i = name_to_idx[shunt.bus1_name]
            Y[i, i] += shunt.calc_y()

        self.ybus = pd.DataFrame(Y, index=bus_names, columns=bus_names)
        return self.ybus

    def addshunt(self, name: str, bus1_name: str, q_mvar: float, sbase=100.0):
        if name in self.shunts:
            raise ValueError(f"Shunt with name '{name}' already exists.")
        self.shunts[name] = Shunt(name, bus1_name, q_mvar, sbase)