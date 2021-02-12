from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DATETIME, JSON, TEXT, BOOLEAN

Base = declarative_base()


class Event(Base):
    __tablename__ = 'Event'

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_message = Column(Integer, unique=True)
    max_user = Column(Integer)
    type = Column(String)
    date_closure = Column(DATETIME)
    users = Column(TEXT)
    open = Column(BOOLEAN, default=True)

    def __repr__(self):
        return "<Event(id='%s', id_message='%s, date_closure='%s', users='%s')>" % (
            self.id, self.id_message, self.date_closure.strftime("%m/%d/%Y, %H:%M:%S"), self.users)
