class settings:
    """
    Stores system-wide settings for per-unit calculations.
    """

    def __init__(self, freq=60.0, sbase=100.0):
        self.freq = float(freq)      # System frequency (Hz)
        self.sbase = float(sbase)    # Base power (MVA)

    def __repr__(self):
        return f"settings(freq={self.freq}, sbase={self.sbase})"

if __name__ == "__main__":
        s = settings()
        print("Default Settings:", s)

        s2 = settings(freq=50, sbase=200)
        print("Custom Settings:", s2)