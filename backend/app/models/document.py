from sqlalchemy import Column, String, Text, JSON, Integer
from pgvector.sqlalchemy import Vector
from app.core.database import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True, default=generate_uuid, index=True)
    source_id = Column(String, index=True, nullable=False) # e.g., the URL or filename
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, nullable=True) # guest name, date, type
    embedding = Column(Vector(768)) # nomic-embed-text is 768 dims
