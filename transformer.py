class Transformer:
    """
    Represents a simplified transformer modeled as a series impedance
    between two buses.
    """

    def __init__(self, name: str, bus1: str, bus2: str, r: float, x: float):
        self.name = name
        self.bus1 = bus1
        self.bus2 = bus2
        self.r = float(r)
        self.x = float(x)

        self.g = 0.0
        self.b = 0.0

        self.calc_y()

    def calc_y(self):
        """
        Calculates series admittance Y = 1 / (R + jX)
        Stores real part (g) and imaginary part (b)
        """
        z_sq = self.r**2 + self.x**2
        if z_sq == 0:
            raise ValueError("Transformer impedance cannot be zero")

        self.g = self.r / z_sq
        self.b = -self.x / z_sq

        return self.g, self.b

    def __repr__(self):
        return (
            f"Transformer(name={self.name}, "
            f"bus1={self.bus1}, bus2={self.bus2}, "
            f"r={self.r}, x={self.x}, "
            f"g={self.g}, b={self.b})"
        )


if __name__ == "__main__":
    t = Transformer("T1", "Bus1", "Bus2", 0.01, 0.05)
    print(t)
