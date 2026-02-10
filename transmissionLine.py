class TransmissionLine:
    """
    Represents a transmission line using the pi-equivalent model.
    """

    def __init__(self, name: str, bus1: str, bus2: str, r: float, x: float, b: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.r = float(r)
        self.x = float(x)
        self.b = float(b)

        self.g = 0.0
        self.calc_y()

    def calc_y(self):
        """
        Calculates series admittance (g + jb) from R and X.
        Shunt susceptance B is handled separately as jB/2 at each bus.
        """
        z_sq = self.r**2 + self.x**2
        if z_sq == 0:
            raise ValueError("Line impedance cannot be zero")

        self.g = self.r / z_sq
        self.b_series = -self.x / z_sq

        return self.g, self.b_series

    def shunt_b_per_bus(self):
        """
        Returns shunt susceptance jB/2 applied to each bus.
        """
        return self.b / 2

    def __repr__(self):
        return (
            f"TransmissionLine(name={self.name}, "
            f"bus1={self.bus1}, bus2={self.bus2}, "
            f"r={self.r}, x={self.x}, "
            f"g={self.g}, b_series={self.b_series}, "
            f"b_shunt_total={self.b})"
        )


if __name__ == "__main__":
    line = TransmissionLine("L1", "Bus1", "Bus2", 0.02, 0.1, 0.04)
    print(line)
