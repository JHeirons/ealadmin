import mysql.connector

conn = mysql.connector.connect(
user = 'jonathan', 
password = 'HP224AZ',
host='192.168.0.107',
database='eal_test')

curr = conn.cursor()

query = ("SELECT * FROM equipment")

curr.execute(query)

for (id, name, model) in curr:
    print ("{}, {}, {}".format(id, name, model))
    
curr.close()
conn.close()





