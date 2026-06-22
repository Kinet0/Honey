"""
Intelligence and analytics routes
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attack import Command, Credential, Download, Attack
from app.main import get_session


router = APIRouter()


@router.get("/intelligence/commands")
async def get_command_frequency(
    limit: int = Query(20, ge=1, le=100),
    classification: Optional[str] = None,
    session: AsyncSession = Depends(get_session)
):
    """
    Get most frequently executed commands
    """
    query = select(
        Command.command,
        func.count(Command.id).label('count'),
        Command.classification,
        func.sum(func.cast(Command.success, 'int')).label('success_count')
    ).group_by(Command.command, Command.classification)
    
    if classification:
        query = query.where(Command.classification == classification)
    
    query = query.order_by(desc('count')).limit(limit)
    
    result = await session.execute(query)
    rows = result.all()
    
    return {
        "data": [
            {
                "command": row[0],
                "count": row[1],
                "classification": row[2],
                "success_rate": (row[3] or 0) / row[1] if row[1] > 0 else 0
            }
            for row in rows
        ]
    }


@router.get("/intelligence/credentials")
async def get_credentials_analysis(
    credential_type: str = Query("usernames", regex="^(usernames|passwords)$"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Get top usernames and passwords used in attacks
    """
    
    if credential_type == "usernames":
        query = select(
            Credential.username,
            func.count(Credential.id).label('count'),
            func.sum(func.cast(Credential.success, 'int')).label('success_count')
        ).group_by(Credential.username).order_by(desc('count')).limit(limit)
        
        result = await session.execute(query)
        rows = result.all()
        
        return {
            "top_usernames": [
                {
                    "username": row[0],
                    "count": row[1],
                    "success_count": row[2] or 0,
                    "success_rate": (row[2] or 0) / row[1] if row[1] > 0 else 0
                }
                for row in rows
            ]
        }
    
    else:  # passwords
        query = select(
            Credential.password,
            func.count(Credential.id).label('count'),
            func.sum(func.cast(Credential.success, 'int')).label('success_count')
        ).group_by(Credential.password).order_by(desc('count')).limit(limit)
        
        result = await session.execute(query)
        rows = result.all()
        
        return {
            "top_passwords": [
                {
                    "password": row[0],
                    "count": row[1],
                    "success_count": row[2] or 0,
                    "success_rate": (row[2] or 0) / row[1] if row[1] > 0 else 0
                }
                for row in rows
            ]
        }


@router.get("/intelligence/payloads")
async def get_payloads_analysis(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Get payload download analysis
    """
    total_downloads = await session.scalar(select(func.count(Download.id)))
    
    query = select(
        Download.filename,
        func.count(Download.id).label('count'),
        Download.file_hash,
        Download.file_size,
        Download.file_type
    ).group_by(
        Download.filename,
        Download.file_hash,
        Download.file_size,
        Download.file_type
    ).order_by(desc('count')).limit(limit)
    
    result = await session.execute(query)
    rows = result.all()
    
    unique_payloads = await session.scalar(
        select(func.count(func.distinct(Download.filename)))
    )
    
    return {
        "total_downloads": total_downloads or 0,
        "unique_payloads": unique_payloads or 0,
        "payloads": [
            {
                "filename": row[0],
                "count": row[1],
                "file_hash": row[2],
                "file_size": row[3],
                "file_type": row[4]
            }
            for row in rows
        ]
    }
