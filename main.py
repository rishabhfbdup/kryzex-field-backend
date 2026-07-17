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
    # यहाँ चेक करेंगे कि क्या एम्प्लॉई आईडी सही है (जैसे KRYZ-2604)
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

# 2. एम्प्लॉई की परफॉर्मेंस ट्रैक करने की API
@app.get("/employee-performance/{emp_id}")
def get_performance(emp_id: str, db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).filter(models.Merchant.onboarded_by_id == emp_id).all()
    total_added = len(merchants)
    activated_apps = len([m for m in merchants if m.app_status == "Activated"])
    
    return {
        "employee_id": emp_id,
        "total_shops_onboarded": total_added,
        "activated_apps": activated_apps,
        "pending_apps": total_added - activated_apps
    }
# सब मर्चेंट्स का डेटा एक साथ देखने के लिए API (Admin Dashboard के लिए)
@app.get("/get-all-merchants")
def get_all_merchants(db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).all()
    return merchants