import os
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from .models import Base, Job

# sqlite for low-memory first start; PostgreSQL supported through DATABASE_URL.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./careerpilot.sqlite3")
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite:") else {})
SessionLocal = sessionmaker(bind=engine)

DEMO_JOBS = [
    ("demo-1", "Junior Cloud Engineer", "Demo Systems", "Bengaluru", "hybrid", "aws,linux,python", "Synthetic test listing, not a real vacancy."),
    ("demo-2", "Python Backend Developer", "Example Labs", "Kochi", "onsite", "python,fastapi,sql", "Synthetic test listing, not a real vacancy."),
    ("demo-3", "DevOps Engineer", "Sample Networks", "Hyderabad", "remote", "docker,terraform,aws", "Synthetic test listing, not a real vacancy."),
    ("demo-4", "Frontend Engineer", "Demo Systems", "Pune", "hybrid", "react,typescript,css", "Synthetic test listing, not a real vacancy."),
]

def initialize_demo_data():
    Base.metadata.create_all(engine)  # demo only; replace with Alembic migrations before public beta
    if os.getenv("APP_ENV", "development") != "development":
        return
    with SessionLocal.begin() as db:
        if db.scalar(select(func.count()).select_from(Job)) == 0:
            for source_id, title, company, city, mode, skills, description in DEMO_JOBS:
                db.add(Job(source="demo", source_id=source_id, title=title, company=company, city=city, mode=mode, skills=skills, description=description))
