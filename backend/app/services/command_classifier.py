"""
Command classification utilities
"""

from app.models.attack import CommandClassification


def classify_command(command: str) -> CommandClassification:
    """
    Classify a command into a category based on keywords
    """
    command_lower = command.lower()
    
    # Reconnaissance keywords
    recon_keywords = [
        'whoami', 'id', 'uname', 'cat', 'ls', 'pwd', 'ifconfig', 
        'ip', 'ps', 'netstat', 'ss', 'hostname', 'w', 'who', 'env'
    ]
    
    # File download keywords
    download_keywords = [
        'wget', 'curl', 'ftp', 'scp', 'sftp', 'lynx', 'fetch', 'python -m'
    ]
    
    # Command execution keywords
    exec_keywords = [
        'bash', 'sh', 'python', 'perl', 'ruby', './', '/bin/', 'exec', 'eval'
    ]
    
    # Persistence keywords
    persist_keywords = [
        'cron', 'crontab', 'systemd', 'service', 'chkconfig', 'update-rc.d',
        'at', 'launchd', 'plist'
    ]
    
    # Networking keywords
    network_keywords = [
        'ifconfig', 'ip', 'route', 'iptables', 'netstat', 'ss', 'arp',
        'traceroute', 'ping', 'nmap', 'nc', 'netcat', 'dig', 'nslookup'
    ]
    
    # Privilege escalation keywords
    privesc_keywords = [
        'sudo', 'su ', 'chmod', 'chown', 'setuid', 'setgid', 'setcap',
        'visudo', 'adduser', 'useradd'
    ]
    
    # Check each category
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
    
    # Default to reconnaissance if no match
    return CommandClassification.RECONNAISSANCE


def get_command_severity_score(classification: CommandClassification) -> int:
    """
    Get severity score (0-100) for a command classification
    """
    severity_scores = {
        CommandClassification.RECONNAISSANCE: 20,
        CommandClassification.FILE_DOWNLOAD: 70,
        CommandClassification.EXECUTION: 75,
        CommandClassification.PERSISTENCE: 95,
        CommandClassification.NETWORKING: 40,
        CommandClassification.PRIVILEGE_ESCALATION: 90
    }
    return severity_scores.get(classification, 10)
