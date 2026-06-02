from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel, field_validator
from typing import Optional, List
from models import Department, init_db, db


# ===== Pydantic схемы с валидацией =====
class DepartmentCreate(BaseModel):
    name: str
    code: str
    head_name: str
    head_cabinet_id: str
    head_phone: Optional[str] = None
    reception_is_active: bool = False
    reception_start: Optional[int] = None
    reception_end: Optional[int] = None

    @field_validator('name')
    def validate_name(cls, v):
        if not (2 <= len(v) <= 200):
            raise ValueError('2-200 символов')
        return v

    @field_validator('code')
    def validate_code(cls, v):
        if not (2 <= len(v) <= 20):
            raise ValueError('2-20 символов')
        return v

    @field_validator('head_name')
    def validate_head_name(cls, v):
        if not (2 <= len(v) <= 150):
            raise ValueError('2-150 символов')
        return v

    @field_validator('head_cabinet_id')
    def validate_cabinet(cls, v):
        if len(v) != 3 or not v.isdigit():
            raise ValueError('ровно 3 цифры')
        return v

    @field_validator('head_phone')
    def validate_phone(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 20):
            raise ValueError('2-20 символов')
        return v

    @field_validator('reception_start')
    def validate_start(cls, v):
        if v is not None and not (0 <= v <= 23):
            raise ValueError('0-23')
        return v

    @field_validator('reception_end')
    def validate_end(cls, v, info):
        if v is not None and not (0 <= v <= 23):
            raise ValueError('0-23')
        # Проверка ≥ start выполняется в модели, но дублируем для ранней ошибки
        start = info.data.get('reception_start')
        if start is not None and v is not None and v < start:
            raise ValueError('reception_end не может быть меньше reception_start')
        return v


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    head_name: Optional[str] = None
    head_cabinet_id: Optional[str] = None
    head_phone: Optional[str] = None
    reception_is_active: Optional[bool] = None
    reception_start: Optional[int] = None
    reception_end: Optional[int] = None

    @field_validator('name')
    def validate_name(cls, v):
        if v is not None and not (2 <= len(v) <= 200):
            raise ValueError('2-200 символов')
        return v

    @field_validator('code')
    def validate_code(cls, v):
        if v is not None and not (2 <= len(v) <= 20):
            raise ValueError('2-20 символов')
        return v

    @field_validator('head_name')
    def validate_head_name(cls, v):
        if v is not None and not (2 <= len(v) <= 150):
            raise ValueError('2-150 символов')
        return v

    @field_validator('head_cabinet_id')
    def validate_cabinet(cls, v):
        if v is not None and (len(v) != 3 or not v.isdigit()):
            raise ValueError('ровно 3 цифры')
        return v

    @field_validator('head_phone')
    def validate_phone(cls, v):
        if v is not None and (len(v) < 2 or len(v) > 20):
            raise ValueError('2-20 символов')
        return v

    @field_validator('reception_start')
    def validate_start(cls, v):
        if v is not None and not (0 <= v <= 23):
            raise ValueError('0-23')
        return v

    @field_validator('reception_end')
    def validate_end(cls, v, info):
        if v is not None and not (0 <= v <= 23):
            raise ValueError('0-23')
        start = info.data.get('reception_start')
        if start is not None and v is not None and v < start:
            raise ValueError('reception_end ≥ reception_start')
        return v


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str
    head_name: str
    head_cabinet_id: str
    head_phone: Optional[str] = None
    reception_is_active: bool
    reception_start: Optional[int] = None
    reception_end: Optional[int] = None
    created_at: str
    is_active: bool


# ===== Lifespan (инициализация БД) =====
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Запуск Faculty Service API...")
    init_db()
    print("База данных готова")
    yield
    print("Остановка...")
    if not db.is_closed():
        db.close()

app = FastAPI(
    title="Faculty Service API",
    description="Справочник отделений СПО",
    version="1.0",
    lifespan=lifespan
)


# ===== Эндпоинты =====
@app.post("/departments", response_model=DepartmentOut, status_code=201)
def create_department(data: DepartmentCreate):
    db.connect()
    try:
        new = Department.create(**data.model_dump())
        db.close()
        return new.to_dict()
    except Exception as e:
        db.close()
        if "UNIQUE" in str(e) or "Отделение с таким name и code уже существует" in str(e):
            raise HTTPException(409, "Отделение с таким name и code уже существует")
        raise HTTPException(400, str(e))


@app.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int = Path(..., ge=1)):
    db.connect()
    result = Department.get_by_id(dept_id)
    db.close()
    if result is False:
        raise HTTPException(404, "Отделение не найдено")
    return result


@app.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = Query(None)
):
    db.connect()
    items = Department.get_list(page=page, size=size, name=name)
    db.close()
    return items


@app.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int = Path(..., ge=1),
    data: DepartmentUpdate = None
):
    db.connect()
    # Передаём только те поля, которые были явно указаны (включая None)
    update_kwargs = data.model_dump(exclude_unset=False)  # все поля, даже None
    result = Department.update_by_id(dept_id, **update_kwargs)
    db.close()
    if result is False:
        raise HTTPException(404, "Отделение не найдено")
    return result


@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int = Path(..., ge=1)):
    db.connect()
    ok = Department.delete_by_id(dept_id)
    db.close()
    if not ok:
        raise HTTPException(404, "Отделение не найдено")
    return {"deleted": True}


@app.get("/")
def root():
    return {"service": "Faculty Service API", "version": "1.0"}