import os
import json
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.document import DocumentChunk
from app.core.database import SessionLocal, engine
from langchain_text_splitters import RecursiveCharacterTextSplitter
import ollama

logger = logging.getLogger(__name__)

def get_embedding(text: str) -> list[float]:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    return response["embedding"]

def process_file(filepath: Path, db: Session):
    exists = db.query(DocumentChunk).filter(DocumentChunk.source_id == filepath.name).first()
    if exists:
        logger.info(f"Skipping {filepath.name}, already ingested.")
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        logger.warning(f"Could not read {filepath}: {e}")
        return

    title = filepath.stem.replace("-", " ").title()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(content)

    docs_to_insert = []
    for i, chunk in enumerate(chunks):
        try:
            embedding = get_embedding(chunk)
            doc = DocumentChunk(
                source_id=filepath.name,
                title=title,
                content=chunk,
                metadata_={"chunk_index": i},
                embedding=embedding
            )
            docs_to_insert.append(doc)
        except Exception as e:
            logger.error(f"Error embedding chunk {i} in {filepath.name}: {e}")
            break
            
    if docs_to_insert:
        db.add_all(docs_to_insert)
        db.commit()
        logger.info(f"Ingested {filepath.name} into {len(docs_to_insert)} chunks.")

def ingest_all(data_dir: str):
    db = SessionLocal()
    try:
        path = Path(data_dir)
        for cat in ["newsletters", "podcasts"]:
            cat_path = path / cat
            if cat_path.exists():
                md_files = list(cat_path.glob("*.md"))
                logger.info(f"Found {len(md_files)} files in {cat}")
                for md_file in md_files:
                    process_file(md_file, db)
    finally:
        db.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data"))
    logger.info(f"Starting ingestion from {data_dir}")
    
    # Ensure tables exist
    from app.core.database import Base
    from sqlalchemy import text
    try:
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
    except Exception:
        pass
    Base.metadata.create_all(bind=engine)
    
    ingest_all(data_dir)
