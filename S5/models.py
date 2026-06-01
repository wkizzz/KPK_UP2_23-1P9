from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField, Check
from datetime import datetime

db = SqliteDatabase('faculty_service.db')

class Department(Model):
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
        indexes = ((('name', 'code'), True),)
        constraints = [
            Check("length(name) >= 2"),
            Check("length(code) >= 2 AND length(code) <= 20"),
            Check("length(head_name) >= 2")
        ]

    @classmethod
    def get_by_id(cls, dept_id):
        try:
            obj = cls.get((cls.id == dept_id) & (cls.is_active == True))
            return obj.to_dict()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_list(cls, page=1, size=10, name=None):
        query = cls.select().where(cls.is_active == True)
        if name:
            query = query.where(cls.name.contains(name))
        query = query.order_by(cls.id)
        offset = (page - 1) * size
        items = list(query.offset(offset).limit(size))
        return [item.to_dict() for item in items]

    @classmethod
    def delete_by_id(cls, dept_id):
        rows = cls.update(is_active=False).where(cls.id == dept_id).execute()
        return rows > 0  # True/False

    @classmethod
    def update_by_id(cls, dept_id, **kwargs):
        forbidden = {'id', 'created_at', 'is_active'}
        update_data = {}
        for k, v in kwargs.items():
            if k in forbidden:
                continue
            if v is not None:
                update_data[k] = v
            else:
                # Явное обнуление: передаём None в базу
                update_data[k] = None

        if update_data:
            try:
                cls.update(**update_data).where(cls.id == dept_id).execute()
            except Exception as e:
                if 'UNIQUE' in str(e):
                    raise ValueError("Нарушение уникальности name+code")
                raise
        obj = cls.get_or_none(cls.id == dept_id)
        return obj.to_dict() if obj and obj.is_active else None

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
        # Преобразование пустых строк в None
        for f in ('head_phone', 'head_email', 'head_specialty', 'reception_schedule'):
            val = getattr(self, f)
            if val == "":
                setattr(self, f, None)

        # Проверки только по требованиям
        if self.head_specialty is not None and len(self.head_specialty) > 200:
            raise ValueError("Специальность не должна превышать 200 символов")
        if self.head_phone is not None and len(self.head_phone) > 20:
            raise ValueError("Телефон не должен превышать 20 символов")
        if self.head_email is not None and len(self.head_email) > 255:
            raise ValueError("Email не должен превышать 255 символов")
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