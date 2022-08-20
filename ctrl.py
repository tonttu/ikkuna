import threading
import time
from event import Event


class RelayCtrl:
    def __init__(self, rcfg):
        self.rcfg = rcfg
        self.last_activate = time.time()
        self.safety_time = 1.0

    def up(self):
        self.safety_throttle()
        print("UP")

    def down(self):
        self.safety_throttle()
        print("DOWN")

    def stop(self):
        print("STOP")

    def safety_throttle(self):
        while time.time() - self.last_activate < self.safety_time:
            time.sleep(max(0, self.safety_time -
                       (time.time() - self.last_activate)))


class RelayCfg:
    def __init__(self, up_relays, down_relays, up_as, down_as, max_time):
        self.up_relays = up_relays
        self.down_relays = down_relays
        self.up_as = up_as
        self.down_as = down_as
        self.max_time = max_time


class Window(threading.Thread):
    def __init__(self, rctrl, integrator):
        threading.Thread.__init__(self)
        self.pos = None  # unknown
        self.target = None
        self.stop_ = False
        self.stat = "stopped"
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.rctrl = rctrl
        self.integrator = integrator
        self.on_stat = Event()
        self.on_pos = Event()
        self.start()

    def run(self):
        while True:
            with self.lock:
                while self.target is None or (self.pos is not None and abs(self.pos - self.target) < 1.0):
                    self.cv.wait()
                tgt = self.target
                self.target = None
            self.work(tgt)

    def stop(self):
        with self.lock:
            self.stop_ = True
            self.target = None

    def set_target(self, target):
        with self.lock:
            if target is not None:
                self.stop_ = False
            self.target = target
            self.cv.notify_all()

    def work(self, tgt):
        if tgt >= 100.0 or (self.pos is not None and tgt > self.pos):
            self.go(tgt, up=True)
        elif tgt <= 0.0 or (self.pos is not None and tgt < self.pos):
            self.go(tgt, up=False)
        elif self.pos is None:
            self.go(tgt, up=True)

    def go(self, tgt, up):
        print("Go", tgt, up)
        try:
            if up:
                self.set_stat("opening")
                units_per_ampsecond = 100.0 / self.rctrl.rcfg.up_as
                self.rctrl.up()
            else:
                self.set_stat("closing")
                units_per_ampsecond = 100.0 / self.rctrl.rcfg.down_as
                self.rctrl.down()

            self.integrator.start()
            start_time = time.time()
            while time.time() - start_time < self.rctrl.rcfg.max_time:
                with self.lock:
                    if self.stop_:
                        self.stop_ = False
                        break
                    if self.target is not None:
                        if (up and self.target >= tgt) or (not up and self.target <= tgt):
                            tgt = self.target
                            self.target = None
                        else:
                            break

                ampseconds = self.integrator.sample()
                # Sometimes the reading just fails
                if ampseconds is None:
                    continue

                zeroes = ampseconds.count(0)
                # All three sensors report zero, so we definitely have stopped now
                if zeroes == 3:
                    if up:
                        self.set_pos(100)
                    else:
                        self.set_pos(0)
                    break

                # If two sensors have stopped on our way up, we better stop
                # before the last one twists the window
                if zeroes == 2 and up:
                    self.set_pos(100)
                    break

                pos = 0 if self.pos is None else self.pos
                total = sum(ampseconds)
                if up:
                    self.set_pos(pos +
                                 units_per_ampsecond * total)
                    if self.pos != 100 and self.pos >= tgt:
                        break
                else:
                    self.set_pos(pos -
                                 units_per_ampsecond * total)
                    if self.pos != 0 and self.pos <= tgt:
                        break
        finally:
            self.rctrl.stop()
            if self.pos == 0.0:
                self.set_stat("closed")
            elif self.pos == 100.0:
                self.set_stat("open")
            else:
                self.set_stat("stopped")

    def set_pos(self, newpos):
        newpos = max(0.0, min(100.0, newpos))
        if newpos != self.pos:
            notify = self.pos is None or int(self.pos) != int(newpos)
            self.pos = newpos
            if notify:
                self.on_pos(self.pos)

    def set_stat(self, newstat):
        if newstat != self.stat:
            self.stat = newstat
            self.on_stat(self.stat)
