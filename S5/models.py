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
    head_email = CharField(max_length=255, null=True)
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
        # Проверка обязательных полей
        if not self.name or len(self.name) < 2:
            raise ValueError("Название отделения должно быть не менее 2 символов")
        if len(self.name) > 200:
            raise ValueError("Название отделения не должно превышать 200 символов")
        
        if not self.code or len(self.code) < 2:
            raise ValueError("Код должен быть не менее 2 символов")
        if len(self.code) > 20:
            raise ValueError("Код не должен превышать 20 символов")
        
        if not self.head_name or len(self.head_name) < 2:
            raise ValueError("ФИО заведующего должно быть не менее 2 символов")
        if len(self.head_name) > 150:
            raise ValueError("ФИО заведующего не должно превышать 150 символов")
        
        # Проверка опциональных полей (если заполнены)
        if self.head_specialty is not None:
            if len(self.head_specialty) < 2:
                raise ValueError("Специальность должна быть не менее 2 символов")
            if len(self.head_specialty) > 200:
                raise ValueError("Специальность не должна превышать 200 символов")
        
        if self.head_phone is not None and self.head_phone != "":
            if len(self.head_phone) > 20:
                raise ValueError("Телефон не должен превышать 20 символов")
            if not re.match(r'^\+7\d{10}$', self.head_phone):
                raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        
        if self.head_email is not None and self.head_email != "":
            if len(self.head_email) > 255:
                raise ValueError("Email не должен превышать 255 символов")
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.head_email):
                raise ValueError("Неверный формат email")
        
        if self.head_cabinet_id is not None:
            if self.head_cabinet_id <= 0:
                raise ValueError("Номер кабинета должен быть положительным числом")
        
        if self.reception_schedule is not None and self.reception_schedule != "":
            if len(self.reception_schedule) > 500:
                raise ValueError("Время приёма не должно превышать 500 символов")
        
        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")