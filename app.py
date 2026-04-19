"""
Concrete Curing Live Monitor
=============================
run this:   python app.py
open at:    http://127.0.0.1:5000

samples sensor every 1 second but each second in simulation
represents about 6 minutes of real curing time (speed factor)
so you can watch the whole 28 day cure in about 6 hours
or just set SPEED_FACTOR higher to go faster
"""

import threading
import time

from flask import Flask, jsonify, render_template

from alarm import AlarmSystem
from data_logger import DataLogger
from maturity import MaturityCalc
from sensor_sim import ConcreateSensorSim

app     = Flask(__name__)

# ── how fast simulation runs ──────────────────────────────────
# 1 real second = SPEED_FACTOR hours of curing time
# default 0.1 means 1 sec = 6 minutes of curing
# set to 1.0 if you want 1 sec = 1 hour (very fast)
SPEED_FACTOR = 0.1

# ── global objects ────────────────────────────────────────────
sensor   = ConcreateSensorSim()
maturity = MaturityCalc()
logger   = DataLogger()
alarm    = AlarmSystem()

# fix the dt_hours based on speed factor
sensor.dt_hours = SPEED_FACTOR / 3600.0 * 3600.0  # simplifies to SPEED_FACTOR
sensor.dt_hours = SPEED_FACTOR

_last_milestone = None

# ── background sampling loop ──────────────────────────────────
def sampling_loop():
    global _last_milestone
    while True:
        reading = sensor.read()

        # update maturity with current temp and time step
        mat_idx, strength = maturity.update(reading["temp"], sensor.dt_hours)

        # check for milestone
        milestone = maturity.check_milestones()
        if milestone:
            _last_milestone = milestone

        # check alarms
        alarm.check(reading["temp"], reading["humidity"], milestone)

        # build full data row
        row = {
            "timestamp"   : reading["timestamp"],
            "elapsed_hours": reading["elapsed_hours"],
            "temp"        : reading["temp"],
            "humidity"    : reading["humidity"],
            "maturity"    : round(mat_idx, 2),
            "strength_mpa": strength,
            "strength_pct": maturity.strength_percent(),
        }
        logger.log(row)
        time.sleep(1)


t = threading.Thread(target=sampling_loop, daemon=True)
t.start()

# ── routes ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/data")
def api_data():
    global _last_milestone

    latest = logger.get_latest()
    recent = logger.get_recent(200)

    # consume the milestone so it only shows once
    ms = _last_milestone
    _last_milestone = None

    return jsonify({
        "latest"       : latest,
        "recent"       : recent,
        "alarm"        : bool(alarm.active_alarms),
        "alarm_message": alarm.summary(),
        "milestone"    : ms,
    })


@app.route("/api/fault/<ftype>", methods=["POST"])
def api_fault(ftype):
    if ftype == "clear":
        sensor.clear_fault()
        return jsonify({"ok": True})
    if ftype in ("cold_snap", "heat_spike", "curing_removed"):
        sensor.inject_fault(ftype)
        return jsonify({"ok": True})
    return jsonify({"error": "unknown fault"}), 400


@app.route("/api/reset", methods=["POST"])
def api_reset():
    global sensor, maturity, alarm, _last_milestone
    sensor         = ConcreateSensorSim()
    sensor.dt_hours = SPEED_FACTOR
    maturity       = AlarmSystem.__new__(AlarmSystem)
    maturity       = MaturityCalc()
    alarm          = AlarmSystem()
    _last_milestone = None
    logger.clear()
    return jsonify({"ok": True})


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 52)
    print("  Concrete Curing Monitor  —  server starting")
    print("  Open browser at:  http://127.0.0.1:5000")
    print("  Speed factor:", SPEED_FACTOR, "hrs per second")
    print("=" * 52 + "\n")
    app.run(debug=False)