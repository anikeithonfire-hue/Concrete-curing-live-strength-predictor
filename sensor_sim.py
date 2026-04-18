import numpy as np
import time


# this file simulates the sensors that are embeded inside
# a concrete slab during pouring. in real life these are
# thermocouples and humidity probes but here we fake it
# the concrete temp starts high because of hydration heat
# then slowly comes down to ambient over time

class ConcreateSensorSim:

    def __init__(self):
        # starting temp of fresh poured concrete
        # hydration reaction makes it go upto 60-70 deg C in first few hours
        self.ambient_temp   = 28.0    # outside air temp in celsius
        self.concrete_temp  = 32.0    # just poured, slightly above ambient
        self.peak_temp      = 62.0    # peak hydration temp (hit around hour 12-15)
        self.humidity       = 92.0    # concrete is wet when just poured

        self.elapsed_hours  = 0.0     # how many hours since pouring
        self.dt_hours       = 1/3600  # each tick = 1 second = 1/3600 of a hour

        # noise levels for sensors, real sensors have this
        self.temp_noise     = 0.15
        self.humid_noise    = 0.4

        # fault stuff
        self.fault_active   = False
        self.fault_type     = None

        self._tick          = 0

    def _calc_true_temp(self):
        # concrete temp profile follows a bell curve roughly
        # rises fast in first 12 hrs then drops slowly
        # this is a simplified model not exact science
        h = self.elapsed_hours

        if h < 12:
            # rising phase - hydration heat building up
            rise = (self.peak_temp - self.ambient_temp) * (h / 12.0)
            t = self.ambient_temp + rise
        else:
            # cooling phase - slowly approaches ambient over 3-4 days
            decay = np.exp(-0.018 * (h - 12))
            t = self.ambient_temp + (self.peak_temp - self.ambient_temp) * decay

        return t

    def _calc_true_humidity(self):
        # humidity drops slowly as slab dries out from surface
        # starts near 92% drops to about 65% over 28 days
        h = self.elapsed_hours
        base_humid = 92.0 - (h / 672.0) * 27.0   # 672 hrs = 28 days
        return float(np.clip(base_humid, 40.0, 95.0))

    def read(self):
        self._tick += 1
        self.elapsed_hours += self.dt_hours

        true_temp  = self._calc_true_temp()
        true_humid = self._calc_true_humidity()

        # inject faults if active
        if self.fault_active:
            if self.fault_type == "cold_snap":
                # sudden drop in ambient, slows curing badly
                true_temp = true_temp - np.random.uniform(8, 14)
            elif self.fault_type == "heat_spike":
                # too much external heat, thermal cracking risk
                true_temp = true_temp + np.random.uniform(10, 18)
            elif self.fault_type == "curing_removed":
                # somebody removed the wet burlap/plastic too early
                true_humid = true_humid - np.random.uniform(20, 35)

        # add sensor noise on top
        meas_temp  = true_temp  + np.random.normal(0, self.temp_noise)
        meas_humid = true_humid + np.random.normal(0, self.humid_noise)

        meas_temp  = float(np.clip(meas_temp,  -5.0, 90.0))
        meas_humid = float(np.clip(meas_humid,  0.0, 100.0))

        return {
            "timestamp"    : time.strftime("%Y-%m-%d %H:%M:%S"),
            "elapsed_hours": round(self.elapsed_hours, 4),
            "temp"         : round(meas_temp,  2),
            "humidity"     : round(meas_humid, 2),
        }

    def inject_fault(self, ftype):
        self.fault_active = True
        self.fault_type   = ftype

    def clear_fault(self):
        self.fault_active = False
        self.fault_type   = None