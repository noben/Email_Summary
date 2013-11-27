import sqlite3

conn = sqlite3.connect('../bc3/bc3.db')

c = conn.cursor()

print "========================================Thread============================"
for row in c.execute('SELECT * FROM thread'):
        print row
print "========================================email============================"        
for row in c.execute('SELECT * FROM email'):
        print row
print "========================================sentence============================"        
for row in c.execute('SELECT * FROM sentence'):
        print row
print "========================================feature============================"        
for row in c.execute('SELECT * FROM feature'):
        print row        
        
        