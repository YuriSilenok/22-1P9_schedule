from peewee import SqliteDatabase, Model, AutoField, CharField

# Настройка базы данных
DATABASE_URL = "./schedule.db"  # Путь к файлу базы данных
db = SqliteDatabase(DATABASE_URL)

# Определение базовой модели для работы с базой данных
class BaseModel(Model):
    class Meta:
        database = db

# Модель расписания
class Schedule(BaseModel):
    id = AutoField()  # Автоматическое создание уникального идентификатора
    day = CharField()  # Поле для хранения дня недели
    subject = CharField()  # Поле для хранения названия предмета
    timeslot = CharField()  # Поле для хранения временного интервала

# Функция для инициализации базы данных
def initialize_database():
    if db.is_closed():  # Проверяем, если база данных не подключена
        db.connect()
    db.create_tables([Schedule], safe=True)  # safe=True, чтобы избежать ошибок, если таблицы уже существуют
