from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from typing import Optional, List
from peewee import IntegrityError
from models import Department, init_db, db

app = FastAPI(title="Faculty Service")

# Схемы ответов
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


@app.on_event("startup")
def startup():
    """Открываем соединение с БД при старте"""
    init_db()


@app.on_event("shutdown")
def shutdown():
    """Закрываем соединение с БД при остановке"""
    if not db.is_closed():
        db.close()


@app.post("/departments", response_model=DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(dept: DepartmentCreate):
    """Создание нового отделения"""
    try:
        new_dept = Department.create(**dept.dict())
        return new_dept.to_dict()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отделение с таким названием и кодом уже существует"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int):
    """Получение отделения по ID"""
    try:
        dept = Department.get_or_none(
            (Department.id == dept_id) & (Department.is_active == True)
        )
        if not dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отделение не найдено"
            )
        return dept.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    page: int = Query(1, ge=1, description="Номер страницы"),
    size: int = Query(10, ge=1, le=100, description="Количество записей на странице"),
    name: Optional[str] = Query(None, description="Поиск по названию")
):
    """Получение списка отделений с пагинацией и фильтрацией"""
    try:
        query = Department.get_active()
        if name:
            query = query.where(Department.name.contains(name))
        query = query.order_by(Department.id)
        offset = (page - 1) * size
        items = list(query.offset(offset).limit(size))
        return [item.to_dict() for item in items]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(dept_id: int, dept: DepartmentUpdate):
    """Обновление отделения по ID"""
    try:
        # Проверяем существование активной записи
        existing = Department.get_or_none(
            (Department.id == dept_id) & (Department.is_active == True)
        )
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отделение не найдено"
            )
        
        # Обновляем
        updated_dict = Department.update_by_id(dept_id, **dept.dict(exclude_unset=True))
        if not updated_dict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отделение не найдено"
            )
        return updated_dict
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Отделение с таким названием и кодом уже существует"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int):
    """Мягкое удаление отделения по ID"""
    try:
        result = Department.delete_by_id(dept_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@app.get("/")
def root():
    return {
        "service": "Faculty Service",
        "version": "1.0",
        "endpoints": {
            "POST /departments": "Создать отделение",
            "GET /departments": "Список отделений",
            "GET /departments/{id}": "Получить по ID",
            "PUT /departments/{id}": "Обновить",
            "DELETE /departments/{id}": "Удалить"
        }
    }