class Generator:
    
    def __init__(
        self,
        name: str,
        bus1_name: str,
        voltage_setpoint: float,
        mw_setpoint: float
    ):
        self.name = name
        self.bus1_name = bus1_name
        self.voltage_setpoint = float(voltage_setpoint)
        self.mw_setpoint = float(mw_setpoint)

    def __repr__(self):
        return (
            f"Generator(name={self.name!r}, "
            f"bus1_name={self.bus1_name!r}, "
            f"voltage_setpoint={self.voltage_setpoint}, "
            f"mw_setpoint={self.mw_setpoint})"
        )


# ---------------- TEST CASE ----------------
if __name__ == "__main__":
    gen = Generator("G1", "Bus 1", 1.04, 100.0)

    print(gen)

    assert gen.name == "G1"
    assert gen.bus1_name == "Bus 1"
    assert gen.voltage_setpoint == 1.04
    assert gen.mw_setpoint == 100.0

    print("Generator test passed ✔")
