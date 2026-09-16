from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Any
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str
    sources: Optional[List[Any]] = None

class MessageCreate(MessageBase):
    provider: Optional[str] = "ollama"
    skill: Optional[str] = None

class Message(MessageBase):
    id: str
    session_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SessionBase(BaseModel):
    title: str

class SessionCreate(SessionBase):
    title: str = "New Conversation"

class Session(SessionBase):
    id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SessionWithMessages(Session):
    messages: List[Message] = []
