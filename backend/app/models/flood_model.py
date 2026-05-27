from sqlalchemy import Column, Integer, Text
from geoalchemy2 import Geometry

from app.database import Base

class FloodPoint(Base):
    __tablename__ = "flood_points"

    id = Column(Integer, primary_key=True, index=True)
    location_name = Column(Text)
    risk_level = Column(Text)
    geom = Column(Geometry("POINT"))