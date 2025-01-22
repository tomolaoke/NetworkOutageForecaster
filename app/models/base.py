import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime, Integer

Base = declarative_base()


class TimestampedModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created_at = Column('created_at', DateTime, default=datetime.datetime.now)
    updated_at = Column('updated_at', DateTime, onupdate=datetime.datetime.now)

    class Meta:
        abstract = True
