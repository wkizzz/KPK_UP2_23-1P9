from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime
import re

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    """Модель отделения СПО"""
    name = CharField(max_length=200, null=False)
    code = CharField(max_length=20, null=False)
    head_name = CharField(max_length=150, null=False)
    head_specialty = CharField(max_length=200, null=True)
    head_phone = CharField(max_length=20, null=True)
    head_email = CharField(max_length=100, null=True)
    head_cabinet_id = IntegerField(null=True)
    reception_is_active = BooleanField(default=False)
    reception_schedule = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'departments'
        indexes = (
            (('name', 'code'), True),  # составной уникальный индекс
        )

def init_db():
    """Инициализация БД"""
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()


# ==================== Валидаторы ====================

def validate_phone(phone):
    """Проверка телефона: +7XXXXXXXXXX"""
    if phone is None:
        return True
    return bool(re.match(r'^\+7\d{10}$', phone))

def validate_email(email):
    """Проверка email"""
    if email is None:
        return True
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))

def validate_code(code):
    """Проверка кода: цифры и точки (пример: 09.02.07)"""
    return bool(re.match(r'^\d{2}\.\d{2}\.\d{2}$', code))

def validate_cabinet_id(cabinet_id):
    """Проверка кабинета: положительное число"""
    if cabinet_id is None:
        return True
    return cabinet_id > 0