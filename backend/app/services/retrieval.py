from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.document import DocumentChunk
from app.services.ingestion import get_embedding

def search_transcripts(query: str, db: Session, limit: int = 5):
    """
    Search for transcript chunks similar to the query using pgvector.
    """
    query_embedding = get_embedding(query)
    
    # Use L2 distance (<->) for similarity search
    # We order by distance and get top 'limit' results
    stmt = select(DocumentChunk).order_by(
        DocumentChunk.embedding.l2_distance(query_embedding)
    ).limit(limit)
    
    results = db.execute(stmt).scalars().all()
    
    return [
        {
            "title": doc.title,
            "source_id": doc.source_id,
            "content": doc.content,
            "metadata": doc.metadata_
        }
        for doc in results
    ]
