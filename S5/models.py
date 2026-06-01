from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime

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
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'departments'
        indexes = (
            (('name', 'code'), True),
        )

    def save(self, *args, **kwargs):
        # Преобразуем пустые строки в None для опциональных полей
        if self.head_phone == "":
            self.head_phone = None
        if self.head_email == "":
            self.head_email = None
        if self.head_specialty == "":
            self.head_specialty = None
        if self.reception_schedule == "":
            self.reception_schedule = None

        # Валидация минимальной длины
        if len(self.name) < 2 or len(self.name) > 200:
            raise ValueError("name должен быть 2-200 символов")
        if len(self.code) < 2 or len(self.code) > 20:
            raise ValueError("code должен быть 2-20 символов")
        if len(self.head_name) < 2 or len(self.head_name) > 150:
            raise ValueError("head_name должен быть 2-150 символов")
        if self.head_specialty is not None and (len(self.head_specialty) < 2 or len(self.head_specialty) > 200):
            raise ValueError("head_specialty должен быть 2-200 символов")
        if self.head_phone is not None and (len(self.head_phone) < 2 or len(self.head_phone) > 20):
            raise ValueError("head_phone должен быть 2-20 символов")
        if self.head_email is not None and len(self.head_email) > 255:
            raise ValueError("head_email не более 255 символов")
        if self.reception_schedule is not None and (len(self.reception_schedule) < 2 or len(self.reception_schedule) > 500):
            raise ValueError("reception_schedule должен быть 2-500 символов")

        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")