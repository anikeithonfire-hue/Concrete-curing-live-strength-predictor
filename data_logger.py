import sqlite3

# logs every sensor reading + calculated maturity and strength
# into a local sqlite database, one row per second
# this is importent for construction records because
# if something goes wrong with the slab you have proof
# of the curing history

DB = "curing_log.db"


class DataLogger:

    def __init__(self):
        self._setup_db()

    def _setup_db(self):
        con = sqlite3.connect(DB)
        con.execute("""
            CREATE TABLE IF NOT EXISTS curing (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp      TEXT,
                elapsed_hours  REAL,
                temp           REAL,
                humidity       REAL,
                maturity       REAL,
                strength_mpa   REAL,
                strength_pct   REAL
            )
        """)
        con.commit()
        con.close()

    def log(self, data: dict):
        # data dict must have all the keys above
        con = sqlite3.connect(DB)
        con.execute(
            """INSERT INTO curing
               (timestamp, elapsed_hours, temp, humidity, maturity, strength_mpa, strength_pct)
               VALUES (?,?,?,?,?,?,?)""",
            (
                data["timestamp"],
                data["elapsed_hours"],
                data["temp"],
                data["humidity"],
                data["maturity"],
                data["strength_mpa"],
                data["strength_pct"],
            )
        )
        con.commit()
        con.close()

    def get_latest(self):
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        row = con.execute(
            "SELECT * FROM curing ORDER BY id DESC LIMIT 1"
        ).fetchone()
        con.close()
        return dict(row) if row else None

    def get_recent(self, n=200):
        # last n readings, oldest first for charting
        con = sqlite3.connect(DB)
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT * FROM curing ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        con.close()
        return [dict(r) for r in reversed(rows)]

    def clear(self):
        con = sqlite3.connect(DB)
        con.execute("DELETE FROM curing")
        con.commit()
        con.close()