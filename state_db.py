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

def existtable():
    sql = "SELECT EXISTS(SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'state')"
    c = _execute(sql)
    v = c.fetchone()
    return v[0] == 1

def createtable():
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

def insert(state,
           cnt = 0,
           a0_cnt = 0, a1_cnt = 0, a2_cnt = 0, a3_cnt = 0,
           a0_score = 0.0, a1_score = 0.0, a2_score = 0.0, a3_score = 0.0):
    global conn
    global cursor
    sql = 'insert into state values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    c = uint2chars(state)
    value = (c, cnt, a0_cnt, a0_score, a1_cnt, a1_score, a2_cnt, a2_score, a3_cnt, a3_score)
    _execute(sql, value)
    conn.commit()

def query(state):
    global conn
    global cursor
    c = uint2chars(state)
    sql = 'select * from state where id=?'
    cursor.execute(sql, (c,))
    values = cursor.fetchall()
    return values[0]

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
    if not existtable():
        print('create table')
        createtable()
    i = 0xFFFFFFFFFFFFFFFF
    if not exists(i):
        insert(state = i)
    print(query(i))
    update(state = i, cnt = 1, a3_cnt = 1, a3_score = 1.0)
    print(query(i))
    j = 0x7FFFFFFFFFFFFFFF
    exists(j)
    delete(i)
    closedb()

