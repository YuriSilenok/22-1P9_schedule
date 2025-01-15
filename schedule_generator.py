from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
import uvicorn
from database import Schedule, initialize_database

# Создаем экземпляр приложения FastAPI
app = FastAPI()

# Инициализация базы данных
initialize_database()

# Список предметов
SUBJECTS = [
    "Основы философии", "Правовое обеспечение профессиональной деятельности", "Физическая культура",
    "Теория вероятностей и математическая статистика", "БЖ", "Основы медицинских знаний", "Экономика",
    "Основы БД", "Психология", "ПМ 01", "МДК 01.01", "МДК 01.02", "МДК 01.04", "ПМ 02",
    "МДК 02.03", "МДК 02.01", "ПМ 04", "МДК 04.01", "МДК 04.02", "ПМ 11", "МДК 11.01",
    "УП 02.03", "УП 02.01", "УП 01.01", "УП 11.01", "УП 04", "УП 01.04"
]

# Модели запросов и ответов
class ScheduleCreateRequest(BaseModel):
    days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    timeslots: List[str] = ["08:00-09:30", "09:40-11:10", "11:20-12:50", "13:30-15:00", "15:10-16:40"]

class ScheduleResponse(BaseModel):
    day: str
    timeslot: str
    subject: str

# Маршруты API
@app.post("/generate_schedule/", response_model=List[ScheduleResponse])
def generate_schedule(request: ScheduleCreateRequest):
    """Генерация случайного расписания и сохранение его в базе данных."""
    Schedule.delete().execute()

    schedule = []
    for day in request.days:
        for timeslot in request.timeslots:
            subject = random.choice(SUBJECTS)
            db_schedule = Schedule.create(day=day, timeslot=timeslot, subject=subject)
            schedule.append(ScheduleResponse(day=db_schedule.day, timeslot=db_schedule.timeslot, subject=db_schedule.subject))

    return schedule

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

