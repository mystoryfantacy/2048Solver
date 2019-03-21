import sqlite3

conn = sqlite3.connect('Game2048Policy.db')

cursor = conn.cursor()

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

# 执行查询语句:
cursor.execute('select * from state where id=?', (c,))
# 获得查询结果集:
values = cursor.fetchall()
print(values)
cursor.close()
conn.close()
