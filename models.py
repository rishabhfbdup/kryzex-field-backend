from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
import datetime
import enum

Base = declarative_base()

class AppStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    ACTIVATED = "Activated"
    DECLINED = "Declined" # नया स्टेटस रिजेक्शन के लिए

class PayoutStatusEnum(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"

# 1. Employees Table
class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, default="Sales Agent")
    mobile_number = Column(String, nullable=True)
    password = Column(String, nullable=False, default="123456")
    
    merchants = relationship("Merchant", back_populates="onboarded_by")

# 2. Merchants Table
class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    shop_name = Column(String, nullable=False)
    owner_name = Column(String, nullable=False)
    mobile_number = Column(String, nullable=False)
    location_address = Column(String, nullable=False)
    shop_photo_url = Column(String, nullable=True)
    
    onboarded_by_id = Column(String, ForeignKey("employees.employee_id"), nullable=False)
    
    app_status = Column(Enum(AppStatusEnum), default=AppStatusEnum.PENDING)
    payout_status = Column(Enum(PayoutStatusEnum), default=PayoutStatusEnum.PENDING)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    onboarded_by = relationship("Employee", back_populates="merchants")