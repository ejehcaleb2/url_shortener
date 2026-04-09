from app import database
from sqlalchemy import Column, Integer, String
from app.database import Base

class URL(database.Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, unique=True, index=True)
    short_code = Column(String, unique=True, index=True) 