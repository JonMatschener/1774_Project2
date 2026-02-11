class Transformer:
    """
    Transformer modeled by its series impedance (r + jx) between two buses.
    Milestone 1: data container only (no calculations).
    """

    def __init__(self, name: str, bus1_name: str, bus2_name: str, r: float, x: float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = float(r)
        self.x = float(x)

    def __repr__(self):
        return (f"Transformer(name={self.name!r}, bus1_name={self.bus1_name!r}, "
                f"bus2_name={self.bus2_name!r}, r={self.r}, x={self.x})")


if __name__ == "__main__":
    t1 = Transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)
    print(t1.name, t1.bus1_name, t1.bus2_name, t1.r, t1.x)
