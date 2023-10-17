from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
import uuid


class CarChoice(Base):
    """ Car Choice """

    __tablename__ = "car_choice"

    id = Column(Integer, primary_key=True)
    car_id = Column(String(36), nullable=False)
    type = Column(String(250), nullable=False)
    passenger_capacity = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    make = Column(String(250), nullable=False)
    model = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)
    

    def __init__(self, car_id, type, passenger_capacity, year, make, model, trace_id):
        """ Initializes a car choice """
        self.car_id = car_id
        self.type = type
        self.passenger_capacity = passenger_capacity
        self.year = year
        self.make = make
        self.model = model
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a car choice """
        dict = {}
        dict['id'] = self.id
        dict['car_id'] = self.car_id
        dict['type'] = self.type
        dict['passenger_capacity'] = self.passenger_capacity
        dict['year'] = self.year
        dict['make'] = self.make
        dict['model'] = self.model
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
