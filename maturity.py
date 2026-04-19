# maturity method for concrete strength prediction
# based on nurse-saul equation which is a standard
# method used in construction industry worldwide
# basically says : strength depends on temperature X time
# cold weather = slower curing, hot weather = faster curing
# below -10 deg C hydration basically stops completley

T_DATUM   = -10.0
F28       = 30.0
BETA      = 900.0


class MaturityCalc:

    def __init__(self):
        self.maturity_index  = 0.0
        self.strength_mpa    = 0.0
        self._milestones_hit = set()

    def update(self, temp_c, dt_hours):
        # nurse saul step - add contribution of this time step
        contribution = max(0.0, (temp_c - T_DATUM)) * dt_hours
        self.maturity_index += contribution

        M = self.maturity_index
        self.strength_mpa = F28 * (M / (BETA + M))
        self.strength_mpa = round(self.strength_mpa, 3)

        return self.maturity_index, self.strength_mpa

    def strength_percent(self):
        return round((self.strength_mpa / F28) * 100, 1)

    def check_milestones(self):
        pct = self.strength_percent()
        milestones = {
            25 : "25% strength — formwork can be partially loosened",
            50 : "50% strength — light loads allowed on slab",
            70 : "70% strength — normal construction loads ok",
            100: "100% design strength — full load capacity reached",
        }
        for threshold, msg in milestones.items():
            if pct >= threshold and threshold not in self._milestones_hit:
                self._milestones_hit.add(threshold)
                return msg
        return None

    def estimated_days_to_full(self):
        target_M  = BETA * (0.95 / 0.05)
        remaining = max(0.0, target_M - self.maturity_index)
        return round(remaining, 1)