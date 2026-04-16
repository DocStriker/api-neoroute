from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import DateTime, Enum, Column
from app.models.base import Base
import uuid

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    status = Column(Enum("pending", "running", "done", "error", name="job_status"))
    created_at = Column(DateTime, server_default=func.now())