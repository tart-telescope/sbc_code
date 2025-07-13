import sqlite3
from tart.util import utc

def connect_to_db():
    con = None
    try:
        dbfile = 'tart_web_api_database.db'
        con = sqlite3.connect(dbfile)
    except Exception as e:
        print(type(e))     # the exception instance
        print(e.args)      # arguments stored in .args
        print(e)
    return con


def setup_db(num_ant):
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS raw_data (Id INTEGER PRIMARY KEY, date timestamp, filename TEXT, checksum TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS observation_cache_process (Id INTEGER PRIMARY KEY, date timestamp, state TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS vis_data (Id INTEGER PRIMARY KEY, date timestamp, filename TEXT, checksum TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS vis_cache_process (Id INTEGER PRIMARY KEY, date timestamp, state TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS calibration_process (Id INTEGER PRIMARY KEY, date timestamp, state TEXT)")
        c.execute("CREATE TABLE IF NOT EXISTS sample_delay (date timestamp, delay REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS calibration (date timestamp, antenna INTEGER, g_abs REAL, g_phase REAL)")
        c.execute("CREATE TABLE IF NOT EXISTS channels (channel_id INTEGER, enabled BOOLEAN)")
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM channels;')
        if len(c.fetchall()) == 0:
            ch = [(i, 1) for i in range(num_ant)]
            c.executemany("INSERT INTO channels(channel_id, enabled) values (?, ?)", ch)
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM calibration_process;')
        if len(c.fetchall()) == 0:
            c.execute("INSERT INTO calibration_process(date, state) values (?, ?)",
                    (utc.now(), 'idle'))
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM calibration;')
        if len(c.fetchall()) == 0:
            utc_date = utc.now()
            g = [1,]*num_ant
            ph = [0,]*num_ant
            insert_gain(c, utc_date, g, ph)


def get_manual_channel_status():
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM channels;')
        rows = c.fetchall()
        ret = [{'channel_id': row[0], 'enabled': row[1]} for row in rows]
    return ret


def update_manual_channel_status(channel_idx, enable):
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('UPDATE channels SET enabled = ? WHERE channel_id = ?', (enable, channel_idx))


def get_sample_delay():
    con = connect_to_db()
    ret = 0
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM sample_delay ORDER BY datetime(date) DESC LIMIT 1')
        rows = c.fetchall()
        if len(rows) == 0:
            ret = 0
        else:
            ret = rows[0][1]
    return ret


def insert_sample_delay(timestamp, sample_delay):
    con = connect_to_db()
    with con:
        c = con.cursor()
        SQL = "INSERT INTO sample_delay(date, delay) values (?, ?)"
        c.execute(SQL, (timestamp, sample_delay))
    return 1


##################
#  Antenna Gain  #
##################


def insert_gain(c, utc_date, g, ph):
    for ant_i in range(len(g)):
        c.execute("INSERT INTO calibration VALUES (?,?,?,?)",
                  (utc_date, ant_i, g[ant_i], ph[ant_i]))


def get_gain():
    rows_dict = {}
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('SELECT date, antenna, g_abs, g_phase from calibration WHERE date = (SELECT MAX(date) FROM calibration) ORDER BY antenna;')
        rows = c.fetchall()
        for row in rows:
            rows_dict[row[1]] = row

    return rows_dict


#########################
#  Calibration Process  #
#########################


def update_calibration_process_state(state):
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('UPDATE calibration_process SET state = ? WHERE Id = ?', (state, 1))


def get_calibration_process_state():
    con = connect_to_db()
    ret = 'Error'
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM calibration_process')
        rows = c.fetchall()
        if len(rows) == 0:
            ret = 'Error'
        else:
            ret = rows[0][2]
    return ret


####################
#  Raw Data Cache  #
####################


def insert_raw_file_handle(filename, checksum):
    con = connect_to_db()
    with con:
        c = con.cursor()
        timestamp = utc.now()
        c.execute("INSERT INTO raw_data(date, filename, checksum) VALUES (?,?,?)",
                  (timestamp, filename, checksum))


def remove_raw_file_handle_by_Id(Id):
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute("DELETE FROM raw_data WHERE Id=?", (Id,))


def get_raw_file_handle():
    con = connect_to_db()
    ret = ''
    with con:
        c = con.cursor()
        c.execute("SELECT * FROM raw_data ORDER BY date DESC")
        rows = c.fetchall()
        ret = [{'filename': row[2],
                'timestamp': utc.from_string(row[1]),
                'checksum': row[3],
                'Id': row[0]} for row in rows]
    return ret


def update_observation_cache_process_state(state):
    con = connect_to_db()
    with con:
        c = con.cursor()
        ts = utc.now()
        c.execute('UPDATE observation_cache_process SET state = ?, date = ? WHERE Id = ?', (state, ts, 1))


def get_observation_cache_process_state():
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM observation_cache_process')
        rows = c.fetchall()
        if len(rows) == 0:
            ret = 'Error'
        else:
            ret = {'state':rows[0][2], 'timestamp':rows[0][1]}
    return ret


###########################
#  Visibility Data Cache  #
###########################


def insert_vis_file_handle(filename, checksum):
    con = connect_to_db()
    with con:
        c = con.cursor()
        timestamp = utc.now()
        c.execute("INSERT INTO vis_data(date, filename, checksum) VALUES (?,?,?)",
                  (timestamp, filename, checksum))


def remove_vis_file_handle_by_Id(Id):
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute("DELETE FROM vis_data WHERE Id=?", (Id,))


def get_vis_file_handle():
    con = connect_to_db()
    ret = ''
    with con:
        c = con.cursor()
        c.execute("SELECT * FROM vis_data ORDER BY date DESC")
        rows = c.fetchall()
        ret = [{'filename': row[2], 'timestamp': utc.from_string(row[1]),
                'checksum': row[3], 'Id': row[0]} for row in rows]
    return ret


def update_vis_cache_process_state(state):
    con = connect_to_db()
    with con:
        c = con.cursor()
        ts = utc.now()
        c.execute('UPDATE vis_cache_process SET state = ?, date = ? WHERE Id = ?', (state, ts, 1))


def get_vis_cache_process_state():
    con = connect_to_db()
    with con:
        c = con.cursor()
        c.execute('SELECT * FROM vis_cache_process')
        rows = c.fetchall()
        if len(rows) == 0:
            ret = 'Error'
        else:
            ret = {'state': rows[0][2], 'timestamp': rows[0][1]}
    return ret
