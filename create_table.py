import sqlite3

conn = sqlite3.connect('Game2048Policy.db')
cursor = conn.cursor()
cursor.execute('create table state (id char(8) primary key, cnt int(64), a0_cnt int(32), a0_score float, a1_cnt int(32), a1_score float, a2_cnt int(32), a2_score float, a3_cnt int(32), a3_score float)')

def uint2chars(id_uint):
  id_char = ''
  i = 0
  while i < 8:
      id_char += chr(id_uint & 0xFF)
      id_uint = (id_uint >> 8)
      i += 1
  return id_char

i = 0xFFFFFFFFFFFFFFFF
c = uint2chars(i)
print(c)

cursor.execute('insert into state (id, cnt, a0_cnt, a0_score, a1_cnt, a1_score, a2_cnt, a2_score, a3_cnt, a3_score) values (\'' + c + '\', 0, 0, 0.0, 0, 0.0, 0, 0.0, 0, 0.0)')
cursor.rowcount
cursor.close()
conn.commit()
conn.close()
