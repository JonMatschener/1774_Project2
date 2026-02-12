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

    def __init__(self, name: str, nominal_kv: float):
        self.name = name
        self.nominal_kv = float(nominal_kv)

        self.index = Bus.bus_index
        Bus.bus_index += 1

    def __repr__(self):
        return (f"Bus(name={self.name!r}, "
                f"nominal_kv={self.nominal_kv}, "
                f"index={self.index})")


if __name__ == "__main__":
    bus1 = Bus("Bus 1", 230)
    bus2 = Bus("Bus 2", 115)

    print(bus1.name, bus1.nominal_kv, bus1.index)
    print(bus2.name, bus2.nominal_kv, bus2.index)
