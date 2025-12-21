"""
Database models for wafer analysis persistence.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Lot(Base):
    __tablename__ = 'lots'
    
    id = Column(Integer, primary_key=True)
    lot_id = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_wafers = Column(Integer)
    defective_wafers = Column(Integer)
    yield_rate = Column(Float)
    
    wafers = relationship("Wafer", back_populates="lot")

class Wafer(Base):
    __tablename__ = 'wafers'
    
    id = Column(Integer, primary_key=True)
    wafer_id = Column(String(50), unique=True, nullable=False)
    lot_id = Column(Integer, ForeignKey('lots.id'))
    file_name = Column(String(255))
    tool_id = Column(String(50))
    chamber_id = Column(String(50))
    processed_at = Column(DateTime)
    analyzed_at = Column(DateTime, default=datetime.utcnow)
    predicted_class = Column(String(50))
    confidence = Column(Float)
    final_verdict = Column(String(10))
    severity = Column(String(20))
    
    lot = relationship("Lot", back_populates="wafers")
    defect_distributions = relationship("DefectDistribution", back_populates="wafer")

class DefectDistribution(Base):
    __tablename__ = 'defect_distributions'
    
    id = Column(Integer, primary_key=True)
    wafer_id = Column(Integer, ForeignKey('wafers.id'))
    pattern = Column(String(50))
    probability = Column(Float)
    
    wafer = relationship("Wafer", back_populates="defect_distributions")

# Database connection setup
DATABASE_URL = "sqlite:///./wafer_analysis.db"  # Using SQLite for simplicity, can switch to PostgreSQL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
