from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, DateTimeField

# Настройка базы данных
DATABASE_URL = "./schedule.db"  # Путь к файлу базы данных
db = SqliteDatabase(DATABASE_URL)

# Определение базовой модели для работы с базой данных
class BaseModel(Model):
    class Meta:
        database = db

# Модель преподавателей
class Teacher(BaseModel):
    name = CharField()  # Имя преподавателя
    department = CharField()  # Отдел

# Модель предметов
class Subject(BaseModel):
    name = CharField()  # Название предмета
    teacher = ForeignKeyField(Teacher, backref='subjects')  # Связь с преподавателем

# Модель групп
class Group(BaseModel):
    group_name = CharField()  # Название группы

# Модель аудиторий
class Classroom(BaseModel):
    room_number = CharField()  # Номер аудитории

# Модель расписания
class Schedule(BaseModel):
    day = CharField()  # Поле для хранения дня недели
    subject = ForeignKeyField(Subject, backref='schedules')  # Связь с предметом
    group = ForeignKeyField(Group, backref='schedules')  # Связь с группой
    classroom = ForeignKeyField(Classroom, backref='schedules')  # Связь с аудиторией
    time = DateTimeField()  # Поле для хранения времени занятия

# Функция для инициализации базы данных
def initialize_database():
    if db.is_closed():  # Проверяем, если база данных не подключена
        db.connect()
    db.create_tables([Teacher, Subject, Group, Classroom, Schedule], safe=True)  # Создаем все таблицы
