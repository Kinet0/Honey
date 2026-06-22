"""
Attack data routes
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attack import Attack, Session as DBSession, Attacker, Severity
from app.schemas.attack import (
    AttackResponse, PaginatedResponse, AttackFilter, AttackStatistics, SeverityEnum
)
from app.main import get_session


router = APIRouter()


@router.get("/attacks/feed", response_model=PaginatedResponse)
async def get_attacks_feed(
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    severity: Optional[SeverityEnum] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Get recent attack feed with pagination
    """
    query = select(Attack).order_by(desc(Attack.timestamp))
    
    # Apply severity filter if provided
    if severity:
        query = query.where(Attack.severity == severity.value)
    
    # Get total count
    count_query = select(func.count(Attack.id))
    if severity:
        count_query = count_query.where(Attack.severity == severity.value)
    
    total = await session.scalar(count_query)
    
    # Apply pagination
    query = query.limit(limit).offset(offset)
    
    result = await session.execute(query)
    attacks = result.scalars().all()
    
    return PaginatedResponse(
        data=[AttackResponse.from_orm(attack) for attack in attacks],
        total=total,
        limit=limit,
        offset=offset
    )


@router.get("/attacks/statistics", response_model=AttackStatistics)
async def get_attack_statistics(session: AsyncSession = Depends(get_session)):
    """
    Get attack statistics
    """
    now = datetime.utcnow()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Attacks today
    attacks_today = await session.scalar(
        select(func.count(Attack.id)).where(Attack.timestamp >= today)
    )
    
    # Attacks this week
    attacks_week = await session.scalar(
        select(func.count(Attack.id)).where(Attack.timestamp >= week_ago)
    )
    
    # Attacks this month
    attacks_month = await session.scalar(
        select(func.count(Attack.id)).where(Attack.timestamp >= month_ago)
    )
    
    # Unique attackers
    unique_attackers = await session.scalar(
        select(func.count(func.distinct(Attack.attacker_ip)))
    )
    
    # Unique countries
    unique_countries = await session.scalar(
        select(func.count(func.distinct(Attack.country_code)))
    )
    
    # Total commands (from commands table)
    from app.models.attack import Command
    total_commands = await session.scalar(
        select(func.count(Command.id))
    )
    
    # Total downloads (from downloads table)
    from app.models.attack import Download
    total_downloads = await session.scalar(
        select(func.count(Download.id))
    )
    
    # Average session duration
    avg_duration = await session.scalar(
        select(func.avg(DBSession.duration_seconds)).where(
            DBSession.duration_seconds.isnot(None)
        )
    )
    
    return AttackStatistics(
        attacks_today=attacks_today or 0,
        attacks_this_week=attacks_week or 0,
        attacks_this_month=attacks_month or 0,
        unique_attackers=unique_attackers or 0,
        unique_countries=unique_countries or 0,
        total_commands=total_commands or 0,
        total_downloads=total_downloads or 0,
        avg_session_duration=avg_duration
    )


@router.post("/attacks/search", response_model=PaginatedResponse)
async def search_attacks(
    filters: AttackFilter,
    session: AsyncSession = Depends(get_session)
):
    """
    Search and filter attacks
    """
    query = select(Attack)
    conditions = []
    
    # Apply filters
    if filters.country:
        conditions.append(Attack.country_code == filters.country)
    
    if filters.asn:
        conditions.append(Attack.asn == filters.asn)
    
    if filters.severity:
        conditions.append(Attack.severity == filters.severity.value)
    
    if filters.start_date:
        conditions.append(Attack.timestamp >= filters.start_date)
    
    if filters.end_date:
        conditions.append(Attack.timestamp <= filters.end_date)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # Get total count
    count_query = select(func.count(Attack.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total = await session.scalar(count_query)
    
    # Order and paginate
    query = query.order_by(desc(Attack.timestamp)).limit(filters.limit).offset(filters.offset)
    
    result = await session.execute(query)
    attacks = result.scalars().all()
    
    return PaginatedResponse(
        data=[AttackResponse.from_orm(attack) for attack in attacks],
        total=total,
        limit=filters.limit,
        offset=filters.offset
    )


@router.get("/attacks/{attack_id}", response_model=AttackResponse)
async def get_attack_details(
    attack_id: str,
    session: AsyncSession = Depends(get_session)
):
    """
    Get detailed information about a specific attack
    """
    result = await session.execute(
        select(Attack).where(Attack.id == attack_id)
    )
    attack = result.scalar_one_or_none()
    
    if not attack:
        raise HTTPException(status_code=404, detail="Attack not found")
    
    return AttackResponse.from_orm(attack)
