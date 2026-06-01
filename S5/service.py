from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from models import Department, init_db, db

app = FastAPI(title="Faculty Service")

# ----- Схемы с валидацией -----
class DepartmentCreate(BaseModel):
    name: str
    code: str
    head_name: str
    head_specialty: Optional[str] = None
    head_phone: Optional[str] = None
    head_email: Optional[str] = None
    head_cabinet_id: Optional[int] = None
    reception_is_active: bool = False
    reception_schedule: Optional[str] = None

    @field_validator('name')
    def name_len(cls, v):
        if not (2 <= len(v) <= 200):
            raise ValueError('Длина name 2-200')
        return v

    @field_validator('code')
    def code_len(cls, v):
        if not (2 <= len(v) <= 20):
            raise ValueError('Длина code 2-20')
        return v

    @field_validator('head_name')
    def head_name_len(cls, v):
        if not (2 <= len(v) <= 150):
            raise ValueError('Длина head_name 2-150')
        return v

    @field_validator('head_specialty')
    def head_specialty_len(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 200):
            raise ValueError('head_specialty 2-200')
        return v

    @field_validator('head_phone')
    def head_phone_len(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError('head_phone не более 20 символов')
        return v

    @field_validator('head_email')
    def head_email_len(cls, v):
        if v is not None and len(v) > 255:
            raise ValueError('head_email не более 255 символов')
        return v

    @field_validator('reception_schedule')
    def reception_schedule_len(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('reception_schedule не более 500 символов')
        return v

class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    head_name: Optional[str] = None
    head_specialty: Optional[str] = None
    head_phone: Optional[str] = None
    head_email: Optional[str] = None
    head_cabinet_id: Optional[int] = None
    reception_is_active: Optional[bool] = None
    reception_schedule: Optional[str] = None

    @field_validator('name')
    def name_len(cls, v):
        if v is not None and not (2 <= len(v) <= 200):
            raise ValueError('Длина name 2-200')
        return v

    @field_validator('code')
    def code_len(cls, v):
        if v is not None and not (2 <= len(v) <= 20):
            raise ValueError('Длина code 2-20')
        return v

    @field_validator('head_name')
    def head_name_len(cls, v):
        if v is not None and not (2 <= len(v) <= 150):
            raise ValueError('Длина head_name 2-150')
        return v

    @field_validator('head_specialty')
    def head_specialty_len(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 200):
            raise ValueError('head_specialty 2-200')
        return v

    @field_validator('head_phone')
    def head_phone_len(cls, v):
        if v is not None and len(v) > 20:
            raise ValueError('head_phone не более 20 символов')
        return v

    @field_validator('head_email')
    def head_email_len(cls, v):
        if v is not None and len(v) > 255:
            raise ValueError('head_email не более 255 символов')
        return v

    @field_validator('reception_schedule')
    def reception_schedule_len(cls, v):
        if v is not None and len(v) > 500:
            raise ValueError('reception_schedule не более 500 символов')
        return v

class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    head_name: str
    head_specialty: Optional[str] = None
    head_phone: Optional[str] = None
    head_email: Optional[str] = None
    head_cabinet_id: Optional[int] = None
    reception_is_active: bool
    reception_schedule: Optional[str] = None
    created_at: str
    is_active: bool

# ----- API -----
@app.on_event("startup")
def startup():
    init_db()

@app.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(dept: DepartmentCreate):
    db.connect()
    try:
        new_dept = Department.create(**dept.dict())
        db.close()
        return new_dept.to_dict()
    except Exception as e:
        db.close()
        raise HTTPException(400, str(e))

@app.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int):
    db.connect()
    data = Department.get_by_id(dept_id)
    db.close()
    if not data:
        raise HTTPException(404, "Отделение не найдено")
    return data

@app.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None
):
    db.connect()
    items = Department.get_list(page=page, size=size, name=name)
    db.close()
    return items

@app.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(dept_id: int, dept: DepartmentUpdate):
    db.connect()
    try:
        updated_dict = Department.update_by_id(dept_id, **dept.dict(exclude_unset=False))
    except ValueError as e:
        db.close()
        raise HTTPException(400, str(e))
    db.close()
    if not updated_dict:
        raise HTTPException(404, "Отделение не найдено")
    return updated_dict

@app.delete("/departments/{dept_id}", response_model=bool)
def delete_department(dept_id: int):
    db.connect()
    result = Department.delete_by_id(dept_id)
    db.close()
    return result

@app.get("/")
def root():
    return {"service": "Faculty Service", "version": "1.0"}