from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from datetime import datetime
from .db import Base

class Profile(Base):
    __tablename__ = "profiles"
    id = Column(Integer, primary_key=True)
    name = Column(String, default="Athlete")
    age = Column(Integer, default=25)
    sex = Column(String, default="male")
    height_cm = Column(Float, default=175)
    weight_kg = Column(Float, default=70)
    activity = Column(String, default="moderate")
    goal = Column(String, default="recomp")

class Progress(Base):
    __tablename__ = "progress"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, default=1)
    date = Column(DateTime, default=datetime.utcnow)
    weight_kg = Column(Float)
    waist_cm = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)

class WorkoutLog(Base):
    __tablename__ = "workout_logs"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, default=1)
    workout = Column(String)
    exercise = Column(String)
    weight_kg = Column(Float)
    reps = Column(Integer)
    date = Column(DateTime, default=datetime.utcnow)

class FoodLog(Base):
    __tablename__ = "food_logs"
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, default=1)
    food = Column(String)
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    date = Column(DateTime, default=datetime.utcnow)
