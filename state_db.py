import sqlite3

conn = None
cursor = None

def _execute(sql, value = None, commit = False):
    global conn
    global cursor
    if value:
        cursor.execute(sql, value)
    else:
        cursor.execute(sql)
    if commit:
        conn.commit()
    return cursor


def opendb():
    global conn
    global cursor
    conn = sqlite3.connect('Game2048Policy.db')
    cursor = conn.cursor()

def exist_table():
    sql = "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'state')"
    c = _execute(sql)
    v = c.fetchone()
    return v[0] == 1

def create_table():
    _execute('create table state (id char(8) primary key, cnt int(64), a0_cnt int(32), a0_score float, a1_cnt int(32), a1_score float, a2_cnt int(32), a2_score float, a3_cnt int(32), a3_score float)', commit = True)

def closedb():
    global conn
    global cursor
    cursor.close()
    conn.close()

def uint2chars(id_uint):
    id_char = ''
    i = 0
    while i < 8:
        id_char += chr(id_uint & 0xFF)
        id_uint = (id_uint >> 8)
        i += 1
    return id_char

uint64_mask = (1 << 64) - 1
def chars2uint(id_char):
    id_uint = 0
    i = 0
    while i < 8:
        j = ord(id_char[i])
        id_uint |= (j << (8 * i))
        i += 1
    #id_uint &= uint64_mask
    return id_uint

def insert(state,
           cnt = 0,
           a0_cnt = 0, a1_cnt = 0, a2_cnt = 0, a3_cnt = 0,
           a0_score = 0.0, a1_score = 0.0, a2_score = 0.0, a3_score = 0.0):
    sql = 'insert into state values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    c = uint2chars(state)
    value = (c, cnt, a0_cnt, a0_score, a1_cnt, a1_score, a2_cnt, a2_score, a3_cnt, a3_score)
    _execute(sql, value, commit = True)

def query(state):
    c = uint2chars(state)
    sql = 'select * from state where id=?'
    cursor = _execute(sql, (c,))
    values = cursor.fetchall()
    if len(values) < 1:
        return None
    assert(len(values) == 1)
    values = values[0]
    return [chars2uint(values[0]), values[1],
            values[2], values[3], values[4], values[5],
            values[6], values[7], values[8], values[9]]

def try_query(state):
    sql = 'SELECT EXISTS(SELECT 1 FROM state WHERE id=?)';
    state = uint2chars(state)
    c = _execute(sql, (state,))
    v = c.fetchone()
    if v[0] == 1:
        sql = 'select * from state where id=?'
        c = _execute(sql, (state,))
        v = c.fetchall()[0]
        return [chars2uint(v[0]), v[1],
                v[2], v[3], v[4], v[5],
                v[6], v[7], v[8], v[9]]
    else:
        return None



def update(state,
           cnt = 0,
           a0_cnt = 0, a1_cnt = 0, a2_cnt = 0, a3_cnt = 0,
           a0_score = 0.0, a1_score = 0.0, a2_score = 0.0, a3_score = 0.0):
    sql = 'update state set cnt = ?, a0_cnt = ?, a0_score = ?, a1_cnt = ?, a1_score = ?, a2_cnt = ?, a2_score = ?, a3_cnt = ?, a3_score = ? where id = ?'
    c = uint2chars(state)
    v = (cnt, a0_cnt, a0_score, a1_cnt, a1_score, a2_cnt, a2_score, a3_cnt, a3_score, c)
    _execute(sql, value = v, commit = True)

def exists(state):
    sql = 'SELECT EXISTS(SELECT 1 FROM state WHERE id=?)';
    c = _execute(sql, (uint2chars(state),))
    v = c.fetchone()
    return v[0] == 1

def delete(state):
    sql = 'DELETE FROM state where id=?'
    v = (uint2chars(state),)
    _execute(sql, v, commit = True)

if __name__ == '__main__':
    opendb()
    if not exist_table():
        print('create table')
        create_table()
    i = 0xFFFFFFFFFFFFFFFF
    print('test id =', i)
    if not exists(i):
        insert(state = i)
    print(query(i))
    update(state = i, cnt = 1, a3_cnt = 1, a3_score = 1.0)
    print(query(i))
    j = 0x7FFFFFFFFFFFFFFF
    exists(j)
    print(query(j))
    delete(i)
    closedb()

