import mysql.connector

conn = mysql.connector.connect(
user = 'jonathan', 
password = 'HP224AZ',
host='192.168.0.103',
database='eal_admin')

curr = conn.cursor()

query = ("SELECT * FROM equipment")

curr.execute(query)

items = curr.fetchall()
for item in items:
    print (item)
    
curr.close()
conn.close()





