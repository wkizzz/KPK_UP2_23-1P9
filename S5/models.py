from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime
import re

db = SqliteDatabase('faculty_service.db')

class Department(Model):
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
            (('name', 'code'), True),
        )

    def save(self, *args, **kwargs):
        if len(self.name) < 2:
            raise ValueError("Название отделения должно быть не менее 2 символов")
        if len(self.code) < 2:
            raise ValueError("Код должен быть не менее 2 символов")
        if len(self.head_name) < 2:
            raise ValueError("ФИО заведующего должно быть не менее 2 символов")
        if self.head_specialty and len(self.head_specialty) < 2:
            raise ValueError("Специальность должна быть не менее 2 символов")
        if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', self.code):
            raise ValueError("Код должен быть в формате 09.02.07")
        if self.head_phone and not re.match(r'^\+7\d{10}$', self.head_phone):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        if self.head_email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.head_email):
            raise ValueError("Неверный формат email")
        if self.head_cabinet_id is not None and self.head_cabinet_id <= 0:
            raise ValueError("Номер кабинета должен быть положительным числом")
        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")