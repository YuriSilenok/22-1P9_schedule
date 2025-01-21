from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
import uvicorn
from database import Schedule, Teacher, Subject, Group, Classroom, initialize_database

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Инициализация базы данных
initialize_database()

# Модели запросов и ответов
class ScheduleCreateRequest(BaseModel):
    days: List[str] = []  # Список дней недели
    timeslots: List[str] = []  # Список временных интервалов
    subjects: List[str] = []  # Список предметов

class ScheduleResponse(BaseModel):
    day: str
    timeslot: str
    subject: str

class SubjectCreateRequest(BaseModel):
    name: str
    teacher_id: int  # ID преподавателя

class TimeslotCreateRequest(BaseModel):
    timeslot: str

class DayCreateRequest(BaseModel):
    day: str

# Маршруты API

# Эндпоинт для создания предмета
@app.post("/create_subject/", response_model=Subject)
def create_subject(request: SubjectCreateRequest):
    """Создание нового предмета."""
    teacher = Teacher.get_or_none(Teacher.id == request.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден.")
    subject = Subject.create(name=request.name, teacher=teacher)
    return subject

# Эндпоинт для добавления временного интервала
@app.post("/create_timeslot/", response_model=TimeslotCreateRequest)
def create_timeslot(request: TimeslotCreateRequest):
    """Добавление нового временного интервала."""
    # Важно: здесь можно добавить валидацию на дублирование времени
    return request

# Эндпоинт для добавления дня недели
@app.post("/create_day/", response_model=DayCreateRequest)
def create_day(request: DayCreateRequest):
    """Добавление дня недели."""
    return request

# Эндпоинт для генерации расписания
@app.post("/generate_schedule/", response_model=List[ScheduleResponse])
def generate_schedule(request: ScheduleCreateRequest):
    """Генерация расписания с пользовательскими предметами и временем."""
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

# Эндпоинт для получения расписания
@app.get("/get_schedule/", response_model=List[ScheduleResponse])
def get_schedule():
    """Получение расписания из базы данных."""
    db_schedule = Schedule.select()
    if not db_schedule.exists():
        raise HTTPException(status_code=404, detail="Расписание не найдено.")

    return [ScheduleResponse(day=item.day, timeslot=item.timeslot, subject=item.subject) for item in db_schedule]

# Точка входа
if __name__ == "__main__":
    uvicorn.run("schedule_generator:app", host="127.0.0.1", port=8000, reload=True)
