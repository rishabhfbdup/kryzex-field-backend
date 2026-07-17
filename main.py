from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import models

app = FastAPI(title="Kryzex Field API")

@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

SQLALCHEMY_DATABASE_URL = "sqlite:///./kryzex_field.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/submit-merchant/")
def submit_merchant(shop_name: str, owner_name: str, mobile_number: str, location_address: str, onboarded_by_id: str, shop_photo_url: str = "", db: Session = Depends(get_db)):
    emp_exists = db.query(models.Employee).filter(models.Employee.employee_id == onboarded_by_id).first()
    if not emp_exists:
        return {"status": "Error", "message": "Authorized Employee ID space not found!"}

    db_merchant = models.Merchant(
        shop_name=shop_name,
        owner_name=owner_name,
        mobile_number=mobile_number,
        location_address=location_address,
        onboarded_by_id=onboarded_by_id,
        shop_photo_url=shop_photo_url
    )
    db.add(db_merchant)
    db.commit()
    return {"status": "Success", "message": "Merchant added successfully"}

@app.get("/employee-performance/{emp_id}")
def get_performance(emp_id: str, db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).filter(models.Merchant.onboarded_by_id == emp_id).all()
    total_added = len(merchants)
    approved_count = len([m for m in merchants if m.app_status == "Activated" or m.app_status == models.AppStatusEnum.ACTIVATED])
    
    return {
        "employee_id": emp_id,
        "total_shops_onboarded": total_added,
        "approved_apps": approved_count,
        "pending_apps": total_added - approved_count
    }

@app.get("/get-all-merchants")
def get_all_merchants(db: Session = Depends(get_db)):
    return db.query(models.Merchant).all()

@app.post("/create-employee")
def create_employee(emp_id: str, emp_name: str, password: str, db: Session = Depends(get_db)):
    existing = db.query(models.Employee).filter(models.Employee.employee_id == emp_id).first()
    if existing: return {"status": "Error", "message": "Employee ID already exists!"}
    new_emp = models.Employee(employee_id=emp_id, name=emp_name, password=password)
    db.add(new_emp)
    db.commit()
    return {"status": "Success", "message": "Employee created successfully!"}

@app.post("/employee-login")
def employee_login(emp_id: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Employee).filter(models.Employee.employee_id == emp_id, models.Employee.password == password).first()
    if user: return {"status": "Success", "emp_name": user.name}
    return {"status": "Error", "message": "Galat ID ya Password!"}