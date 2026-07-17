from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import sessionmaker, Session
import models

app = FastAPI(title="Kryzex Field API")

# HTML फाइल दिखाने के लिए रास्ता
@app.get("/")
async def read_index():
    return FileResponse('static/index.html')

# लोकल टेस्ट के लिए SQLite डेटाबेस का इस्तेमाल कर रहे हैं
SQLALCHEMY_DATABASE_URL = "sqlite:///./kryzex_field.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# डेटाबेस टेबल्स बनाना
models.Base.metadata.create_all(bind=engine)

# डेटाबेस सेशन हैंडलर
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. नया मर्चेंट (दुकानदार) जोड़ने की API
@app.post("/submit-merchant/")
def submit_merchant(shop_name: str, owner_name: str, mobile_number: str, location_address: str, onboarded_by_id: str, db: Session = Depends(get_db)):
    # पहले चेक करो कि क्या यह एम्प्लोयी डेटाबेस में एक्सिस्ट करता है
    emp_exists = db.query(models.Employee).filter(models.Employee.employee_id == onboarded_by_id).first()
    if not emp_exists:
        return {"status": "Error", "message": "Authorized Employee ID space not found! Please check ID or create it from Admin panel."}

    db_merchant = models.Merchant(
        shop_name=shop_name,
        owner_name=owner_name,
        mobile_number=mobile_number,
        location_address=location_address,
        onboarded_by_id=onboarded_by_id
    )
    db.add(db_merchant)
    db.commit()
    db.refresh(db_merchant)
    return {"status": "Success", "message": "Merchant added successfully", "merchant_id": db_merchant.id}

# 2. एम्प्लोयी की परफॉर्मेंस ट्रैक करने की API
@app.get("/employee-performance/{emp_id}")
def get_performance(emp_id: str, db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).filter(models.Merchant.onboarded_by_id == emp_id).all()
    total_added = len(merchants)
    activated_apps = len([m for m in merchants if m.app_status == "Activated" or m.app_status == models.AppStatusEnum.ACTIVATED])
    
    return {
        "employee_id": emp_id,
        "total_shops_onboarded": total_added,
        "activated_apps": activated_apps,
        "pending_apps": total_added - activated_apps
    }

# 3. सब मर्चेंट्स का डेटा एक साथ देखने के लिए API (Admin Dashboard के लिए)
@app.get("/get-all-merchants")
def get_all_merchants(db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).all()
    return merchants

# 4. नया एम्प्लोयी बनाने की API (सिर्फ कंपनी एडमिन के लिए - models.py के साथ फिक्स)
@app.post("/create-employee")
def create_employee(emp_id: str, emp_name: str, password: str, db: Session = Depends(get_db)):
    # चेक करो कि एम्प्लोयी पहले से तो नहीं है
    existing = db.query(models.Employee).filter(models.Employee.employee_id == emp_id).first()
    if existing:
        return {"status": "Error", "message": "Employee ID already exists!"}
    
    new_emp = models.Employee(employee_id=emp_id, name=emp_name, password=password)
    db.add(new_emp)
    db.commit()
    return {"status": "Success", "message": f"Employee {emp_name} created successfully!"}

# 5. फील्ड एम्प्लोयी लॉगिन चेक करने की API (models.py के साथ फिक्स)
@app.post("/employee-login")
def employee_login(emp_id: str, password: str, db: Session = Depends(get_db)):
    user = db.query(models.Employee).filter(models.Employee.employee_id == emp_id, models.Employee.password == password).first()
    if user:
        return {"status": "Success", "message": "Login Successful", "emp_name": user.name}
    else:
        return {"status": "Error", "message": "Galat ID ya Password!"}