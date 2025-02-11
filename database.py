from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, DateTimeField

# Настройка базы данных
DATABASE_URL = "./schedule.db"
db = SqliteDatabase(DATABASE_URL)

class BaseModel(Model):
    class Meta:
        database = db

# Модель пользователей
class User(BaseModel):
    username = CharField(unique=True)
    hashed_password = CharField()

# Модель преподавателей
class Teacher(BaseModel):
    name = CharField()
    department = CharField()

# Модель предметов
class Subject(BaseModel):
    name = CharField()
    teacher = ForeignKeyField(Teacher, backref='subjects')

# Модель групп
class Group(BaseModel):
    group_name = CharField()

# Модель аудиторий
class Classroom(BaseModel):
    room_number = CharField()

# Модель расписания
class Schedule(BaseModel):
    day = CharField()
    subject = ForeignKeyField(Subject, backref='schedules')
    group = ForeignKeyField(Group, backref='schedules')
    classroom = ForeignKeyField(Classroom, backref='schedules')
    time = DateTimeField()

# Функция инициализации базы данных
def initialize_database():
    if db.is_closed():
        db.connect()
    db.create_tables([User, Teacher, Subject, Group, Classroom, Schedule], safe=True)
