"""
Cowrie log parser for ingesting attack data into database
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.attack import (
    Attack, Session as DBSession, Command, Download, Credential,
    Attacker, EventType, Severity, CommandClassification, SessionStatus
)


class CowrieParser:
    """
    Parses Cowrie JSON logs and ingests them into the database
    """
    
    def __init__(self):
        self.engine = None
        self.async_session = None
    
    async def init(self):
        """Initialize database connection"""
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            pool_pre_ping=True
        )
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def parse_file(self, filepath: str):
        """Parse a Cowrie JSON log file"""
        log_file = Path(filepath)
        
        if not log_file.exists():
            print(f"Log file not found: {filepath}")
            return
        
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    await self.process_log_entry(data)
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing log entry: {e}")
    
    async def process_log_entry(self, entry: dict):
        """Process a single log entry"""
        async with self.async_session() as session:
            try:
                event_type = entry.get('eventid')
                timestamp_str = entry.get('timestamp')
                src_ip = entry.get('src_ip', 'UNKNOWN')
                
                if not timestamp_str:
                    return
                
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                
                # Ensure attacker exists
                await self._ensure_attacker(session, src_ip)
                
                # Process different event types
                if event_type == 'cowrie.session.connect':
                    await self._handle_connect(session, entry, timestamp)
                
                elif event_type == 'cowrie.login.attempt':
                    await self._handle_login_attempt(session, entry, timestamp)
                
                elif event_type == 'cowrie.login.success':
                    await self._handle_login_success(session, entry, timestamp)
                
                elif event_type == 'cowrie.command.input':
                    await self._handle_command_input(session, entry, timestamp)
                
                elif event_type == 'cowrie.session.file_download':
                    await self._handle_download(session, entry, timestamp)
                
                elif event_type == 'cowrie.session.closed':
                    await self._handle_session_closed(session, entry, timestamp)
                
                await session.commit()
            
            except Exception as e:
                print(f"Error processing log entry: {e}")
                await session.rollback()
    
    async def _ensure_attacker(self, session: AsyncSession, ip: str):
        """Ensure attacker record exists"""
        from sqlalchemy import select
        
        result = await session.execute(
            select(Attacker).where(Attacker.ip_address == ip)
        )
        attacker = result.scalar_one_or_none()
        
        if not attacker:
            # Create new attacker (with placeholder country)
            attacker = Attacker(
                ip_address=ip,
                country_code='UNKNOWN',
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow()
            )
            session.add(attacker)
            await session.flush()
        else:
            attacker.last_seen = datetime.utcnow()
            session.add(attacker)
            await session.flush()
    
    async def _handle_connect(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle connection event"""
        src_ip = entry.get('src_ip')
        session_id = entry.get('session')
        
        # Create attack event
        attack = Attack(
            timestamp=timestamp,
            attacker_ip=src_ip,
            event_type=EventType.CONNECTION,
            severity=Severity.INFO,
            country_code='UNKNOWN'
        )
        session.add(attack)
        await session.flush()
        
        # Create session record
        db_session = DBSession(
            id=session_id,
            attacker_ip=src_ip,
            start_time=timestamp,
            status=SessionStatus.ACTIVE,
            protocol=entry.get('protocol', 'ssh').lower()
        )
        session.add(db_session)
    
    async def _handle_login_attempt(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle login attempt"""
        src_ip = entry.get('src_ip')
        session_id = entry.get('session')
        username = entry.get('username', 'unknown')
        password = entry.get('password', 'unknown')
        
        # Create attack event
        attack = Attack(
            timestamp=timestamp,
            session_id=session_id,
            attacker_ip=src_ip,
            event_type=EventType.AUTH_ATTEMPT,
            severity=Severity.LOW,
            country_code='UNKNOWN'
        )
        session.add(attack)
        
        # Record credential attempt
        cred = Credential(
            session_id=session_id,
            timestamp=timestamp,
            username=username,
            password=password,
            success=False
        )
        session.add(cred)
    
    async def _handle_login_success(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle successful login"""
        src_ip = entry.get('src_ip')
        session_id = entry.get('session')
        username = entry.get('username', 'unknown')
        password = entry.get('password', 'unknown')
        
        # Create attack event
        attack = Attack(
            timestamp=timestamp,
            session_id=session_id,
            attacker_ip=src_ip,
            event_type=EventType.LOGIN,
            severity=Severity.MEDIUM,
            country_code='UNKNOWN'
        )
        session.add(attack)
        
        # Update credential as successful
        cred = Credential(
            session_id=session_id,
            timestamp=timestamp,
            username=username,
            password=password,
            success=True
        )
        session.add(cred)
    
    async def _handle_command_input(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle command execution"""
        src_ip = entry.get('src_ip')
        session_id = entry.get('session')
        command = entry.get('input', 'unknown')
        
        # Classify command
        classification = self._classify_command(command)
        
        # Create attack event
        attack = Attack(
            timestamp=timestamp,
            session_id=session_id,
            attacker_ip=src_ip,
            event_type=EventType.COMMAND,
            severity=self._calculate_command_severity(classification),
            country_code='UNKNOWN'
        )
        session.add(attack)
        
        # Record command
        cmd = Command(
            session_id=session_id,
            timestamp=timestamp,
            command=command,
            classification=classification,
            success=True
        )
        session.add(cmd)
    
    async def _handle_download(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle payload download"""
        src_ip = entry.get('src_ip')
        session_id = entry.get('session')
        filename = entry.get('filename', 'unknown')
        
        # Create attack event
        attack = Attack(
            timestamp=timestamp,
            session_id=session_id,
            attacker_ip=src_ip,
            event_type=EventType.DOWNLOAD,
            severity=Severity.HIGH,
            country_code='UNKNOWN'
        )
        session.add(attack)
        
        # Record download
        download = Download(
            session_id=session_id,
            timestamp=timestamp,
            filename=filename,
            url=entry.get('url')
        )
        session.add(download)
    
    async def _handle_session_closed(self, session: AsyncSession, entry: dict, timestamp: datetime):
        """Handle session close"""
        session_id = entry.get('session')
        
        # Update session
        from sqlalchemy import select
        result = await session.execute(
            select(DBSession).where(DBSession.id == session_id)
        )
        db_session = result.scalar_one_or_none()
        
        if db_session:
            db_session.end_time = timestamp
            db_session.status = SessionStatus.COMPLETE
            
            if db_session.start_time:
                duration = (timestamp - db_session.start_time).total_seconds()
                db_session.duration_seconds = int(duration)
            
            session.add(db_session)
    
    def _classify_command(self, command: str) -> CommandClassification:
        """Classify a command based on its content"""
        command_lower = command.lower()
        
        recon_keywords = ['whoami', 'id', 'uname', 'cat', 'ls', 'pwd', 'ifconfig', 'ip', 'ps']
        download_keywords = ['wget', 'curl', 'ftp', 'scp']
        exec_keywords = ['bash', 'sh', 'python', 'perl', 'ruby', './']
        persist_keywords = ['cron', 'systemd', 'service', 'chkconfig']
        network_keywords = ['ifconfig', 'ip', 'route', 'iptables', 'netstat', 'ss']
        privesc_keywords = ['sudo', 'su', 'chmod']
        
        for keyword in recon_keywords:
            if keyword in command_lower:
                return CommandClassification.RECONNAISSANCE
        
        for keyword in download_keywords:
            if keyword in command_lower:
                return CommandClassification.FILE_DOWNLOAD
        
        for keyword in exec_keywords:
            if keyword in command_lower:
                return CommandClassification.EXECUTION
        
        for keyword in persist_keywords:
            if keyword in command_lower:
                return CommandClassification.PERSISTENCE
        
        for keyword in network_keywords:
            if keyword in command_lower:
                return CommandClassification.NETWORKING
        
        for keyword in privesc_keywords:
            if keyword in command_lower:
                return CommandClassification.PRIVILEGE_ESCALATION
        
        return CommandClassification.RECONNAISSANCE
    
    def _calculate_command_severity(self, classification: CommandClassification) -> Severity:
        """Calculate severity based on command classification"""
        severity_map = {
            CommandClassification.RECONNAISSANCE: Severity.LOW,
            CommandClassification.FILE_DOWNLOAD: Severity.HIGH,
            CommandClassification.EXECUTION: Severity.HIGH,
            CommandClassification.PERSISTENCE: Severity.CRITICAL,
            CommandClassification.NETWORKING: Severity.MEDIUM,
            CommandClassification.PRIVILEGE_ESCALATION: Severity.CRITICAL
        }
        return severity_map.get(classification, Severity.LOW)


async def main():
    """Main entry point for log parser"""
    parser = CowrieParser()
    await parser.init()
    
    # Parse log file (adjust path as needed)
    cowrie_log_path = "/var/log/cowrie/cowrie.json"
    await parser.parse_file(cowrie_log_path)
    
    print("Log parsing complete")


if __name__ == "__main__":
    asyncio.run(main())
