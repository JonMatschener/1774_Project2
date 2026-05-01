class Shunt:
    def __init__(self, name, bus1_name, q_mvar, sbase=100.0):
        self.name = name
        self.bus1_name = bus1_name
        self.q_mvar = q_mvar
        self.sbase = sbase

    def calc_b_pu(self):
        return self.q_mvar / self.sbase

    def calc_y(self):
        return 1j * self.calc_b_pu()

    def __repr__(self):
        return f"Shunt(name={self.name}, bus={self.bus1_name}, q_mvar={self.q_mvar})"