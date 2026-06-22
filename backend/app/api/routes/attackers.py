"""
Attacker profile and intelligence routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.attack import Attacker, Session as DBSession, Command
from app.schemas.attack import AttackerResponse, PaginatedResponse
from app.main import get_session


router = APIRouter()


@router.get("/attackers", response_model=PaginatedResponse)
async def list_attackers(
    threat_level: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_session)
):
    """
    List attackers with optional filtering
    """
    query = select(Attacker).order_by(desc(Attacker.last_seen))
    
    # Apply filters
    if threat_level:
        query = query.where(Attacker.threat_level == threat_level)
    
    if country:
        query = query.where(Attacker.country_code == country)
    
    # Get total count
    count_query = select(func.count(Attacker.ip_address))
    total = await session.scalar(count_query)
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    attackers = result.scalars().all()
    
    return PaginatedResponse(
        data=[AttackerResponse.from_orm(attacker) for attacker in attackers],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/attackers/{ip}", response_model=dict)
async def get_attacker_profile(
    ip: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed attacker profile
    """
    result = await session.execute(
        select(Attacker)
        .where(Attacker.ip_address == ip)
        .options(
            selectinload(Attacker.sessions)
        )
    )
    attacker = result.unique().scalar_one_or_none()
    
    if not attacker:
        raise HTTPException(status_code=404, detail="Attacker not found")
    
    # Get top commands
    commands_result = await session.execute(
        select(Command.command, func.count(Command.id).label('count'))
        .select_from(Command)
        .join(DBSession)
        .where(DBSession.attacker_ip == ip)
        .group_by(Command.command)
        .order_by(desc('count'))
        .limit(10)
    )
    top_commands = [
        {"command": cmd[0], "count": cmd[1]}
        for cmd in commands_result.all()
    ]
    
    return {
        "ip_address": attacker.ip_address,
        "country": attacker.country_code,
        "country_code": attacker.country_code,
        "asn": attacker.asn,
        "isp": attacker.isp,
        "first_seen": attacker.first_seen,
        "last_seen": attacker.last_seen,
        "session_count": attacker.total_sessions,
        "command_count": attacker.total_commands,
        "download_count": attacker.total_downloads,
        "max_severity": attacker.max_severity,
        "threat_level": attacker.threat_level,
        "recent_sessions": [
            {
                "id": s.id,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "status": s.status,
                "command_count": s.total_commands
            }
            for s in sorted(attacker.sessions, key=lambda x: x.start_time, reverse=True)[:5]
        ],
        "top_commands": top_commands
    }


@router.get("/attackers/{ip}/timeline")
async def get_attacker_timeline(
    ip: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get attack story timeline for an attacker
    """
    result = await session.execute(
        select(Attacker)
        .where(Attacker.ip_address == ip)
        .options(
            selectinload(Attacker.sessions).selectinload(DBSession.attacks),
            selectinload(Attacker.sessions).selectinload(DBSession.commands),
            selectinload(Attacker.sessions).selectinload(DBSession.downloads)
        )
    )
    attacker = result.unique().scalar_one_or_none()
    
    if not attacker:
        raise HTTPException(status_code=404, detail="Attacker not found")
    
    # Build timeline from all sessions
    timeline = []
    
    # Get earliest session
    if attacker.sessions:
        earliest_session = min(attacker.sessions, key=lambda x: x.start_time)
        
        timeline.append({
            "stage": "connection",
            "timestamp": earliest_session.start_time,
            "details": "Initial connection established",
            "session_id": earliest_session.id
        })
        
        # Add auth attempts
        auth_attacks = [
            a for s in attacker.sessions for a in s.attacks
            if a.event_type == "auth_attempt"
        ]
        if auth_attacks:
            first_auth = min(auth_attacks, key=lambda x: x.timestamp)
            timeline.append({
                "stage": "authentication",
                "timestamp": first_auth.timestamp,
                "details": "Authentication attempts made",
                "session_id": first_auth.session_id
            })
        
        # Add successful login
        login_attacks = [
            a for s in attacker.sessions for a in s.attacks
            if a.event_type == "login"
        ]
        if login_attacks:
            first_login = min(login_attacks, key=lambda x: x.timestamp)
            timeline.append({
                "stage": "login",
                "timestamp": first_login.timestamp,
                "details": "Successful authentication",
                "session_id": first_login.session_id
            })
        
        # Add reconnaissance
        all_commands = [cmd for s in attacker.sessions for cmd in s.commands]
        recon_commands = [
            c for c in all_commands
            if c.classification == "reconnaissance"
        ]
        if recon_commands:
            first_recon = min(recon_commands, key=lambda x: x.timestamp)
            cmd_list = ", ".join([c.command.split()[0] for c in recon_commands[:3]])
            timeline.append({
                "stage": "reconnaissance",
                "timestamp": first_recon.timestamp,
                "details": f"Executed commands: {cmd_list}",
                "session_id": first_recon.session_id
            })
        
        # Add downloads
        all_downloads = [d for s in attacker.sessions for d in s.downloads]
        if all_downloads:
            first_download = min(all_downloads, key=lambda x: x.timestamp)
            timeline.append({
                "stage": "download",
                "timestamp": first_download.timestamp,
                "details": f"Downloaded {first_download.filename}",
                "session_id": first_download.session_id
            })
        
        # Add execution
        execution_commands = [
            c for c in all_commands
            if c.classification == "execution"
        ]
        if execution_commands:
            first_execution = min(execution_commands, key=lambda x: x.timestamp)
            timeline.append({
                "stage": "execution",
                "timestamp": first_execution.timestamp,
                "details": f"Executed: {first_execution.command}",
                "session_id": first_execution.session_id
            })
    
    # Sort by timestamp
    timeline.sort(key=lambda x: x["timestamp"])
    
    return {
        "ip_address": ip,
        "timeline": timeline
    }
