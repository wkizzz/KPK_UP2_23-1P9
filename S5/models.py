from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField, Check
from datetime import datetime
import re

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    """Модель отделения СПО"""
    name = CharField(max_length=200, null=False, constraints=[Check("length(name) >= 2")])
    code = CharField(max_length=20, null=False, constraints=[Check("length(code) >= 2")])
    head_name = CharField(max_length=150, null=False, constraints=[Check("length(head_name) >= 2")])
    head_specialty = CharField(max_length=200, null=True)
    head_phone = CharField(max_length=20, null=True)
    head_email = CharField(max_length=255, null=True)
    head_cabinet_id = IntegerField(null=True, constraints=[Check("head_cabinet_id > 0")])
    reception_is_active = BooleanField(default=False)
    reception_schedule = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'departments'
        indexes = (
            (('name', 'code'), True),
        )

    def validate_for_create(self):
        """Валидация при создании новой записи"""
        if len(self.name) < 2:
            raise ValueError("Название отделения должно быть не менее 2 символов")
        if len(self.code) < 2:
            raise ValueError("Код должен быть не менее 2 символов")
        if len(self.head_name) < 2:
            raise ValueError("ФИО заведующего должно быть не менее 2 символов")
        if not re.match(r'^\d{2}\.\d{2}\.\d{2}$', self.code):
            raise ValueError("Код должен быть в формате 09.02.07")
        self._validate_optional_fields()

    def validate_for_update(self):
        """Валидация при обновлении - проверяем только те поля, которые не None"""
        if self.name is not None and len(self.name) < 2:
            raise ValueError("Название отделения должно быть не менее 2 символов")
        if self.code is not None and len(self.code) < 2:
            raise ValueError("Код должен быть не менее 2 символов")
        if self.code is not None and not re.match(r'^\d{2}\.\d{2}\.\d{2}$', self.code):
            raise ValueError("Код должен быть в формате 09.02.07")
        if self.head_name is not None and len(self.head_name) < 2:
            raise ValueError("ФИО заведующего должно быть не менее 2 символов")
        self._validate_optional_fields()

    def _validate_optional_fields(self):
        """Валидация опциональных полей"""
        if self.head_specialty is not None and len(self.head_specialty) < 2:
            raise ValueError("Специальность должна быть не менее 2 символов")
        if self.head_phone is not None and not re.match(r'^\+7\d{10}$', self.head_phone):
            raise ValueError("Телефон должен быть в формате +7XXXXXXXXXX")
        if self.head_email is not None and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', self.head_email):
            raise ValueError("Неверный формат email")
        if self.head_cabinet_id is not None and self.head_cabinet_id < 1:
            raise ValueError("Номер кабинета должен быть положительным числом")
        if self.reception_schedule is not None and len(self.reception_schedule) > 500:
            raise ValueError("Время приёма не должно превышать 500 символов")
        # Запрещаем пустые строки
        if self.head_phone == "" or (self.head_phone is not None and self.head_phone.strip() == ""):
            raise ValueError("Телефон не может быть пустой строкой")
        if self.head_email == "" or (self.head_email is not None and self.head_email.strip() == ""):
            raise ValueError("Email не может быть пустой строкой")
        if self.head_specialty == "" or (self.head_specialty is not None and self.head_specialty.strip() == ""):
            raise ValueError("Специальность не может быть пустой строкой")
        if self.reception_schedule == "" or (self.reception_schedule is not None and self.reception_schedule.strip() == ""):
            raise ValueError("Время приёма не может быть пустой строкой")

    def save(self, *args, **kwargs):
        # Определяем, это создание или обновление
        is_new = self.id is None
        
        if is_new:
            self.validate_for_create()
        else:
            self.validate_for_update()
        
        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")