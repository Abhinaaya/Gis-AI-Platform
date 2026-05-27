from app.database import engine
from app.models.flood_model import Base

Base.metadata.create_all(bind=engine)

print("Tables created")