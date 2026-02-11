class TransmissionLine:
    """
    Transmission line modeled by lumped parameters between two buses.
    Milestone 1: data container only (no calculations).
    """

    def __init__(self, name: str, bus1_name: str, bus2_name: str,
                 r: float, x: float, g: float, b: float):
        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name
        self.r = float(r)
        self.x = float(x)
        self.g = float(g)
        self.b = float(b)

    def __repr__(self):
        return (f"TransmissionLine(name={self.name!r}, bus1_name={self.bus1_name!r}, "
                f"bus2_name={self.bus2_name!r}, r={self.r}, x={self.x}, g={self.g}, b={self.b})")


if __name__ == "__main__":
    line1 = TransmissionLine("Line 1", "Bus 1", "Bus 2", 0.02, 0.25, 0.0, 0.04)
    print(line1.name, line1.bus1_name, line1.bus2_name, line1.r, line1.x, line1.g, line1.b)
