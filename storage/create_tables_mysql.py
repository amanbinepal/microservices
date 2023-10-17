import mysql.connector

db_conn = mysql.connector.connect(host="aman3855.eastus2.cloudapp.azure.com", user="root", passwd="password", database="carbookings")


c = db_conn.cursor()
c.execute('''
          CREATE TABLE car_choice
          (id INT NOT NULL AUTO_INCREMENT,
           car_id VARCHAR(36) NOT NULL, 
           type VARCHAR(250) NOT NULL,
           passenger_capacity INT NOT NULL,
           year INT NOT NULL,
           make VARCHAR(250) NOT NULL,
           model VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(36) NOT NULL,
            CONSTRAINT car_choice_pk PRIMARY KEY (id))
          ''')

c.execute('''
          CREATE TABLE schedule_choice
          (id INT NOT NULL AUTO_INCREMENT,
           sched_id VARCHAR(36) NOT NULL, 
           location VARCHAR(250) NOT NULL,
           start_time VARCHAR(250) NOT NULL,
           days INT NOT NULL,
           est_kms INT NOT NULL,
           end_time VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(36) NOT NULL,
            CONSTRAINT schedule_choice_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
