import SDL_Pi_INA3221
import time
import random


class AmpsReader:
    def __init__(self, resistor=1/30.0):
        self.ina3221 = SDL_Pi_INA3221(shunt_resistor=resistor)

    def read_ma(self):
        try:
            currents = []
            currents.append(self.ina3221.getCurrent_mA(1))
            currents.append(self.ina3221.getCurrent_mA(2))
            currents.append(self.ina3221.getCurrent_mA(3))
            return currents
        except OSError:
            return None


class MockAmpsReader:
    def __init__(self):
        pass

    def read_ma(self):
        return [random.uniform(1488.719419 - 700, 1488.719419 + 700),
                random.uniform(1245.458124 - 700, 1245.458124 + 700),
                random.uniform(1403.787285 - 700, 1403.787285 + 700)]


class AmpsIntegrator:
    def __init__(self, reader):
        self.reader = reader
        self.zero_current_threshold_a = 0.1
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

        # Amp seconds
        return [ma/1000.0*dt for ma in currents]
