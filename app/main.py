from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import Profile, Progress, WorkoutLog, FoodLog
from .calculations import targets
from .workouts import WORKOUTS
from .rag import answer

Base.metadata.create_all(bind=engine)
app=FastAPI(title="Be2Gen2 API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class ProfileIn(BaseModel):
    name:str="Athlete"; age:int=25; sex:str="male"; height_cm:float=175; weight_kg:float=70; activity:str="moderate"; goal:str="recomp"
class ProgressIn(BaseModel):
    weight_kg:float; waist_cm:float|None=None; notes:str|None=None
class WorkoutIn(BaseModel):
    workout:str; exercise:str; weight_kg:float; reps:int
class FoodIn(BaseModel):
    food:str; calories:float; protein:float; carbs:float; fat:float
class ChatIn(BaseModel):
    message:str

@app.get("/api/health")
def health(): return {"status":"ok","app":"Be2Gen2"}

@app.post("/api/profile")
def save_profile(data:ProfileIn, db:Session=Depends(get_db)):
    p=db.query(Profile).first() or Profile()
    for k,v in data.model_dump().items(): setattr(p,k,v)
    db.add(p); db.commit(); db.refresh(p)
    return {"profile":data.model_dump(),"metrics":targets(data.age,data.sex,data.height_cm,data.weight_kg,data.activity,data.goal)}

@app.get("/api/profile")
def get_profile(db:Session=Depends(get_db)):
    p=db.query(Profile).first()
    if not p: return {"profile":ProfileIn().model_dump(),"metrics":targets(25,"male",175,70,"moderate","recomp")}
    return {"profile":{c.name:getattr(p,c.name) for c in p.__table__.columns},"metrics":targets(p.age,p.sex,p.height_cm,p.weight_kg,p.activity,p.goal)}

@app.get("/api/workouts")
def workouts(): return WORKOUTS

@app.post("/api/progress")
def progress(data:ProgressIn, db:Session=Depends(get_db)):
    row=Progress(**data.model_dump()); db.add(row); db.commit(); db.refresh(row); return row

@app.get("/api/progress")
def progress_list(db:Session=Depends(get_db)):
    return [{"date":r.date.isoformat(),"weight_kg":r.weight_kg,"waist_cm":r.waist_cm} for r in db.query(Progress).order_by(Progress.date).all()]

@app.post("/api/workout-log")
def workout_log(data:WorkoutIn, db:Session=Depends(get_db)):
    row=WorkoutLog(**data.model_dump()); db.add(row); db.commit(); return row

@app.get("/api/workout-log")
def workout_logs(db:Session=Depends(get_db)):
    return [{"date":r.date.isoformat(),"workout":r.workout,"exercise":r.exercise,"weight_kg":r.weight_kg,"reps":r.reps} for r in db.query(WorkoutLog).order_by(WorkoutLog.date.desc()).limit(100).all()]

@app.post("/api/food-log")
def food_log(data:FoodIn, db:Session=Depends(get_db)):
    row=FoodLog(**data.model_dump()); db.add(row); db.commit(); return row

@app.get("/api/food-log/today")
def food_today(db:Session=Depends(get_db)):
    rows=db.query(FoodLog).order_by(FoodLog.date.desc()).limit(100).all()
    return [{"food":r.food,"calories":r.calories,"protein":r.protein,"carbs":r.carbs,"fat":r.fat,"date":r.date.isoformat()} for r in rows[:20]]

@app.post("/api/ai/chat")
async def chat(data:ChatIn): return await answer(data.message)
