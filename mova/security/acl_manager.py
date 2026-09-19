"""
Mova Core ACL Manager - Access Control Lists and Security
Moved from movadev to avoid duplication - this is the core security layer
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import re

from ..mova_logging.logger import MovaLogger


class SecurityLevel(Enum):
    """Poziomy bezpieczeństwa"""
    OPEN = "open"
    RESTRICTED = "restricted"
    SECURE = "secure"
    LOCKED = "locked"


@dataclass
class SecurityPolicy:
    """Polityka bezpieczeństwa"""
    name: str
    level: SecurityLevel
    allowed_commands: Set[str]
    forbidden_patterns: List[str]
    max_execution_time: int = 30
    max_memory_mb: int = 100
    allow_network_access: bool = True
    allow_file_write: bool = True


@dataclass
class SecurityAuditEntry:
    """Wpis w audycie bezpieczeństwa"""
    timestamp: datetime
    user_id: str
    command: str
    allowed: bool
    reason: str
    context: Dict[str, Any] = field(default_factory=dict)


class ACLManager:
    """
    Core ACL Manager - podstawowy system kontroli dostępu dla ecosystem Mova

    To jest podstawowy komponent który inne projekty mova* powinny rozszerzać,
    a nie duplikować. Zapewnia:
    - Command validation
    - Security policies
    - Audit logging
    - Environment-based configuration
    """

    def __init__(self):
        self.logger = MovaLogger("mova.security.acl")
        self.security_policies: Dict[str, SecurityPolicy] = {}
        self.audit_log: List[SecurityAuditEntry] = []

        # Load from environment
        self._load_security_config()
        self._initialize_default_policies()

        self.logger.info("Mova ACL Manager initialized")

    def _load_security_config(self):
        """Ładuje konfigurację z environment variables"""

        # MOVA_ALLOWED_COMMANDS - główna lista dozwolonych komend
        allowed_commands_env = os.getenv('MOVA_ALLOWED_COMMANDS', '')
        self.global_allowed_commands = set(allowed_commands_env.split(',')) if allowed_commands_env else set()

        # MOVA_SECURITY_LEVEL
        security_level = os.getenv('MOVA_SECURITY_LEVEL', 'restricted')
        try:
            self.default_security_level = SecurityLevel(security_level)
        except ValueError:
            self.default_security_level = SecurityLevel.RESTRICTED
            self.logger.warning(f"Invalid security level '{security_level}', using RESTRICTED")

        # MOVA_ALLOW_SHELL
        self.allow_shell = os.getenv('MOVA_ALLOW_SHELL', 'false').lower() == 'true'

        self.logger.info(f"Security config: level={self.default_security_level.value}, "
                        f"shell={self.allow_shell}, global_commands={len(self.global_allowed_commands)}")

    def _initialize_default_policies(self):
        """Inicjalizuje domyślne polityki"""

        # Development policy
        dev_policy = SecurityPolicy(
            name="development",
            level=SecurityLevel.OPEN,
            allowed_commands={"ls", "pwd", "echo", "cat", "mkdir", "touch", "python3", "node", "npm"},
            forbidden_patterns=[],
        )

        # Production policy
        prod_policy = SecurityPolicy(
            name="production",
            level=SecurityLevel.SECURE,
            allowed_commands={"echo", "pwd"},
            forbidden_patterns=["rm -rf", "dd if=", "mkfs", "> /dev/", "curl.*exec", "wget.*exec"],
            max_execution_time=10,
            max_memory_mb=50,
            allow_network_access=False,
            allow_file_write=False,
        )

        # Restricted policy - default balance
        restricted_policy = SecurityPolicy(
            name="restricted",
            level=SecurityLevel.RESTRICTED,
            allowed_commands=self.global_allowed_commands | {
                "ls", "pwd", "echo", "cat", "mkdir", "touch", "python3", "node", "npm"
            },
            forbidden_patterns=["rm -rf /", "dd if=/dev/", "mkfs", "format", "fdisk"],
            max_execution_time=30,
            max_memory_mb=100,
        )

        self.security_policies = {
            "development": dev_policy,
            "production": prod_policy,
            "restricted": restricted_policy
        }

    def validate_command(self,
                        command: str,
                        user_id: str = "system",
                        policy_name: Optional[str] = None) -> tuple[bool, str]:
        """
        Główna funkcja walidacji komend

        Returns: (allowed: bool, reason: str)
        """

        if not policy_name:
            policy_name = "restricted"

        policy = self.security_policies.get(policy_name)
        if not policy:
            return False, f"Unknown security policy: {policy_name}"

        # Extract base command
        base_command = command.split()[0] if command.strip() else ""

        # Check forbidden patterns
        for pattern in policy.forbidden_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                reason = f"Command matches forbidden pattern: {pattern}"
                self._log_security_event(user_id, command, False, reason)
                return False, reason

        # Shell injection check
        if not self.allow_shell and self._contains_shell_injection(command):
            reason = "Shell injection detected and MOVA_ALLOW_SHELL=false"
            self._log_security_event(user_id, command, False, reason)
            return False, reason

        # Check allowed commands after known-dangerous patterns so callers get
        # the security reason instead of a generic allowlist miss.
        if base_command not in policy.allowed_commands:
            reason = f"Command '{base_command}' not in allowed commands"
            self._log_security_event(user_id, command, False, reason)
            return False, reason

        # Command allowed
        self._log_security_event(user_id, command, True, "Command validated successfully")
        return True, "Command allowed"

    def _contains_shell_injection(self, command: str) -> bool:
        """Sprawdza shell injection"""

        dangerous_patterns = [
            r'[;&|`$]',           # Command separators
            r'>\s*/dev/',         # Writing to device files
            r'<\s*/dev/',         # Reading from device files
            r'\$\(',              # Command substitution
            r'`.*`',              # Backtick substitution
            r'>\s*&',             # Redirect to file descriptor
            r'\|\s*sh',           # Pipe to shell
            r'eval\s+',           # Eval command
            r'exec\s+',           # Exec command
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command):
                return True

        return False

    def get_security_policy(self, policy_name: str) -> Optional[SecurityPolicy]:
        """Zwraca politykę bezpieczeństwa"""
        return self.security_policies.get(policy_name)

    def add_security_policy(self, policy: SecurityPolicy) -> bool:
        """Dodaje nową politykę bezpieczeństwa"""
        self.security_policies[policy.name] = policy
        self.logger.info(f"Added security policy: {policy.name}")
        return True

    def get_audit_log(self, limit: int = 100) -> List[SecurityAuditEntry]:
        """Zwraca logi audytu"""
        return self.audit_log[-limit:]

    def _log_security_event(self, user_id: str, command: str, allowed: bool, reason: str):
        """Loguje zdarzenie bezpieczeństwa"""

        audit_entry = SecurityAuditEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            command=command,
            allowed=allowed,
            reason=reason
        )

        self.audit_log.append(audit_entry)

        # Limit log size
        if len(self.audit_log) > 10000:
            self.audit_log = self.audit_log[-5000:]

        # Log critical events
        if not allowed:
            self.logger.warning(f"Security violation: {user_id} - {command} - {reason}")

    def get_security_report(self) -> Dict[str, Any]:
        """Generuje raport bezpieczeństwa"""

        total_events = len(self.audit_log)
        blocked_events = len([e for e in self.audit_log if not e.allowed])

        return {
            'security_level': self.default_security_level.value,
            'allow_shell': self.allow_shell,
            'total_events': total_events,
            'blocked_events': blocked_events,
            'success_rate': ((total_events - blocked_events) / total_events * 100) if total_events > 0 else 100,
            'policies': list(self.security_policies.keys()),
            'global_allowed_commands': len(self.global_allowed_commands)
        }
