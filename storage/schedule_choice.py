from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime
import uuid

class ScheduleChoice(Base):
    """ Schedule Choice """

    __tablename__ = "schedule_choice"

    id = Column(Integer, primary_key=True)
    sched_id = Column(String(36), nullable=False)
    location = Column(String(250), nullable=False)
    start_time = Column(String(250), nullable=False)
    days = Column(Integer, nullable=False)
    est_kms = Column(Integer, nullable=False)
    end_time = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(String(36), nullable=False)
    

    def __init__(self, sched_id, location, start_time, days, est_kms, end_time, trace_id):
        """ Initializes a car choice """
        self.sched_id = sched_id
        self.location = location
        self.start_time = start_time
        self.days = days
        self.est_kms = est_kms
        self.end_time = end_time
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        """ Dictionary Representation of a car choice """
        dict = {}
        dict['id'] = self.id
        dict['sched_id'] = self.sched_id
        dict['location'] = self.location
        dict['start_time'] = self.start_time
        dict['days'] = self.days
        dict['est_kms'] = self.est_kms
        dict['end_time'] = self.end_time
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
