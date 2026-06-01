from peewee import Model, SqliteDatabase, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime
import re

db = SqliteDatabase('departments.db')


class Department(Model):
    
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
    is_active = BooleanField(default=True, null=False)
    
    class Meta:
        database = db
        indexes = ((('name', 'code'), True),)
    
    def save(self, *args, **kwargs):
        self._validate()
        return super().save(*args, **kwargs)
    
    def _validate(self):
        # 1. name
        if len(self.name.strip()) == 0:
            raise ValueError("name: не может быть пустым")
        if len(self.name) < 2 or len(self.name) > 200:
            raise ValueError("name: длина должна быть от 2 до 200 символов")
        
        # 2. code - строгая проверка формата (00.00.00 или 00.00.00.00)
        if len(self.code.strip()) == 0:
            raise ValueError("code: не может быть пустым")
        if not re.fullmatch(r'\d{2}\.\d{2}\.\d{2}(\.\d{2})?', self.code.strip()):
            raise ValueError("code: неверный формат. Допустимые форматы: 00.00.00 или 00.00.00.00")
        
        # 3. head_name
        if len(self.head_name.strip()) == 0:
            raise ValueError("head_name: не может быть пустым")
        if len(self.head_name) < 2 or len(self.head_name) > 150:
            raise ValueError("head_name: длина должна быть от 2 до 150 символов")
        
        # 4. head_specialty
        if self.head_specialty is not None:
            if len(self.head_specialty.strip()) == 0:
                raise ValueError("head_specialty: пустая строка не допускается, используйте null")
            if len(self.head_specialty) < 2 or len(self.head_specialty) > 200:
                raise ValueError("head_specialty: длина должна быть от 2 до 200 символов")
        
        # 5. head_phone - строгий формат +7XXXXXXXXXX
        if self.head_phone is not None:
            if len(self.head_phone.strip()) == 0:
                raise ValueError("head_phone: пустая строка не допускается, используйте null")
            if not re.fullmatch(r'\+7\d{10}', self.head_phone.strip()):
                raise ValueError("head_phone: неверный формат. Требуется +7 и 10 цифр. Пример: +79161234567")
        
        # 6. head_email
        if self.head_email is not None:
            if len(self.head_email.strip()) == 0:
                raise ValueError("head_email: пустая строка не допускается, используйте null")
            if len(self.head_email) > 255:
                raise ValueError("head_email: длина не более 255 символов")
            email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_pattern, self.head_email.strip()):
                raise ValueError("head_email: неверный формат email")
        
        # 7. head_cabinet_id - строго положительное число
        if self.head_cabinet_id is not None:
            if self.head_cabinet_id <= 0:
                raise ValueError("head_cabinet_id: должно быть положительным числом (больше 0)")
        
        # 8. reception_schedule
        if self.reception_schedule is not None:
            if len(self.reception_schedule.strip()) == 0:
                raise ValueError("reception_schedule: пустая строка не допускается, используйте null")
            if len(self.reception_schedule) > 500:
                raise ValueError("reception_schedule: длина не более 500 символов")
    
    @classmethod
    def delete_by_id(cls, department_id):
        try:
            department = cls.get_by_id(department_id)
            if not department.is_active:
                return False
            department.is_active = False
            department.save()
            return True
        except cls.DoesNotExist:
            return False
    
    @classmethod
    def update_by_id(cls, department_id, **kwargs):
        try:
            department = cls.get_by_id(department_id)
            if not department.is_active:
                return None
            for key, value in kwargs.items():
                if hasattr(department, key) and key not in ['id', 'created_at', 'is_active']:
                    setattr(department, key, value)
            department.save()
            return department
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_list(cls, page=1, size=10, name=None, code=None, sort_by='created_at', sort_order='asc'):
        query = cls.select().where(cls.is_active == True)
        if name:
            query = query.where(cls.name.contains(name))
        if code:
            query = query.where(cls.code == code)
        if sort_order == 'desc':
            query = query.order_by(getattr(cls, sort_by).desc())
        else:
            query = query.order_by(getattr(cls, sort_by).asc())
        total = query.count()
        query = query.paginate(page, size)
        items = [item.to_dict() for item in query]
        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size if total > 0 else 0
        }
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "head_name": self.head_name,
            "head_specialty": self.head_specialty,
            "head_phone": self.head_phone,
            "head_email": self.head_email,
            "head_cabinet_id": self.head_cabinet_id,
            "reception_is_active": self.reception_is_active,
            "reception_schedule": self.reception_schedule,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @classmethod
    def get_active(cls, *args, **kwargs):
        return cls.select().where(cls.is_active == True, *args, **kwargs)


def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    return db


if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")