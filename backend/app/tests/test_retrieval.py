import pytest
from unittest.mock import MagicMock
from app.services.retrieval import search_transcripts
from app.models.document import DocumentChunk

def test_search_transcripts():
    mock_db = MagicMock()
    
    # Mock embedding
    import app.services.retrieval
    app.services.retrieval.get_embedding = MagicMock(return_value=[0.1] * 1536)
    
    # Mock DB result
    mock_doc = DocumentChunk(
        title="Test Podcast",
        source_id="test.md",
        content="This is a relevant chunk",
        metadata_={"chunk_index": 0}
    )
    
    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_doc]
    mock_db.execute.return_value = mock_result
    
    results = search_transcripts("growth strategies", mock_db, limit=1)
    
    assert len(results) == 1
    assert results[0]["title"] == "Test Podcast"
    assert results[0]["content"] == "This is a relevant chunk"
    assert results[0]["metadata"]["chunk_index"] == 0
