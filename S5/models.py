from peewee import SqliteDatabase, Model, AutoField, CharField, IntegerField, BooleanField, DateTimeField, Check
from datetime import datetime

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    id = AutoField(primary_key=True)
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
    is_active = BooleanField(default=True)

    class Meta:
        database = db
        table_name = 'departments'
        indexes = ((('name', 'code'), True),)

    @classmethod
    def delete_by_id(cls, dept_id):
        if not isinstance(dept_id, int) or dept_id <= 0:
            return False
        query = cls.update(is_active=False).where(cls.id == dept_id)
        rows = query.execute()
        return rows > 0

    @classmethod
    def update_by_id(cls, dept_id, **kwargs):
        if not isinstance(dept_id, int) or dept_id <= 0:
            return None
        dept = cls.get_or_none(cls.id == dept_id)
        if not dept:
            return None
        # Обновляем только переданные поля, исключая неизменяемые
        for key, value in kwargs.items():
            if key not in ['id', 'created_at', 'is_active'] and value is not None:
                setattr(dept, key, value)
        try:
            dept.save()  # валидация сработает в save()
        except ValueError as e:
            raise ValueError(f"Ошибка валидации: {e}")
        return dept

    @classmethod
    def get_active(cls):
        return cls.select().where(cls.is_active == True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'head_name': self.head_name,
            'head_specialty': self.head_specialty,
            'head_phone': self.head_phone,
            'head_email': self.head_email,
            'head_cabinet_id': self.head_cabinet_id,
            'reception_is_active': self.reception_is_active,
            'reception_schedule': self.reception_schedule,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active,
        }

    def save(self, *args, **kwargs):
        # Преобразование пустых строк в None для всех nullable полей
        nullable_fields = ['head_specialty', 'head_phone', 'head_email', 'reception_schedule']
        for field in nullable_fields:
            if getattr(self, field) == "":
                setattr(self, field, None)

        # Проверка максимальной длины (хотя поле имеет max_length, но для явной ошибки)
        if len(self.name) > 200:
            raise ValueError("Название отделения не может превышать 200 символов")
        if len(self.code) > 20:
            raise ValueError("Код не может превышать 20 символов")
        if len(self.head_name) > 150:
            raise ValueError("ФИО заведующего не может превышать 150 символов")
        if self.head_phone and len(self.head_phone) > 20:
            raise ValueError("Телефон не может превышать 20 символов")
        if self.head_email and len(self.head_email) > 255:
            raise ValueError("Email не может превышать 255 символов")
        if self.head_email is not None and len(self.head_email) < 2:
            raise ValueError("Email должен быть не менее 2 символов")
        if self.head_specialty is not None and len(self.head_specialty) < 2:
            raise ValueError("Специальность должна быть не менее 2 символов")
        if self.reception_schedule is not None and len(self.reception_schedule) > 500:
            raise ValueError("Время приёма не должно превышать 500 символов")
        # head_cabinet_id не требует дополнительной проверки (IntegerField)
        super().save(*args, **kwargs)


def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()

if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")