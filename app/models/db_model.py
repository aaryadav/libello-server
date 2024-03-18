from sqlalchemy import Column, Integer, String, CHAR
from sqlalchemy.ext.declarative import declarative_base
from config.db_config import engine
from sqlalchemy.dialects.postgresql import UUID
import uuid


Base = declarative_base()


class Notebooks(Base):
    __tablename__ = 'notebooks'
    id = Column(CHAR(36), primary_key=True, unique=True, nullable=False)
    name = Column(String(255))
    user_id = Column(CHAR(36))


Base.metadata.create_all(bind=engine)
