"""
Authentication Manager
Handles secure credential storage and session management
"""

from cryptography.fernet import Fernet
import json
import os
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
import structlog

logger = structlog.get_logger(__name__)

class AuthManager:
    """Secure authentication manager"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        self.key = encryption_key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
        
        # Store encryption key for persistence
        self._save_encryption_key()
    
    def _save_encryption_key(self):
        """Save encryption key to file"""
        try:
            key_file = self.sessions_dir / "encryption_key.key"
            with open(key_file, 'wb') as f:
                f.write(self.key)
            logger.info("Encryption key saved")
        except Exception as e:
            logger.error("Failed to save encryption key", error=str(e))
    
    def _load_encryption_key(self) -> bool:
        """Load encryption key from file"""
        try:
            key_file = self.sessions_dir / "encryption_key.key"
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    self.key = f.read()
                self.cipher = Fernet(self.key)
                logger.info("Encryption key loaded")
                return True
            return False
        except Exception as e:
            logger.error("Failed to load encryption key", error=str(e))
            return False
    
    def encrypt_credentials(self, username: str, password: str) -> str:
        """Encrypt user credentials"""
        try:
            credentials = {
                "username": username,
                "password": password,
                "timestamp": time.time()
            }
            encrypted_data = self.cipher.encrypt(json.dumps(credentials).encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error("Failed to encrypt credentials", error=str(e))
            raise
    
    def decrypt_credentials(self, encrypted_data: str) -> Dict[str, str]:
        """Decrypt user credentials"""
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data.encode())
            credentials = json.loads(decrypted_data.decode())
            
            # Check if credentials are still valid (24 hours)
            if time.time() - credentials["timestamp"] > 86400:
                raise ValueError("Credentials expired")
            
            return {
                "username": credentials["username"],
                "password": credentials["password"]
            }
        except Exception as e:
            logger.error("Failed to decrypt credentials", error=str(e))
            raise
    
    def save_session(self, session_id: str, cookies: List[Dict[str, Any]]):
        """Save encrypted session cookies"""
        try:
            session_data = {
                "timestamp": time.time(),
                "cookies": cookies
            }
            
            encrypted_data = self.cipher.encrypt(json.dumps(session_data).encode())
            
            session_file = self.sessions_dir / f"{session_id}_session.enc"
            with open(session_file, 'wb') as f:
                f.write(encrypted_data)
            
            logger.debug("Session saved", session_id=session_id)
            
        except Exception as e:
            logger.error("Failed to save session", session_id=session_id, error=str(e))
            raise
    
    def load_session(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Load encrypted session cookies"""
        try:
            session_file = self.sessions_dir / f"{session_id}_session.enc"
            
            if not session_file.exists():
                return None
            
            with open(session_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            session_data = json.loads(decrypted_data.decode())
            
            # Check if session is still valid (24 hours)
            if time.time() - session_data["timestamp"] > 86400:
                logger.info("Session expired", session_id=session_id)
                session_file.unlink()
                return None
            
            logger.debug("Session loaded", session_id=session_id)
            return session_data["cookies"]
            
        except Exception as e:
            logger.error("Failed to load session", session_id=session_id, error=str(e))
            return None
    
    def delete_session(self, session_id: str):
        """Delete session file"""
        try:
            session_file = self.sessions_dir / f"{session_id}_session.enc"
            if session_file.exists():
                session_file.unlink()
                logger.info("Session deleted", session_id=session_id)
        except Exception as e:
            logger.error("Failed to delete session", session_id=session_id, error=str(e))
    
    def list_sessions(self) -> List[str]:
        """List all session files"""
        try:
            sessions = []
            for file in self.sessions_dir.glob("*_session.enc"):
                session_id = file.stem.replace("_session", "")
                sessions.append(session_id)
            return sessions
        except Exception as e:
            logger.error("Failed to list sessions", error=str(e))
            return []
    
    def cleanup_expired_sessions(self):
        """Clean up expired session files"""
        try:
            current_time = time.time()
            expired_count = 0
            
            for file in self.sessions_dir.glob("*_session.enc"):
                try:
                    with open(file, 'rb') as f:
                        encrypted_data = f.read()
                    
                    decrypted_data = self.cipher.decrypt(encrypted_data)
                    session_data = json.loads(decrypted_data.decode())
                    
                    # Check if session is expired (24 hours)
                    if current_time - session_data["timestamp"] > 86400:
                        file.unlink()
                        expired_count += 1
                        
                except Exception:
                    # If we can't decrypt, delete the file
                    file.unlink()
                    expired_count += 1
            
            if expired_count > 0:
                logger.info("Cleaned up expired sessions", count=expired_count)
                
        except Exception as e:
            logger.error("Failed to cleanup expired sessions", error=str(e))
    
    def validate_credentials(self, username: str, password: str) -> bool:
        """Basic credential validation"""
        if not username or not password:
            return False
        
        # Basic validation rules
        if len(username) < 3 or len(username) > 100:
            return False
        
        if len(password) < 6:
            return False
        
        return True
    
    def generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return str(uuid.uuid4()) 