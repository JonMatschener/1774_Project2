from bus import Bus
from transformer import Transformer
from transmissionLine import TransmissionLine
from load import Load
from generator import Generator
import numpy as np
import pandas as pd

class Circuit:
    """
    Circuit class: container for a full power system network.

    Attributes (all dictionaries except name):
    - buses: dict[str, Bus]
    - transformers: dict[str, Transformer]
    - transmissionlines: dict[str, TransmissionLine]
    - generators: dict[str, Generator]
    - loads: dict[str, Load]

    Dictionary keys are component names (strings).
    Dictionary values are the corresponding equipment objects.
    """

    def __init__(self, name: str):
        self.name = name

        self.buses = {}
        self.transformers = {}
        self.transmissionlines = {}
        self.generators = {}
        self.loads = {}
        self.ybus = None

    # -------------------------
    # Add Methods
    # -------------------------
    def addbus(self, name: str, nominal_kv: float):
        """
        Creates a Bus object and stores it in self.buses using 'name' as key.
        """
        if name in self.buses:
            raise ValueError(f"Bus with name '{name}' already exists.")
        self.buses[name] = Bus(name, nominal_kv)

    def addtransformer(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        """
        Creates a Transformer object and stores it in self.transformers using 'name' as key.
        """
        if name in self.transformers:
            raise ValueError(f"Transformer with name '{name}' already exists.")
        self.transformers[name] = Transformer(name, bus1_name, bus2_name, r, x)

    def addtransmissionline(self, name: str, bus1_name: str, bus2_name: str,
                            r: float, x: float, g: float, b: float):
        """
        Creates a TransmissionLine object and stores it in self.transmissionlines using 'name' as key.
        """
        if name in self.transmissionlines:
            raise ValueError(f"TransmissionLine with name '{name}' already exists.")
        self.transmissionlines[name] = TransmissionLine(name, bus1_name, bus2_name, r, x, g, b)

    def addgenerator(self, name: str, bus1_name: str, voltage_setpoint: float, mw_setpoint: float):
        """
        Creates a Generator object and stores it in self.generators using 'name' as key.
        """
        if name in self.generators:
            raise ValueError(f"Generator with name '{name}' already exists.")
        self.generators[name] = Generator(name, bus1_name, voltage_setpoint, mw_setpoint)

    def addload(self, name: str, bus1_name: str, mw: float, mvar: float):
        """
        Creates a Load object and stores it in self.loads using 'name' as key.
        """
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
            # Build list ordered by Bus.index (0..N-1 expected)
            ordered = sorted(self.buses.values(), key=lambda b: b.index)
            bus_names_ordered = [b.name for b in ordered]
            name_to_idx = {name: i for i, name in enumerate(bus_names_ordered)}
            bus_names = bus_names_ordered
        else:
            # Fall back: insertion order of dict keys
            name_to_idx = {name: i for i, name in enumerate(bus_names)}

        # NxN complex zero matrix
        Y = np.zeros((N, N), dtype=complex)

        # Helper: stamp a 2x2 primitive matrix into Ybus
        def stamp_two_terminal(yprim_df: pd.DataFrame, bus1: str, bus2: str):
            if bus1 not in name_to_idx or bus2 not in name_to_idx:
                raise ValueError(f"Stamping error: bus '{bus1}' or '{bus2}' not found in circuit buses.")

            i = name_to_idx[bus1]
            j = name_to_idx[bus2]

            # Ensure we pull values in the correct labeled order
            y11 = yprim_df.loc[bus1, bus1]
            y12 = yprim_df.loc[bus1, bus2]
            y21 = yprim_df.loc[bus2, bus1]
            y22 = yprim_df.loc[bus2, bus2]

            # 4) Accumulate (do not overwrite)
            Y[i, i] += y11
            Y[i, j] += y12
            Y[j, i] += y21
            Y[j, j] += y22

        # 3) Iterate through all power delivery elements and stamp
        for t in self.transformers.values():
            yprim = t.calc_yprim()  # must be a labeled DataFrame
            stamp_two_terminal(yprim, t.bus1_name, t.bus2_name)

        for line in self.transmissionlines.values():
            yprim = line.calc_yprim()  # must be a labeled DataFrame
            stamp_two_terminal(yprim, line.bus1_name, line.bus2_name)

        # 5) Optional numerical checks (useful for debugging/checkoff)
        # Diagonal nonzero for connected buses (not a hard fail here)
        # Symmetry check for passive networks
        # (If you want hard enforcement, change these to raise ValueError.)
        if not np.allclose(Y, Y.T, atol=1e-12):
            # Not raising by default; just a helpful warning-style comment.
            pass

        # 6) Store result as labeled DataFrame
        self.ybus = pd.DataFrame(Y, index=bus_names, columns=bus_names)
if __name__ == "__main__":
    circuit1 = Circuit("Test Circuit")

    print(circuit1.name)
    print(type(circuit1.name))

    print(circuit1.buses)
    print(type(circuit1.buses))
    print(circuit1.transformers)
    print(circuit1.transmissionlines)
    print(circuit1.generators)
    print(circuit1.loads)

    circuit1.addbus("Bus 1", 20.0)
    circuit1.addbus("Bus 2", 230.0)

    print(list(circuit1.buses.keys()))
    print(circuit1.buses["Bus 1"].name, circuit1.buses["Bus 1"].nominal_kv)

    circuit1.addtransformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    print(list(circuit1.transformers.keys()))
    print(circuit1.transformers["T1"].name,
          circuit1.transformers["T1"].bus1_name,
          circuit1.transformers["T1"].bus2_name,
          circuit1.transformers["T1"].r,
          circuit1.transformers["T1"].x)

    circuit1.addtransmissionline("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)
    print(list(circuit1.transmissionlines.keys()))
    print(circuit1.transmissionlines["Line 1"].name,
          circuit1.transmissionlines["Line 1"].bus1_name,
          circuit1.transmissionlines["Line 1"].bus2_name,
          circuit1.transmissionlines["Line 1"].r,
          circuit1.transmissionlines["Line 1"].x,
          circuit1.transmissionlines["Line 1"].g,
          circuit1.transmissionlines["Line 1"].b)

    circuit1.addload("Load 1", "Bus 2", 50.0, 30.0)
    print(list(circuit1.loads.keys()))
    print(circuit1.loads["Load 1"].name,
          circuit1.loads["Load 1"].bus1_name,
          circuit1.loads["Load 1"].mw,
          circuit1.loads["Load 1"].mvar)

    circuit1.addgenerator("G1", "Bus 1", 1.04, 100.0)
    print(list(circuit1.generators.keys()))
    print(circuit1.generators["G1"].name,
          circuit1.generators["G1"].bus1_name,
          circuit1.generators["G1"].voltage_setpoint,
          circuit1.generators["G1"].mw_setpoint)

if __name__ == "__main__":
    #ms4 test
    c = Circuit("MS4 Test")

    c.addbus("Bus 1", 230.0)
    c.addbus("Bus 2", 230.0)

    c.addtransformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    c.addtransmissionline("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)

    c.calc_ybus()
    print(c.ybus)