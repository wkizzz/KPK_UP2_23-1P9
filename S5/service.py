from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from models import Department, init_db, db

app = FastAPI(title="Faculty Service")

# Pydantic схемы
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
    created_at: datetime
    is_active: bool

@app.on_event("startup")
def startup():
    init_db()

@app.post("/departments", response_model=DepartmentOut)
def create_department(dept: DepartmentCreate):
    db.connect()
    try:
        new_dept = Department.create(**dept.dict())
        db.close()
        return new_dept
    except Exception as e:
        db.close()
        raise HTTPException(400, str(e))

@app.get("/departments/{dept_id}", response_model=DepartmentOut)
def get_department(dept_id: int):
    db.connect()
    dept = Department.get_or_none(Department.id == dept_id)
    db.close()
    if not dept or not dept.is_active:
        raise HTTPException(404, "Отделение не найдено")
    return dept

@app.get("/departments", response_model=List[DepartmentOut])
def list_departments(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    name: Optional[str] = None
):
    db.connect()
    query = Department.get_active()
    if name:
        query = query.where(Department.name.contains(name))
    query = query.order_by(Department.id)
    offset = (page - 1) * size
    result = list(query.offset(offset).limit(size))
    db.close()
    return result

@app.put("/departments/{dept_id}", response_model=DepartmentOut)
def update_department(dept_id: int, dept: DepartmentUpdate):
    db.connect()
    updated = Department.update_by_id(dept_id, **dept.dict(exclude_unset=True))
    db.close()
    if not updated:
        raise HTTPException(404, "Отделение не найдено")
    return updated

@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int):
    db.connect()
    result = Department.delete_by_id(dept_id)
    db.close()
    return {"deleted": result}