class Bus:
    """
    Represents a power system bus.

    Attributes
    ----------
    name : str
        Name of the bus.
    nominal_kv : float
        Nominal voltage level of the bus (kV).
    index : int
        Unique index assigned to the bus.
    """
    bus_index = 0

    VALID_TYPES = {"Slack", "PQ", "PV"}

    def __init__(self, name: str, nominal_kv: float,
                 bus_type="PQ", vpu=1.0, delta=0.0):
        self.name = name
        self.nominal_kv = float(nominal_kv)

        if bus_type not in Bus.VALID_TYPES:
            raise ValueError(f"Invalid bus type: {bus_type}")

        self.bus_type = bus_type
        self.vpu = float(vpu)       # Voltage magnitude (per-unit)
        self.delta = float(delta)   # Voltage angle (degrees)

        self.index = Bus.bus_index
        Bus.bus_index += 1

    def __repr__(self):
        return (f"Bus(name={self.name!r}, "
                f"nominal_kv={self.nominal_kv}, "
                f"index={self.index})")


if __name__ == "__main__":
    b1 = Bus("Bus 1", 230, "Slack", 1.05, 0.0)
    b2 = Bus("Bus 2", 115, "PQ", 1.0, -5.0)
    b3 = Bus("Bus 3", 115, "PV", 1.02, 0.0)

    print(b1)
    print(b2)
    print(b3)