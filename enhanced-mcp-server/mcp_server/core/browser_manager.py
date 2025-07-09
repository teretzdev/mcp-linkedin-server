"""
Enhanced Browser Manager
Manages browser sessions with improved error handling and session persistence
"""

import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional, Dict, Any, List
import logging
import time
import json
from pathlib import Path
import structlog
import sys
sys.path.append(str(Path(__file__).resolve().parent.parent.parent.parent / 'shared'))
from linkedin_login import robust_linkedin_login_playwright

logger = structlog.get_logger(__name__)

class BrowserManager:
    """Enhanced browser session manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.playwright = None
        self.browser = None
        self._sessions: Dict[str, BrowserContext] = {}
        self._session_metadata: Dict[str, Dict[str, Any]] = {}
        self._initialized = False
        
        # Browser configuration
        self.headless = config.get("headless", True)
        self.timeout = config.get("timeout", 30000)
        self.max_retries = config.get("max_retries", 3)
        
        # Session storage
        self.sessions_dir = Path("sessions")
        self.sessions_dir.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize the browser manager"""
        if self._initialized:
            return True
        
        try:
            logger.info("Initializing browser manager")
            
            # Start Playwright
            self.playwright = await async_playwright().start()
            
            # Launch browser
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                timeout=self.timeout,
                args=[
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            self._initialized = True
            logger.info("Browser manager initialized successfully")
            return True
            
        except Exception as e:
            logger.error("Failed to initialize browser manager", error=str(e))
            await self.cleanup()
            return False
    
    async def create_session(self, session_id: str, headless: Optional[bool] = None) -> BrowserContext:
        """Create a new browser session"""
        if not self._initialized:
            await self.initialize()
        
        if session_id in self._sessions:
            logger.info("Session already exists", session_id=session_id)
            return self._sessions[session_id]
        
        try:
            logger.info("Creating new browser session", session_id=session_id)
            
            # Create browser context
            context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                ignore_https_errors=True,
                extra_http_headers={
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
                }
            )
            
            # Load existing cookies if available
            await self._load_session_cookies(context, session_id)
            
            # Open a page and ensure robust login
            page = await context.new_page()
            login_success = await robust_linkedin_login_playwright(context, page)
            if not login_success:
                logger.error("Manual login failed or not on feed page.", session_id=session_id)
                raise Exception("LinkedIn login failed. Please try again.")
            await page.close()
            
            # Store session
            self._sessions[session_id] = context
            self._session_metadata[session_id] = {
                "created_at": time.time(),
                "last_activity": time.time(),
                "headless": headless if headless is not None else self.headless
            }
            
            logger.info("Browser session created and logged in", session_id=session_id)
            return context
            
        except Exception as e:
            logger.error("Failed to create browser session", session_id=session_id, error=str(e))
            raise
    
    async def get_session(self, session_id: str) -> Optional[BrowserContext]:
        """Get existing session or create new one"""
        if session_id in self._sessions:
            # Update activity
            if session_id in self._session_metadata:
                self._session_metadata[session_id]["last_activity"] = time.time()
            return self._sessions[session_id]
        
        # Create new session if not exists
        return await self.create_session(session_id)
    
    async def cleanup_session(self, session_id: str):
        """Clean up a specific browser session"""
        try:
            if session_id in self._sessions:
                context = self._sessions[session_id]
                
                # Save cookies before closing
                await self._save_session_cookies(context, session_id)
                
                # Close context
                await context.close()
                
                # Remove from tracking
                del self._sessions[session_id]
                if session_id in self._session_metadata:
                    del self._session_metadata[session_id]
                
                logger.info("Browser session cleaned up", session_id=session_id)
                
        except Exception as e:
            logger.error("Failed to cleanup session", session_id=session_id, error=str(e))
    
    async def cleanup_all(self):
        """Clean up all browser sessions"""
        try:
            logger.info("Cleaning up all browser sessions")
            
            # Clean up all sessions
            for session_id in list(self._sessions.keys()):
                await self.cleanup_session(session_id)
            
            # Close browser
            if self.browser:
                await self.browser.close()
            
            # Stop Playwright
            if self.playwright:
                await self.playwright.stop()
            
            self._initialized = False
            logger.info("All browser sessions cleaned up")
            
        except Exception as e:
            logger.error("Failed to cleanup all sessions", error=str(e))
    
    async def _save_session_cookies(self, context: BrowserContext, session_id: str):
        """Save session cookies to file"""
        try:
            cookies = await context.cookies()
            
            cookie_data = {
                "timestamp": time.time(),
                "cookies": cookies
            }
            
            cookie_file = self.sessions_dir / f"{session_id}_cookies.json"
            with open(cookie_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            logger.debug("Session cookies saved", session_id=session_id)
            
        except Exception as e:
            logger.warning("Failed to save session cookies", session_id=session_id, error=str(e))
    
    async def _load_session_cookies(self, context: BrowserContext, session_id: str):
        """Load session cookies from file"""
        try:
            cookie_file = self.sessions_dir / f"{session_id}_cookies.json"
            
            if not cookie_file.exists():
                return
            
            with open(cookie_file, 'r') as f:
                cookie_data = json.load(f)
            
            # Check if cookies are still valid (24 hours)
            if time.time() - cookie_data["timestamp"] > 86400:
                logger.info("Session cookies expired", session_id=session_id)
                cookie_file.unlink()
                return
            
            # Add cookies to context
            await context.add_cookies(cookie_data["cookies"])
            logger.debug("Session cookies loaded", session_id=session_id)
            
        except Exception as e:
            logger.warning("Failed to load session cookies", session_id=session_id, error=str(e))
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id in self._session_metadata:
            return self._session_metadata[session_id].copy()
        return None
    
    def list_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self._sessions)
    
    async def is_session_valid(self, session_id: str) -> bool:
        """Check if a session is still valid"""
        if session_id not in self._sessions:
            return False
        
        try:
            # Try to create a new page to test if context is still valid
            context = self._sessions[session_id]
            page = await context.new_page()
            await page.close()
            return True
        except Exception:
            # Session is invalid, clean it up
            await self.cleanup_session(session_id)
            return False 