from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField, Check
from datetime import datetime

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    """Модель отделения СПО"""
    name = CharField(max_length=200, null=False, constraints=[Check("length(name) >= 2")])
    code = CharField(max_length=20, null=False, constraints=[
        Check("length(code) >= 2"),
        Check("length(code) <= 20")
    ])
    head_name = CharField(max_length=150, null=False, constraints=[Check("length(head_name) >= 2")])
    head_specialty = CharField(max_length=200, null=True)
    head_phone = CharField(max_length=20, null=True)
    head_email = CharField(max_length=255, null=True)
    head_cabinet_id = IntegerField(null=True)  # любые целые числа, включая 0 и отрицательные
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

    @classmethod
    def delete_by_id(cls, dept_id):
        """Мягкое удаление: возвращает {"deleted": True/False}"""
        rows = cls.update(is_active=False).where(cls.id == dept_id).execute()
        return {"deleted": rows > 0}

    @classmethod
    def update_by_id(cls, dept_id, **kwargs):
        """Обновление сущности по ID, возвращает словарь с обновлёнными данными"""
        forbidden = {'id', 'created_at', 'is_active'}
        update_data = {k: v for k, v in kwargs.items() if v is not None and k not in forbidden}
        if update_data:
            cls.update(**update_data).where(cls.id == dept_id).execute()
        obj = cls.get_or_none(cls.id == dept_id)
        return obj.to_dict() if obj else None

    @classmethod
    def get_active(cls):
        """Только активные записи"""
        return cls.select().where(cls.is_active == True)

    def to_dict(self):
        """Сериализация для API-ответов"""
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
        # Преобразуем пустые строки в None для опциональных полей
        for field in ('head_phone', 'head_email', 'head_specialty', 'reception_schedule'):
            val = getattr(self, field)
            if val == "":
                setattr(self, field, None)

        # Проверка минимальной длины для всех строковых полей (кроме already checked)
        if self.head_specialty is not None and len(self.head_specialty) < 2:
            raise ValueError("Специальность должна быть не менее 2 символов")
        if self.head_phone is not None and len(self.head_phone) < 2:
            raise ValueError("Телефон должен быть не менее 2 символов")
        if self.head_email is not None and len(self.head_email) < 2:
            raise ValueError("Email должен быть не менее 2 символов")
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