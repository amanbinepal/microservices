import mysql.connector

db_conn = mysql.connector.connect(host="aman3855.eastus2.cloudapp.azure.com", user="root", passwd="password", database="carbookings")

c = db_conn.cursor()
c.execute('''
          DROP TABLE car_choice, schedule_choice
          ''')

db_conn.commit()
db_conn.close()