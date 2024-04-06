import sqlite3

con=sqlite3.connect("fov.14.sqlite")
cur=con.cursor()

#print(cur.execute("""SELECT name FROM sqlite_master WHERE type='table';""").fetchall())
temp = cur.execute("""SELECT * FROM results""").fetchall()
listing = [[hex(num) for num in i if num is not None] for i in temp]
with open("test.txt",'w') as f:
    for i in listing:
        f.write(str(i)+"\n")