import pandas as pd


class Transformer:
    """
    Transformer modeled by its series impedance (r + jx)
    using per-unit values.
    """

    def __init__(self, name: str, bus1_name: str,
                 bus2_name: str, r: float, x: float):

        self.name = name
        self.bus1_name = bus1_name
        self.bus2_name = bus2_name

        self.r = float(r)
        self.x = float(x)

        # Compute series admittance
        self.Yseries = 1 / complex(self.r, self.x)

    def calc_yprim(self):
        """
        Returns the 2x2 primitive admittance matrix
        for a pure series element.
        """

        y = self.Yseries

        data = [
            [y, -y],
            [-y, y]
        ]

        return pd.DataFrame(
            data,
            index=[self.bus1_name, self.bus2_name],
            columns=[self.bus1_name, self.bus2_name]
        )


# ---------------- VALIDATION ----------------
if __name__ == "__main__":

    transformer1 = Transformer("T1", "Bus 1", "Bus 2", 0.01, 0.10)

    print("Transformer Yseries:")
    print(transformer1.Yseries)

    print("\nTransformer Yprim:")
    print(transformer1.calc_yprim())
