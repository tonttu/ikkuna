import SDL_Pi_INA3221
import time
import random


class AmpsReader:
    def __init__(self, resistor=1/30.0):
        self.ina3221 = SDL_Pi_INA3221.SDL_Pi_INA3221(shunt_resistor=resistor)

    def read_ma(self):
        try:
            return [self.ina3221.getCurrent_mA(i + 1) for i in range(3)]
        except OSError:
            return None


class MockAmpsReader:
    def __init__(self):
        pass

    def read_ma(self):
        return [random.uniform(i - 700, i + 700) for i in [1488.7, 1245.5, 1403.8]]


class AmpsIntegrator:
    def __init__(self, reader):
        self.reader = reader
        self.zero_current_threshold_ma = 100
        # Ideally should match the filtering parameters in ina3221
        self.sample_interval = 1/60.0

    def start(self):
        self.last_sample_time = time.time()

    def sample(self):
        time.sleep(max(0, self.sample_interval -
                       (time.time() - self.last_sample_time)))

        currents = self.reader.read_ma()
        now = time.time()
        dt = now - self.last_sample_time
        self.last_sample_time = now

        if currents is None:
            return None

        currents = [
            0 if ma < self.zero_current_threshold_ma else ma for ma in currents]

        # Amp seconds
        return [ma/1000.0*dt for ma in currents]
