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

    @classmethod
    def get_by_id(cls, dept_id):
        """Возвращает словарь с данными отделения или None"""
        try:
            obj = cls.get((cls.id == dept_id) & (cls.is_active == True))
            return obj.to_dict()
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_list(cls, page=1, size=10, name=None):
        """Возвращает список словарей с пагинацией и фильтром по name"""
        # Валидация параметров пагинации
        if page < 1:
            page = 1
        if size < 1:
            size = 1
        if size > 100:
            size = 100

        query = cls.select().where(cls.is_active == True)
        if name:
            query = query.where(cls.name.contains(name))
        query = query.order_by(cls.id)
        offset = (page - 1) * size
        items = list(query.offset(offset).limit(size))
        return [item.to_dict() for item in items]

    @classmethod
    def delete_by_id(cls, dept_id):
        """Мягкое удаление, возвращает True/False"""
        rows = cls.update(is_active=False).where(cls.id == dept_id).execute()
        return rows > 0

    @classmethod
    def update_by_id(cls, dept_id, **kwargs):
        """Обновление сущности с полной валидацией через save()"""
        obj = cls.get_or_none(cls.id == dept_id)
        if not obj or not obj.is_active:
            return None

        for key, value in kwargs.items():
            if value is not None and key not in ('id', 'created_at', 'is_active'):
                if hasattr(obj, key):
                    setattr(obj, key, value)

        obj.save()
        return obj.to_dict()

    def save(self, *args, **kwargs):
        # Преобразование пустых строк в None для опциональных полей
        if self.head_phone == "":
            self.head_phone = None
        if self.head_email == "":
            self.head_email = None
        if self.head_specialty == "":
            self.head_specialty = None
        if self.reception_schedule == "":
            self.reception_schedule = None

        # Проверка типа и пустоты для обязательных полей
        if not isinstance(self.name, str) or not self.name or self.name.strip() == "":
            raise ValueError("name должен быть непустой строкой")
        if not isinstance(self.code, str) or not self.code or self.code.strip() == "":
            raise ValueError("code должен быть непустой строкой")
        if not isinstance(self.head_name, str) or not self.head_name or self.head_name.strip() == "":
            raise ValueError("head_name должен быть непустой строкой")

        # Валидация длины
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
        if self.head_email is not None:
            if len(self.head_email) > 255:
                raise ValueError("head_email не более 255 символов")
            # Простая проверка формата email
            if "@" not in self.head_email or "." not in self.head_email.split("@")[-1]:
                raise ValueError("head_email должен быть корректным email-адресом")
        if self.reception_schedule is not None and (len(self.reception_schedule) < 2 or len(self.reception_schedule) > 500):
            raise ValueError("reception_schedule должен быть 2-500 символов")

        # Проверка head_cabinet_id – должно быть целое число или None
        if self.head_cabinet_id is not None and not isinstance(self.head_cabinet_id, int):
            raise ValueError("head_cabinet_id должен быть целым числом")

        # Проверка уникальности комбинации (name, code) для всех записей (включая неактивные)
        conflict = Department.select().where(
            (Department.name == self.name) &
            (Department.code == self.code)
        )
        if self.id:
            conflict = conflict.where(Department.id != self.id)
        if conflict.exists():
            raise ValueError("Отделение с таким name и code уже существует (включая удалённые)")

        super().save(*args, **kwargs)

    def to_dict(self):
        """Сериализация в словарь, created_at возвращает ISO строку или None"""
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


def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()


if __name__ == "__main__":
    init_db()
    print("База данных инициализирована")