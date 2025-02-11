from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
import random
import uvicorn
from database import Schedule, Teacher, Subject, Group, Classroom, initialize_database, User, db
from auth import (
    authenticate_user, 
    create_access_token, 
    get_current_user, 
    hash_password, 
    UserCreate, 
    Token
)

app = FastAPI()

# Инициализация базы данных
initialize_database()

# Объявляем схему для OAuth2 (нужно для передачи токена)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Модели запросов и ответов
class ScheduleCreateRequest(BaseModel):
    days: List[str] = []
    timeslots: List[str] = []
    subjects: List[str] = []

class ScheduleResponse(BaseModel):
    day: str
    timeslot: str
    subject: str

class SubjectCreateRequest(BaseModel):
    name: str
    teacher_id: int

class SubjectResponse(BaseModel):
    id: int
    name: str
    teacher_id: int

    class Config:
        orm_mode = True

class TimeslotCreateRequest(BaseModel):
    timeslot: str

class DayCreateRequest(BaseModel):
    day: str

# --- НОВЫЕ ЭНДПОИНТЫ ДЛЯ АВТОРИЗАЦИИ ---

@app.post("/register/")
def register_user(user: UserCreate):
    """Регистрация нового пользователя"""
    with db:
        if User.get_or_none(User.username == user.username):
            raise HTTPException(status_code=400, detail="Пользователь уже существует")
        hashed_password = hash_password(user.password)
        User.create(username=user.username, hashed_password=hashed_password)
    return {"message": "Пользователь успешно зарегистрирован"}

@app.post("/token/", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Аутентификация пользователя и выдача JWT"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/protected/")
def protected_route(token: str = Depends(oauth2_scheme)):
    """Защищённый маршрут, который требует JWT-токен"""
    user = get_current_user(token)  # Проверяем токен и получаем пользователя
    return {"message": f"Добро пожаловать, {user.username}!", "your_token": token}

# --- ОСТАВЛЕН СТАРЫЙ ФУНКЦИОНАЛ ---

@app.post("/create_subject/", response_model=SubjectResponse)
def create_subject(request: SubjectCreateRequest):
    teacher = Teacher.get_or_none(Teacher.id == request.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден.")
    subject = Subject.create(name=request.name, teacher=teacher)
    return SubjectResponse.from_orm(subject)

@app.post("/create_timeslot/", response_model=TimeslotCreateRequest)
def create_timeslot(request: TimeslotCreateRequest):
    return request

@app.post("/create_day/", response_model=DayCreateRequest)
def create_day(request: DayCreateRequest):
    return request

@app.post("/generate_schedule/", response_model=List[ScheduleResponse])
def generate_schedule(request: ScheduleCreateRequest):
    if not request.days or not request.timeslots or not request.subjects:
        raise HTTPException(status_code=400, detail="Необходимо передать дни, временные интервалы и предметы.")
    
    Schedule.delete().execute()
    schedule = []
    for day in request.days:
        for timeslot in request.timeslots:
            subject = random.choice(request.subjects) if request.subjects else "Не определено"
            db_schedule = Schedule.create(day=day, timeslot=timeslot, subject=subject)
            schedule.append(ScheduleResponse(day=db_schedule.day, timeslot=db_schedule.timeslot, subject=db_schedule.subject))

    return schedule

@app.get("/get_schedule/", response_model=List[ScheduleResponse])
def get_schedule():
    db_schedule = Schedule.select()
    if not db_schedule.exists():
        raise HTTPException(status_code=404, detail="Расписание не найдено.")

    return [ScheduleResponse(day=item.day, timeslot=item.timeslot, subject=item.subject) for item in db_schedule]

if __name__ == "__main__":
    uvicorn.run("schedule_generator:app", host="127.0.0.1", port=8000, reload=True)