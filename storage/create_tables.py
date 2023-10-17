import sqlite3

conn = sqlite3.connect('carbookings.sqlite')

c = conn.cursor()
c.execute('''
          CREATE TABLE car_choice
          (id INTEGER PRIMARY KEY ASC, 
           type VARCHAR(250) NOT NULL,
           passenger_capacity INTEGER NOT NULL,
           year INTEGER NOT NULL,
           make VARCHAR(250) NOT NULL,
           model VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(36) NOT NULL)
          ''')

c.execute('''
          CREATE TABLE schedule_choice
          (id INTEGER PRIMARY KEY ASC, 
           location VARCHAR(250) NOT NULL,
           start_time VARCHAR(250) NOT NULL,
           days INTEGER NOT NULL,
           est_kms INTEGER NOT NULL,
           end_time VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(36) NOT NULL)
          ''')

conn.commit()
conn.close()
