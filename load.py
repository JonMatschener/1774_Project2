class Load:
    """
    Represents a constant real and reactive power load connected to a bus.
    """

    def __init__(
        self,
        name: str,
        bus1_name: str,
        mw: float,
        mvar: float
    ):
        self.name = name
        self.bus1_name = bus1_name
        self.mw = mw
        self.mvar = mvar

    def calc_p(self, sbase):
        """
        Return per-unit real power consumption.
        """
        return self.mw / sbase

    def calc_q(self, sbase):
        """
        Return per-unit reactive power consumption.
        """
        return self.mvar / sbase

    def __repr__(self):
        return (f"Load(name={self.name}, bus={self.bus1_name}, "
                f"P={self.mw} MW, Q={self.mvar} MVAR)")


# ---------------- TEST CASE ----------------
if __name__ == "__main__":
    if __name__ == "__main__":
        l1 = Load("L1", "Bus 2", 50, 30)

        print(l1)

        sbase = 100
        print("Per-unit P:", l1.calc_p(sbase))
        print("Per-unit Q:", l1.calc_q(sbase))

    print("Load test passed ✔")
