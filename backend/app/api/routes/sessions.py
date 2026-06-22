"""
Session routes
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.attack import Session as DBSession, SessionStatus
from app.schemas.attack import SessionResponse, PaginatedResponse
from app.main import get_session


router = APIRouter()


@router.get("/sessions", response_model=PaginatedResponse)
async def list_sessions(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """
    List attack sessions with optional filtering
    """
    query = select(DBSession).order_by(desc(DBSession.start_time))
    
    # Filter by status if provided
    if status:
        query = query.where(DBSession.status == status)
    
    # Get total count
    count_query = select(func.count(DBSession.id))
    if status:
        count_query = count_query.where(DBSession.status == status)
    total = await session.scalar(count_query)
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    sessions = result.scalars().all()
    
    return PaginatedResponse(
        data=[SessionResponse.from_orm(s) for s in sessions],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/sessions/{session_id}", response_model=dict)
async def get_session_details(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed information about a specific session
    """
    result = await session.execute(
        select(DBSession)
        .where(DBSession.id == session_id)
        .options(
            selectinload(DBSession.commands),
            selectinload(DBSession.downloads),
            selectinload(DBSession.credentials),
            selectinload(DBSession.attacker)
        )
    )
    db_session = result.unique().scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "id": db_session.id,
        "attacker_ip": db_session.attacker_ip,
        "attacker": {
            "country": db_session.attacker.country_code,
            "asn": db_session.attacker.asn,
            "isp": db_session.attacker.isp,
            "first_seen": db_session.attacker.first_seen,
            "last_seen": db_session.attacker.last_seen,
            "session_count": db_session.attacker.total_sessions,
            "command_count": db_session.attacker.total_commands
        },
        "start_time": db_session.start_time,
        "end_time": db_session.end_time,
        "duration_seconds": db_session.duration_seconds,
        "status": db_session.status,
        "protocol": db_session.protocol,
        "commands": [
            {
                "timestamp": cmd.timestamp,
                "command": cmd.command,
                "classification": cmd.classification,
                "success": cmd.success,
                "output": cmd.output
            }
            for cmd in db_session.commands
        ],
        "downloads": [
            {
                "timestamp": dl.timestamp,
                "filename": dl.filename,
                "file_hash": dl.file_hash,
                "file_size": dl.file_size
            }
            for dl in db_session.downloads
        ],
        "credentials_attempted": [
            {
                "username": cred.username,
                "password": cred.password,
                "success": cred.success
            }
            for cred in db_session.credentials
        ]
    }


@router.get("/sessions/{session_id}/replay")
async def get_session_replay(
    session_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get session data for replay functionality
    """
    result = await session.execute(
        select(DBSession)
        .where(DBSession.id == session_id)
        .options(
            selectinload(DBSession.attacks),
            selectinload(DBSession.commands),
            selectinload(DBSession.downloads)
        )
    )
    db_session = result.unique().scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build event list for replay
    events = []
    
    # Connection event
    events.append({
        "timestamp": db_session.start_time,
        "type": "connection",
        "data": {}
    })
    
    # Sort all events by timestamp
    all_events = []
    
    for attack in db_session.attacks:
        all_events.append({
            "timestamp": attack.timestamp,
            "type": "attack",
            "event_type": attack.event_type
        })
    
    for cmd in db_session.commands:
        all_events.append({
            "timestamp": cmd.timestamp,
            "type": "command",
            "command": cmd.command,
            "output": cmd.output
        })
    
    for dl in db_session.downloads:
        all_events.append({
            "timestamp": dl.timestamp,
            "type": "download",
            "filename": dl.filename
        })
    
    all_events.sort(key=lambda x: x["timestamp"])
    events.extend(all_events)
    
    # Disconnect event
    if db_session.end_time:
        events.append({
            "timestamp": db_session.end_time,
            "type": "disconnect",
            "data": {}
        })
    
    return {
        "session_id": db_session.id,
        "duration_seconds": db_session.duration_seconds,
        "events": events
    }
