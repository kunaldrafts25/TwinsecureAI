import uuid
from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
# from sqlalchemy import ForeignKey # If linking to users
# from sqlalchemy.orm import relationship
from app.db.base import Base

class Report(Base):
    """
    Database model for generated reports.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    filename = Column(String, unique=True, nullable=False) # e.g., "weekly-summary-2025-04-23.pdf"
    # Store S3 URL or path where the file is stored
    file_location = Column(String, nullable=False)
    generation_params = Column(JSON, nullable=True) # Parameters used for generation (time range, filters)
    recommendations = Column(String, nullable=True) # Key recommendations from the report

    # Optional: Link to user who generated/triggered it
    # creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    # creator = relationship("User", back_populates="reports")

    generated_at = Column(DateTime(timezone=True), index=True, nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title}', filename='{self.filename}')>"