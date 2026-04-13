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