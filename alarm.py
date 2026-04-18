# alarm system for the curing monitor
# two types of alarms here:
#   1. process alarms  - temp or humidity went out of safe range
#   2. milestone alerts - strength just crossed a construction threshold
#
# in real construction site these would trigger SMS to site engineer
# here we just show them on the dashboard

# safe curing temperature range for OPC cement
TEMP_MIN  = 5.0    # below 5 deg hydration is too slow
TEMP_MAX  = 70.0   # above 70 thermal cracking risk goes up

# humidity should stay high for proper surface curing
HUMID_MIN = 50.0   # if drops below this surface drying is happening


class AlarmSystem:

    def __init__(self):
        self.active_alarms  = []
        self.last_milestone = None
        self.status         = "GREEN"  # GREEN or RED

    def check(self, temp, humidity, milestone_msg=None):
        self.active_alarms = []

        # check temperature limits
        if temp < TEMP_MIN:
            self.active_alarms.append(
                f"COLD CURING: {temp}C is below minimum {TEMP_MIN}C — strength gain slowing down"
            )
        elif temp > TEMP_MAX:
            self.active_alarms.append(
                f"OVERHEATING: {temp}C exceeds {TEMP_MAX}C — thermal cracking risk"
            )

        # check humidity
        if humidity < HUMID_MIN:
            self.active_alarms.append(
                f"DRY SURFACE: humidity {humidity}% below {HUMID_MIN}% — surface curing compromised"
            )

        # milestone notification comes from maturity calc
        if milestone_msg:
            self.last_milestone = milestone_msg

        self.status = "RED" if self.active_alarms else "GREEN"
        return bool(self.active_alarms)

    def summary(self):
        if not self.active_alarms:
            return "Curing conditions normal"
        return " | ".join(self.active_alarms)