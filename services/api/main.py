import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, or_, select
from .database import SessionLocal, initialize_demo_data
from .models import Job
from pydantic import BaseModel, ConfigDict

class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    company: str
    city: str
    mode: str
    skills: str
    source: str
    original_url: str | None
    verified_at: datetime

class JobsResponse(BaseModel):
    items: list[JobOut]
    total: int
    page: int
    page_size: int
    demo_data: bool

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_demo_data()
    yield

app = FastAPI(title="CareerPilot API", version="0.1.0", lifespan=lifespan, docs_url="/api/docs" if os.getenv("APP_ENV", "development") == "development" else None)
origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",") if o.strip()]
if "*" in origins:
    raise RuntimeError("Wildcard CORS origins are forbidden")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET"], allow_headers=["Accept", "Content-Type"], allow_credentials=False)

@app.middleware("http")
async def secure_headers(request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/api/health")
def health():
    return {"status": "ok", "environment": os.getenv("APP_ENV", "development")}

@app.get("/api/jobs", response_model=JobsResponse)
def list_jobs(q: str = Query(default="", max_length=100), city: str = Query(default="", max_length=80), mode: str = Query(default="", pattern="^(|remote|hybrid|onsite)$"), skill: str = Query(default="", max_length=80), page: int = Query(default=1, ge=1, le=1000), page_size: int = Query(default=20, ge=1, le=50)):
    stmt = select(Job)
    def escaped_like(value: str) -> str:
        return "%" + value.strip().replace("!", "!!").replace("%", "!%").replace("_", "!_") + "%"
    if q.strip():
        needle = escaped_like(q)
        stmt = stmt.where(or_(Job.title.ilike(needle, escape="!"), Job.company.ilike(needle, escape="!")))
    if city.strip():
        stmt = stmt.where(Job.city.ilike(escaped_like(city), escape="!"))
    if mode:
        stmt = stmt.where(Job.mode == mode)
    if skill.strip():
        stmt = stmt.where(Job.skills.ilike(escaped_like(skill), escape="!"))
    with SessionLocal() as db:
        total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        items = db.scalars(stmt.order_by(Job.id.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return JobsResponse(items=[JobOut.model_validate(x) for x in items], total=total, page=page, page_size=page_size, demo_data=bool(items) and all(x.source == "demo" for x in items))
