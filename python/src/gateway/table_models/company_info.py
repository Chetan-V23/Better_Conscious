from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint

class CompanyInfo(Base):
    __tablename__ = "company_info"
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, unique=True, index=True, nullable=False)
    
class CompanyActs(Base):
    __tablename__ = "company_acts"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("company_info.id"), nullable=False)
    act_severity = Column(Integer, nullable=False)
    act_title = Column(String, nullable=False)
    act_description = Column(String, nullable=False)
    
    __table_args__ = (
        CheckConstraint("act_severity IN (1, 2, 3, 4)", name="check_act_severity"),
    )
