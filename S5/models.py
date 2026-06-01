from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, DateTimeField
from datetime import datetime

db = SqliteDatabase('faculty_service.db')

class Department(Model):
    name = CharField(max_length=200, unique=True, null=False)
    code = CharField(max_length=20, unique=True, null=False)
    head_name = CharField(max_length=150, null=False)
    head_specialty = CharField(max_length=200, null=True)
    head_phone = CharField(max_length=20, null=True)
    head_email = CharField(max_length=100, null=True)
    head_cabinet_id = IntegerField(null=True)
    reception_is_active = BooleanField(default=False)
    reception_schedule = CharField(max_length=500, null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        database = db
        table_name = 'departments'

def init_db():
    db.connect()
    db.create_tables([Department], safe=True)
    db.close()