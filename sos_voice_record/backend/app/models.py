from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Attachment(Base):
    __tablename__ = 'attachments'

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    filename = Column(String)
    host_path = Column(String)
    static_path = Column(String)
    timestamp = Column(DateTime)
    caller = Column(Integer)
    recorded = Column(Integer)
    call_timestamp = Column(DateTime)
    sos_id = Column(Integer,unique=True, index=True)

class Garbage(Base):
    __tablename__ = 'garbage'

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String, unique=True, index=True)
    filename = Column(String)
    host_path = Column(String)
    static_path = Column(String)
    timestamp = Column(DateTime)
    caller = Column(Integer)
    recorded = Column(Integer)
    call_timestamp = Column(DateTime)

