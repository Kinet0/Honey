"""
Analytics and statistics routes
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attack import Attack, Attacker, Command, Download
from app.main import get_session


router = APIRouter()


@router.get("/analytics/trends")
async def get_activity_trends(
    period: str = Query("hourly", regex="^(hourly|daily|weekly)$"),
    days: int = Query(7, ge=1, le=90),
    session: AsyncSession = Depends(get_session)
):
    """
    Get activity trends over time
    """
    now = datetime.utcnow()
    start_date = now - timedelta(days=days)
    
    # For now, return empty data structure
    # In production, this would aggregate from activity_stats table
    # or calculate from attacks in real-time
    
    data = []
    current_date = start_date
    
    while current_date <= now:
        if period == "hourly":
            next_date = current_date + timedelta(hours=1)
        elif period == "daily":
            next_date = current_date + timedelta(days=1)
        else:  # weekly
            next_date = current_date + timedelta(weeks=1)
        
        # Count attacks in this period
        attack_count = await session.scalar(
            select(func.count(Attack.id)).where(
                Attack.timestamp >= current_date,
                Attack.timestamp < next_date
            )
        )
        
        unique_attackers = await session.scalar(
            select(func.count(func.distinct(Attack.attacker_ip))).where(
                Attack.timestamp >= current_date,
                Attack.timestamp < next_date
            )
        )
        
        unique_countries = await session.scalar(
            select(func.count(func.distinct(Attack.country_code))).where(
                Attack.timestamp >= current_date,
                Attack.timestamp < next_date
            )
        )
        
        data.append({
            "timestamp": current_date,
            "attacks": attack_count or 0,
            "unique_attackers": unique_attackers or 0,
            "unique_countries": unique_countries or 0
        })
        
        current_date = next_date
    
    return {
        "period": period,
        "data": data
    }


@router.get("/analytics/map")
async def get_world_map_data(
    session: AsyncSession = Depends(get_session)
):
    """
    Get geographic attack data for world map
    """
    # Get attack counts by country
    result = await session.execute(
        select(
            Attack.country_code,
            func.count(Attack.id).label('attack_count'),
            func.count(func.distinct(Attack.attacker_ip)).label('unique_attackers')
        )
        .where(Attack.country_code.isnot(None))
        .group_by(Attack.country_code)
        .order_by(desc('attack_count'))
    )
    
    rows = result.all()
    
    # Get max count for intensity calculation
    max_count = max([row[1] for row in rows]) if rows else 1
    
    # Country name mapping (simplified - in production, use a complete mapping)
    country_names = {
        'CN': 'China',
        'RU': 'Russia',
        'US': 'United States',
        'IN': 'India',
        'BR': 'Brazil',
        'DE': 'Germany',
        'FR': 'France',
        'JP': 'Japan',
        'KR': 'South Korea',
        'GB': 'United Kingdom',
        # Add more as needed
    }
    
    # Country coordinates (latitude, longitude)
    country_coords = {
        'CN': (35.8617, 104.1954),
        'RU': (61.5240, 105.3188),
        'US': (37.0902, -95.7129),
        'IN': (20.5937, 78.9629),
        'BR': (-14.2350, -51.9253),
        'DE': (51.1657, 10.4515),
        'FR': (46.2276, 2.2137),
        'JP': (36.2048, 138.2529),
        'KR': (35.9078, 127.7669),
        'GB': (55.3781, -3.4360),
    }
    
    data = []
    for row in rows:
        country_code = row[0]
        attack_count = row[1]
        unique_attackers = row[2]
        
        if country_code in country_coords:
            lat, lon = country_coords[country_code]
        else:
            # Default to approximate world center
            lat, lon = 20.0, 0.0
        
        intensity = min(attack_count / max_count, 1.0) if max_count > 0 else 0.0
        
        data.append({
            "country_code": country_code,
            "country_name": country_names.get(country_code, country_code),
            "latitude": lat,
            "longitude": lon,
            "attack_count": attack_count,
            "unique_attackers": unique_attackers,
            "intensity": intensity
        })
    
    return {"data": data}


@router.get("/analytics/toplist/{list_type}")
async def get_top_list(
    list_type: str = Query(..., regex="^(countries|asns|usernames|commands|payloads)$"),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session)
):
    """
    Get top lists by various categories
    """
    
    if list_type == "countries":
        result = await session.execute(
            select(
                Attack.country_code,
                func.count(Attack.id).label('count')
            )
            .where(Attack.country_code.isnot(None))
            .group_by(Attack.country_code)
            .order_by(desc('count'))
            .limit(limit)
        )
        rows = result.all()
        total = sum([row[1] for row in rows])
        
        return {
            "type": "countries",
            "data": [
                {
                    "rank": i + 1,
                    "name": row[0],
                    "code": row[0],
                    "value": row[1],
                    "percentage": row[1] / total if total > 0 else 0
                }
                for i, row in enumerate(rows)
            ]
        }
    
    elif list_type == "asns":
        result = await session.execute(
            select(
                Attack.asn,
                func.count(Attack.id).label('count')
            )
            .where(Attack.asn.isnot(None))
            .group_by(Attack.asn)
            .order_by(desc('count'))
            .limit(limit)
        )
        rows = result.all()
        total = sum([row[1] for row in rows])
        
        return {
            "type": "asns",
            "data": [
                {
                    "rank": i + 1,
                    "name": f"ASN {row[0]}",
                    "value": row[1],
                    "percentage": row[1] / total if total > 0 else 0
                }
                for i, row in enumerate(rows)
            ]
        }
    
    elif list_type == "usernames":
        from app.models.attack import Credential
        result = await session.execute(
            select(
                Credential.username,
                func.count(Credential.id).label('count')
            )
            .group_by(Credential.username)
            .order_by(desc('count'))
            .limit(limit)
        )
        rows = result.all()
        total = sum([row[1] for row in rows])
        
        return {
            "type": "usernames",
            "data": [
                {
                    "rank": i + 1,
                    "name": row[0],
                    "value": row[1],
                    "percentage": row[1] / total if total > 0 else 0
                }
                for i, row in enumerate(rows)
            ]
        }
    
    elif list_type == "commands":
        result = await session.execute(
            select(
                Command.command,
                func.count(Command.id).label('count')
            )
            .group_by(Command.command)
            .order_by(desc('count'))
            .limit(limit)
        )
        rows = result.all()
        total = sum([row[1] for row in rows])
        
        return {
            "type": "commands",
            "data": [
                {
                    "rank": i + 1,
                    "name": row[0],
                    "value": row[1],
                    "percentage": row[1] / total if total > 0 else 0
                }
                for i, row in enumerate(rows)
            ]
        }
    
    elif list_type == "payloads":
        from app.models.attack import Download
        result = await session.execute(
            select(
                Download.filename,
                func.count(Download.id).label('count')
            )
            .group_by(Download.filename)
            .order_by(desc('count'))
            .limit(limit)
        )
        rows = result.all()
        total = sum([row[1] for row in rows])
        
        return {
            "type": "payloads",
            "data": [
                {
                    "rank": i + 1,
                    "name": row[0],
                    "value": row[1],
                    "percentage": row[1] / total if total > 0 else 0
                }
                for i, row in enumerate(rows)
            ]
        }
