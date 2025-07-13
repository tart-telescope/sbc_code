import os
import sqlite3

from tart.util import utc


def connect_to_db():
    # v1 none utc timestamps
    # v2 utc timestamps!
    con = None
    try:
        db_path = os.getenv("DB_PATH", "tart_web_api_database_v2.db")
        con = sqlite3.connect(db_path)
    except Exception as e:
        print(type(e))  # the exception instance
        print(e.args)  # arguments stored in .args
        print(e)
    return con


def setup_db(num_ant):
    with connect_to_db() as con:
        c = con.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS raw_data (Id INTEGER PRIMARY KEY, utc_timestamp TEXT, filename TEXT, checksum TEXT)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS observation_cache_process (Id INTEGER PRIMARY KEY, utc_timestamp TEXT, state TEXT)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS vis_data (Id INTEGER PRIMARY KEY, utc_timestamp TEXT, filename TEXT, checksum TEXT)"
        )
        c.execute(
            "CREATE TABLE IF NOT EXISTS vis_cache_process (Id INTEGER PRIMARY KEY, utc_timestamp TEXT, state TEXT)"
        )
        c.execute("CREATE TABLE IF NOT EXISTS sample_delay (utc_timestamp TEXT, delay REAL)")
        c.execute(
            "CREATE TABLE IF NOT EXISTS calibration (utc_timestamp TEXT, antenna INTEGER, g_abs REAL, g_phase REAL)"
        )
        c.execute("CREATE TABLE IF NOT EXISTS channels (channel_id INTEGER, enabled BOOLEAN)")
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM channels;")
        if len(c.fetchall()) == 0:
            ch = [(i, 1) for i in range(num_ant)]
            c.executemany("INSERT INTO channels(channel_id, enabled) values (?, ?)", ch)

    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM calibration;")
        if len(c.fetchall()) == 0:
            g = [
                1,
            ] * num_ant
            ph = [
                0,
            ] * num_ant
            insert_gain(c, g, ph)


def get_manual_channel_status():
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM channels;")
        rows = c.fetchall()
        ret = [{"channel_id": row[0], "enabled": row[1]} for row in rows]
    return ret


def update_manual_channel_status(channel_idx, enable):
    with connect_to_db() as con:
        c = con.cursor()
        c.execute(
            "UPDATE channels SET enabled = ? WHERE channel_id = ?",
            (enable, channel_idx),
        )


def get_sample_delay():
    ret = 0
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM sample_delay ORDER BY datetime(utc_timestamp) DESC LIMIT 1")
        rows = c.fetchall()
        if len(rows) == 0:
            ret = 0
        else:
            ret = rows[0][1]
    return ret


def insert_sample_delay(timestamp, sample_delay):
    with connect_to_db() as con:
        c = con.cursor()
        SQL = "INSERT INTO sample_delay(utc_timestamp, delay) values (?, ?)"
        c.execute(SQL, (utc.to_string(timestamp), sample_delay))
    return 1


##################
#  Antenna Gain  #
##################


def insert_gain(c, g, ph):
    utc_date = utc.now()
    for ant_i in range(len(g)):
        c.execute(
            "INSERT INTO calibration VALUES (?,?,?,?)",
            (utc.to_string(utc_date), ant_i, g[ant_i], ph[ant_i]),
        )


def get_gain():
    rows_dict = {}
    with connect_to_db() as con:
        c = con.cursor()
        c.execute(
            "SELECT utc_timestamp, antenna, g_abs, g_phase from calibration WHERE utc_timestamp = (SELECT MAX(utc_timestamp) FROM calibration) ORDER BY antenna;"
        )
        rows = c.fetchall()
        for row in rows:
            rows_dict[row[1]] = row

    return rows_dict


####################
#  Raw Data Cache  #
####################


def insert_raw_file_handle(filename, checksum):
    with connect_to_db() as con:
        c = con.cursor()
        timestamp = utc.now()
        c.execute(
            "INSERT INTO raw_data(utc_timestamp, filename, checksum) VALUES (?,?,?)",
            (utc.to_string(timestamp), filename, checksum),
        )


def remove_raw_file_handle_by_Id(Id):
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("DELETE FROM raw_data WHERE Id=?", (Id,))


def get_raw_file_handle():
    ret = ""
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM raw_data ORDER BY utc_timestamp DESC")
        rows = c.fetchall()
        ret = [
            {
                "filename": row[2],
                "timestamp": utc.from_string(row[1]),
                "checksum": row[3],
                "Id": row[0],
            }
            for row in rows
        ]
    return ret


def update_observation_cache_process_state(state):
    with connect_to_db() as con:
        c = con.cursor()
        ts = utc.now()
        c.execute(
            "UPDATE observation_cache_process SET state = ?, utc_timestamp = ? WHERE Id = ?",
            (state, utc.to_string(ts), 1),
        )


def get_observation_cache_process_state():
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM observation_cache_process")
        rows = c.fetchall()
        if len(rows) == 0:
            ret = "Error"
        else:
            ret = {"state": rows[0][2], "timestamp": rows[0][1]}
    return ret


###########################
#  Visibility Data Cache  #
###########################


def insert_vis_file_handle(filename, checksum):
    with connect_to_db() as con:
        c = con.cursor()
        timestamp = utc.now()
        c.execute(
            "INSERT INTO vis_data(utc_timestamp, filename, checksum) VALUES (?,?,?)",
            (utc.to_string(timestamp), filename, checksum),
        )


def remove_vis_file_handle_by_Id(Id):
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("DELETE FROM vis_data WHERE Id=?", (Id,))


def get_vis_file_handle():
    ret = ""
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM vis_data ORDER BY utc_timestamp DESC")
        rows = c.fetchall()
        ret = [
            {
                "filename": row[2],
                "timestamp": utc.from_string(row[1]),
                "checksum": row[3],
                "Id": row[0],
            }
            for row in rows
        ]
    return ret


def update_vis_cache_process_state(state):
    with connect_to_db() as con:
        c = con.cursor()
        ts = utc.now()
        c.execute(
            "UPDATE vis_cache_process SET state = ?, utc_timestamp = ? WHERE Id = ?",
            (state, utc.to_string(ts), 1),
        )


def get_vis_cache_process_state():
    with connect_to_db() as con:
        c = con.cursor()
        c.execute("SELECT * FROM vis_cache_process")
        rows = c.fetchall()
        if len(rows) == 0:
            ret = "Error"
        else:
            ret = {"state": rows[0][2], "timestamp": rows[0][1]}
    return ret
