from sqlalchemy import create_engine, Column, Integer, String, Date, JSON, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class Company(Base):
    __tablename__ = 'companies'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String)
    sector = Column(String)
    industry = Column(String)
    
    statements = relationship("FinancialStatement", back_populates="company")

class FinancialStatement(Base):
    __tablename__ = 'financial_statements'
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    statement_type = Column(String, nullable=False) # 'income', 'balance', 'cash'
    fiscal_date_ending = Column(Date, nullable=False)
    data = Column(JSON, nullable=False)
    
    company = relationship("Company", back_populates="statements")

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///finance.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
