import pandas as pd


class TransmissionLine:
    """
    Transmission line modeled using per-unit
    series and shunt parameters.
    """

    def __init__(self, name: str, bus1_name: str,
                 bus2_name: str, r: float, x: float,
                 g: float, b: float):

        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name

        self.r = float(r)
        self.x = float(x)
        self.g = float(g)
        self.b = float(b)

        # Series admittance
        self.Yseries = 1 / complex(self.r, self.x)

        # Shunt admittance
        self.Yshunt = complex(self.g, self.b)

    def calc_yprim(self):
        """
        Returns the 2x2 primitive admittance matrix
        for the pi-model transmission line.
        """

        y = self.Yseries
        ysh_half = self.Yshunt / 2

        data = [
            [y + ysh_half, -y],
            [-y, y + ysh_half]
        ]

        return pd.DataFrame(
            data,
            index=[self.bus1_name, self.bus2_name],
            columns=[self.bus1_name, self.bus2_name]
        )


# ---------------- VALIDATION ----------------
if __name__ == "__main__":

    line1 = TransmissionLine(
        "Line 1", "Bus 1", "Bus 2",
        0.02, 0.25, 0.0, 0.04
    )

    print("Line Yseries:")
    print(line1.Yseries)

    print("\nLine Yshunt:")
    print(line1.Yshunt)

    print("\nLine Yprim:")
    print(line1.calc_yprim())
