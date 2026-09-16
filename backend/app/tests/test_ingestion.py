import pytest
from pathlib import Path
from app.services.ingestion import process_file
from unittest.mock import MagicMock
import tempfile
import os

def test_ingestion_chunking():
    # Create a temporary markdown file
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode="w", encoding="utf-8") as f:
        f.write("# Test Document\n\nThis is a test paragraph. " * 50)
        temp_path = f.name
        
    try:
        mock_db = MagicMock()
        mock_db.query().filter().first.return_value = None  # Not ingested yet
        
        # We need to mock get_embedding so it doesn't call ollama if not running
        import app.services.ingestion
        app.services.ingestion.get_embedding = MagicMock(return_value=[0.1] * 1536)
        
        process_file(Path(temp_path), mock_db)
        
        # Verify db.add_all was called with chunks
        assert mock_db.add_all.called
        args, _ = mock_db.add_all.call_args
        docs = args[0]
        
        assert len(docs) > 0
        assert docs[0].title == Path(temp_path).stem.replace("-", " ").title()
        assert len(docs[0].embedding) == 1536
        assert docs[0].source_id == Path(temp_path).name
        
    finally:
        os.remove(temp_path)
