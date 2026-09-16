from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models import session as models
from app.schemas import session as schemas

router = APIRouter()

@router.post("/", response_model=schemas.Session)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    db_session = models.Session(title=session.title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/", response_model=List[schemas.Session])
def get_sessions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    sessions = db.query(models.Session).order_by(models.Session.updated_at.desc()).offset(skip).limit(limit).all()
    return sessions

@router.get("/{session_id}", response_model=schemas.SessionWithMessages)
def get_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

from app.services.agent import Agent

@router.post("/{session_id}/messages", response_model=schemas.Message)
def create_message(session_id: str, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    user_msg = models.Message(
        session_id=session_id,
        role=message.role,
        content=message.content
    )
    db.add(user_msg)
    db.commit()
    
    # Get history
    history_msgs = db.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at.asc()).all()
    history = [{"role": m.role, "content": m.content} for m in history_msgs[:-1]] # exclude the one just added
    
    # Agent processing
    agent = Agent(provider_name=message.provider or "ollama")
    response_data = agent.process_message(message.content, history, skill=message.skill)
    
    # Save assistant message
    asst_msg = models.Message(
        session_id=session_id,
        role=response_data["role"],
        content=response_data["content"],
        sources=response_data["sources"]
    )
    db.add(asst_msg)
    db.commit()
    db.refresh(asst_msg)
    
    return asst_msg
