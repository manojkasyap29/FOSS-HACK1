# SQLAlchemy Models for PostgreSQL
from sqlalchemy import Column, Integer, String, Float

# You would normally import Base from database.py here
# from database import Base

# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True, index=True)
#     dietary_preference = Column(String)

# class IngredientData(Base):
#     __tablename__ = "ingredients"
#     id = Column(Integer, primary_key=True)
#     name = Column(String, index=True)
#     health_score = Column(Float)
#     flags = Column(String)  # e.g., "vegan, keto-friendly"