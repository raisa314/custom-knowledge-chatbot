from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Cbkbindex(Base):
    __tablename__ = 'cb_kb_index'

    category = Column(String(255), primary_key=True)
    pdf_link = Column(String(255), nullable=False)
    upload_time = Column(DateTime, nullable=False)
