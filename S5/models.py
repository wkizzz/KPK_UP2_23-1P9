from peewee import Model, SqliteDatabase, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime
import re

# Инициализация базы данных
db = SqliteDatabase('departments.db')


class Department(Model):
    """Модель отделения/направления подготовки"""
    
    name = CharField(max_length=200, null=False)
    code = CharField(max_length=20, null=False)
    head_name = CharField(max_length=150, null=False)
    head_specialty = CharField(max_length=200, null=True)
    head_phone = CharField(max_length=20, null=True)
    head_email = CharField(max_length=255, null=True)
    head_cabinet_id = IntegerField(null=True)
    reception_is_active = BooleanField(default=False, null=False)
    reception_schedule = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now, null=False)
    is_active = BooleanField(default=True, null=False)  # Для мягкого удаления
    
    class Meta:
        database = db
        # Уникальная комбинация (name, code)
        indexes = (
            (('name', 'code'), True),
        )
    
    def save(self, *args, **kwargs):
        """Валидация перед сохранением"""
        self._validate()
        return super().save(*args, **kwargs)
    
    def _validate(self):
        """Проверка всех ограничений"""
        
        # 1. name
        if self.name and (len(self.name) < 2 or len(self.name) > 200):
            raise ValueError("name: длина должна быть от 2 до 200 символов")
        
        # 2. code (формат 00.00.00 или 00.00.00.00)
        if self.code:
            if len(self.code) < 2 or len(self.code) > 20:
                raise ValueError("code: длина должна быть от 2 до 20 символов")
            if not re.match(r'^\d{2}\.\d{2}\.\d{2}(\.\d{2})?$', self.code):
                raise ValueError("code: неверный формат. Пример: 09.02.07 или 09.02.07.01")
        
        # 3. head_name
        if self.head_name and (len(self.head_name) < 2 or len(self.head_name) > 150):
            raise ValueError("head_name: длина должна быть от 2 до 150 символов")
        
        # 4. head_specialty
        if self.head_specialty and (len(self.head_specialty) < 2 or len(self.head_specialty) > 200):
            raise ValueError("head_specialty: длина должна быть от 2 до 200 символов")
        
        # 5. head_phone (формат +7XXXXXXXXXX)
        if self.head_phone:
            if len(self.head_phone) > 20:
                raise ValueError("head_phone: длина не более 20 символов")
            if not re.match(r'^\+7\d{10}$', self.head_phone):
                raise ValueError("head_phone: неверный формат. Пример: +79161234567")
        
        # 6. head_email
        if self.head_email:
            if len(self.head_email) > 255:
                raise ValueError("head_email: длина не более 255 символов")
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, self.head_email):
                raise ValueError("head_email: неверный формат email")
        
        # 7. head_cabinet_id (положительное число)
        if self.head_cabinet_id is not None and self.head_cabinet_id <= 0:
            raise ValueError("head_cabinet_id: должно быть положительным числом")
        
        # 8. reception_schedule
        if self.reception_schedule and len(self.reception_schedule) > 500:
            raise ValueError("reception_schedule: длина не более 500 символов")
    
    def soft_delete(self):
        """Мягкое удаление"""
        self.is_active = False
        self.save()
    
    @classmethod
    def get_active(cls, *args, **kwargs):
        """Получить только активные записи"""
        return cls.select().where(cls.is_active == True, *args, **kwargs)


def init_db():
    """Инициализация базы данных"""
    db.connect()
    db.create_tables([Department], safe=True)
    return db


# Точка входа для инициализации БД
if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")