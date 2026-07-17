from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import datetime
import enum

Base = declarative_base()

# ऐप का स्टेटस ट्रैक करने के लिए Enums
class AppStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    ACTIVATED = "Activated"

class PayoutStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"

# 1. Employees Table (स्टाफ रिकॉर्ड)
class Employee(Base):
    __tablename__ = "employees"

    # जैसे: KRYZ-2604
    employee_id = Column(String, primary_key=True, index=True) 
    name = Column(String, nullable=False)
    role = Column(String, default="Sales Agent")
    mobile_number = Column(String, unique=True, nullable=False)
    
    # इस एम्प्लॉई ने जितने मर्चेंट जोड़े, उनकी लिस्ट यहाँ से ट्रैक होगी
    merchants = relationship("Merchant", back_populates="onboarded_by")

# 2. Merchants Table (दुकानदारों का रिकॉर्ड)
class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shop_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    location_address = Column(String, nullable=False)
    
    # फॉरेन की (Foreign Key) - जो एम्प्लॉई आईडी से लिंक है
    onboarded_by_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    
    # स्टेटस ट्रैकिंग
    app_status = Column(Enum(AppStatusEnum), default=AppStatusEnum.PENDING)
    payout_status = Column(Enum(PayoutStatusEnum), default=PayoutStatusEnum.PENDING)
    
    # डेटा एंट्री का समय
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # रिलेशनशिप मैपिंग
    onboarded_by = relationship("Employee", back_populates="merchants")
    from sqlalchemy import Column, Integer, String

# नई एम्प्लोयी टेबल (लॉगिन क्रेडेंशियल्स के लिए)

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary key=True, index=True)
    emp_id = Column(String, unique=True, index=True) # जैसे: KRYZ-101
    emp_name = Column(String)
    password = Column(String) # लॉगिन पासवर्ड