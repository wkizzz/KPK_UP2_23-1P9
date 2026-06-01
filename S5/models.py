from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField, Check
from datetime import datetime

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    """Модель отделения СПО"""
    name = CharField(max_length=200, null=False, constraints=[Check("length(name) >= 2")])
    code = CharField(max_length=20, null=False, constraints=[Check("length(code) >= 2")])
    head_name = CharField(max_length=150, null=False, constraints=[Check("length(head_name) >= 2")])
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
        # Только проверка на NULL для обязательных полей
        if self.name is None or len(self.name) < 2:
            raise ValueError("Название отделения должно быть не менее 2 символов")
        if self.code is None or len(self.code) < 2:
            raise ValueError("Код должен быть не менее 2 символов")
        if self.head_name is None or len(self.head_name) < 2:
            raise ValueError("ФИО заведующего должно быть не менее 2 символов")
        
        # Опциональные поля - только если не None
        if self.head_specialty is not None and len(self.head_specialty) < 2:
            raise ValueError("Специальность должна быть не менее 2 символов")
        if self.reception_schedule is not None and len(self.reception_schedule) > 500:
            raise ValueError("Время приёма не должно превышать 500 символов")
        
        super().save(*args, **kwargs)

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")