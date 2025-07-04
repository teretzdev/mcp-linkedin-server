from fastmcp import FastMCP, Context
from playwright.async_api import async_playwright
import asyncio
import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import time
import logging
import sys
from pathlib import Path

# Set up logging to stderr only
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def setup_sessions_directory():
    """Set up the sessions directory with proper permissions"""
    try:
        sessions_dir = Path(__file__).parent / 'sessions'
        sessions_dir.mkdir(mode=0o777, parents=True, exist_ok=True)
        # Ensure the directory has the correct permissions even if it already existed
        os.chmod(sessions_dir, 0o777)
        logger.debug(f"Sessions directory set up at {sessions_dir} with full permissions")
        return True
    except Exception as e:
        logger.error(f"Failed to set up sessions directory: {str(e)}")
        return False

# Load environment variables
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.debug(f"Loaded environment from {env_path}")
else:
    logger.warning(f"No .env file found at {env_path}")

# Create MCP server with required dependencies
mcp = FastMCP(
    "linkedin",
    dependencies=[
        "playwright==1.40.0",
        "python-dotenv>=0.19.0",
        "cryptography>=35.0.0",
        "httpx>=0.24.0"
    ],
    debug=True  # Enable debug mode for better error reporting
)

def report_progress(ctx, current, total, message=None):
    """Helper function to report progress with proper validation"""
    try:
        progress = min(1.0, current / total) if total > 0 else 0
        if message:
            ctx.info(message)
        logger.debug(f"Progress: {progress:.2%} - {message if message else ''}")
    except Exception as e:
        logger.error(f"Error reporting progress: {str(e)}")

def handle_notification(ctx, notification_type, params=None):
    """Helper function to handle notifications with proper validation"""
    try:
        if notification_type == "initialized":
            logger.info("MCP Server initialized")
            if ctx:  # Only call ctx.info if ctx is provided
                ctx.info("Server initialized and ready")
        elif notification_type == "cancelled":
            reason = params.get("reason", "Unknown reason")
            logger.warning(f"Operation cancelled: {reason}")
            if ctx:
                ctx.warning(f"Operation cancelled: {reason}")
        else:
            logger.debug(f"Notification: {notification_type} - {params}")
    except Exception as e:
        logger.error(f"Error handling notification: {str(e)}")

# Helper to save cookies between sessions
async def save_cookies(page, platform):
    """Save cookies with proper directory permissions"""
    try:
        cookies = await page.context.cookies()
        
        # Validate cookies
        if not cookies or not isinstance(cookies, list):
            raise ValueError("Invalid cookie format")
            
        # Add timestamp for expiration check
        cookie_data = {
            "timestamp": int(time.time()),
            "cookies": cookies
        }
        
        # Ensure sessions directory exists with proper permissions
        if not setup_sessions_directory():
            raise Exception("Failed to set up sessions directory")
        
        # Encrypt cookies before saving
        key = os.getenv('COOKIE_ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(cookie_data).encode())
        
        cookie_file = Path(__file__).parent / 'sessions' / f'{platform}_cookies.json'
        with open(cookie_file, 'wb') as f:
            f.write(encrypted_data)
        # Set file permissions to 666 (rw-rw-rw-)
        os.chmod(cookie_file, 0o666)
            
    except Exception as e:
        raise Exception(f"Failed to save cookies: {str(e)}")

# Helper to load cookies
async def load_cookies(context, platform):
    try:
        with open(f'sessions/{platform}_cookies.json', 'rb') as f:
            encrypted_data = f.read()
            
        # Decrypt cookies
        key = os.getenv('COOKIE_ENCRYPTION_KEY')
        if not key:
            return False
            
        f = Fernet(key)
        cookie_data = json.loads(f.decrypt(encrypted_data))
        
        # Check cookie expiration (24 hours)
        if int(time.time()) - cookie_data["timestamp"] > 86400:
            os.remove(f'sessions/{platform}_cookies.json')
            return False
            
        await context.add_cookies(cookie_data["cookies"])
        return True
        
    except FileNotFoundError:
        return False
    except Exception as e:
        # If there's any error loading cookies, delete the file and start fresh
        try:
            os.remove(f'sessions/{platform}_cookies.json')
        except:
            pass
        return False
    
class BrowserSession:
    """Context manager for browser sessions with cookie persistence"""
    
    def __init__(self, platform='linkedin', headless=True, launch_timeout=30000, max_retries=3):
        logger.info(f"Initializing {platform} browser session (headless: {headless})")
        self.platform = platform
        self.headless = headless
        self.launch_timeout = launch_timeout
        self.max_retries = max_retries
        self.playwright = None
        self.browser = None
        self.context = None
        self._closed = False
        
    async def __aenter__(self):
        retry_count = 0
        last_error = None
        
        # Ensure sessions directory exists with proper permissions
        if not setup_sessions_directory():
            raise Exception("Failed to set up sessions directory with proper permissions")
        
        while retry_count < self.max_retries and not self._closed:
            try:
                logger.info(f"Starting Playwright (attempt {retry_count + 1}/{self.max_retries})")
                
                # Ensure clean state
                await self._cleanup()
                
                # Initialize Playwright with timeout
                self.playwright = await asyncio.wait_for(
                    async_playwright().start(),
                    timeout=self.launch_timeout/1000
                )
                
                # Launch browser with more generous timeout and retry logic
                launch_success = False
                for attempt in range(3):
                    try:
                        logger.info(f"Launching browser (sub-attempt {attempt + 1}/3)")
                        self.browser = await self.playwright.chromium.launch(
                            headless=self.headless,
                            timeout=self.launch_timeout,
                            args=[
                                '--disable-dev-shm-usage',
                                '--no-sandbox',
                                '--disable-blink-features=AutomationControlled',  # Try to avoid detection
                                '--start-maximized'  # Start with maximized window
                            ]
                        )
                        launch_success = True
                        break
                    except Exception as e:
                        logger.error(f"Browser launch sub-attempt {attempt + 1} failed: {str(e)}")
                        await asyncio.sleep(2)  # Increased delay between attempts
                
                if not launch_success:
                    raise Exception("Failed to launch browser after 3 attempts")
                
                logger.info("Creating browser context")
                self.context = await self.browser.new_context(
                    viewport={'width': 1280, 'height': 800},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
                )
                
                # Try to load existing session
                logger.info("Attempting to load existing session")
                try:
                    session_loaded = await load_cookies(self.context, self.platform)
                    if session_loaded:
                        logger.info("Existing session loaded successfully")
                    else:
                        logger.info("No existing session found or session expired")
                except Exception as cookie_error:
                    logger.warning(f"Error loading cookies: {str(cookie_error)}")
                    # Continue even if cookie loading fails
                
                return self
                
            except Exception as e:
                last_error = e
                retry_count += 1
                logger.error(f"Browser session initialization attempt {retry_count} failed: {str(e)}")
                
                # Cleanup on failure
                await self._cleanup()
                
                if retry_count < self.max_retries and not self._closed:
                    await asyncio.sleep(2 * retry_count)  # Exponential backoff
                else:
                    logger.error("All browser session initialization attempts failed")
                    raise Exception(f"Failed to initialize browser after {self.max_retries} attempts. Last error: {str(last_error)}")

    async def _cleanup(self):
        """Clean up browser resources"""
        if self.browser:
            try:
                await self.browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {str(e)}")
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception as e:
                logger.error(f"Error stopping playwright: {str(e)}")
        self.browser = None
        self.playwright = None
        self.context = None

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("Closing browser session")
        self._closed = True
        await self._cleanup()
        
    async def new_page(self, url=None):
        if self._closed:
            raise Exception("Browser session has been closed")
        
        page = await self.context.new_page()
        if url:
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
            except Exception as e:
                logger.error(f"Error navigating to {url}: {str(e)}")
                raise
        return page
        
    async def save_session(self, page):
        if self._closed:
            raise Exception("Browser session has been closed")
            
        try:
            await save_cookies(page, self.platform)
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
            raise

@mcp.tool()
async def login_linkedin(username: str | None = None, password: str | None = None, ctx: Context | None = None) -> dict:
    """Open LinkedIn login page in browser for manual login.
    Username and password are optional - if not provided, user will need to enter them manually."""
    
    logger.info("Starting LinkedIn login with browser for manual login")

    # Auto-login when both credentials are provided
    if username and password:
        logger.info("Auto-login with provided credentials")
        async with BrowserSession(platform='linkedin') as session:
            page = await session.new_page()
            await page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            # Pre-fill and submit credentials
            await page.fill('#username', username)
            await page.fill('#password', password)
            await page.click('button[type="submit"]')
            try:
                await page.wait_for_url('**/feed/**', timeout=60000)
                if ctx:
                    ctx.info("Login successful")
                logger.info("Auto login successful")
                await session.save_session(page)
                return {"status": "success", "message": "Login successful"}
            except Exception as e:
                logger.error(f"Auto login failed: {str(e)}")
                return {"status": "error", "message": "Login failed with provided credentials"}

    # Create browser session with explicit window size and position
    async with BrowserSession(platform='linkedin', headless=False) as session:
        try:
            # Configure browser window
            page = await session.new_page()
            await page.set_viewport_size({'width': 1280, 'height': 800})
            
            # Navigate to LinkedIn login
            await page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            
            # Check if already logged in
            if 'feed' in page.url:
                await session.save_session(page)
                return {"status": "success", "message": "Already logged in"}
            
            if ctx:
                ctx.info("Please log in manually through the browser window...")
                ctx.info("The browser will wait for up to 5 minutes for you to complete the login.")
            logger.info("Waiting for manual login...")
            
            # Pre-fill credentials if provided
            try:
                if username:
                    await page.fill('#username', username)
                if password:
                    await page.fill('#password', password)
            except Exception as e:
                logger.warning(f"Failed to pre-fill credentials: {str(e)}")
                # Continue anyway - user can enter manually
            
            # Wait for successful login (feed page)
            try:
                await page.wait_for_url('**/feed/**', timeout=300000)  # 5 minutes timeout
                if ctx:
                    ctx.info("Login successful!")
                logger.info("Manual login successful")
                await session.save_session(page)
                # Keep browser open for a moment to show success
                await asyncio.sleep(3)
                return {"status": "success", "message": "Manual login successful"}
            except Exception as e:
                logger.error(f"Login timeout: {str(e)}")
                return {
                    "status": "error",
                    "message": "Login timeout. Please try again and complete login within 5 minutes."
                }
                
        except Exception as e:
            logger.error(f"Login process error: {str(e)}")
            return {"status": "error", "message": f"Login process error: {str(e)}"}

@mcp.tool()
async def login_linkedin_secure(ctx: Context | None = None) -> dict:
    """Open LinkedIn login page in browser for manual login using environment credentials as default values.
    
    Optional environment variables:
    - LINKEDIN_USERNAME: Your LinkedIn email/username (will be pre-filled if provided)
    - LINKEDIN_PASSWORD: Your LinkedIn password (will be pre-filled if provided)
    
    Returns:
        dict: Login status and message
    """
    logger.info("Starting secure LinkedIn login")
    username = os.getenv('LINKEDIN_USERNAME', '').strip()
    password = os.getenv('LINKEDIN_PASSWORD', '').strip()

    # Validate credentials
    if not username or not password:
        return {"status": "error", "message": "Missing LinkedIn credentials"}
    import re
    if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
        return {"status": "error", "message": "Invalid email format"}
    if len(password) < 8:
        return {"status": "error", "message": "password must be at least 8 characters"}

    # Proceed with secure login
    return await login_linkedin(username if username else None, password if password else None, ctx)

@mcp.tool()
async def get_linkedin_profile(username: str, ctx: Context) -> dict:
    """Get LinkedIn profile information"""
    async with BrowserSession(platform='linkedin', headless=False) as session:
        page = await session.new_page(f'https://www.linkedin.com/in/{username}')
        
        # Check if profile page loaded
        if 'profile' not in page.url:
            return {"status": "error", "message": "Profile page not found"}
            
@mcp.tool()
async def browse_linkedin_feed(ctx: Context, count: int = 5) -> dict:
    """Browse LinkedIn feed and return recent posts
    
    Args:
        ctx: MCP context for logging and progress reporting
        count: Number of posts to retrieve (default: 5)
        
    Returns:
        dict: Contains status, posts array, and any errors
    """
    posts = []
    errors = []
    
    async with BrowserSession(platform='linkedin') as session:
        try:
            page = await session.new_page('https://www.linkedin.com/feed/')
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            ctx.info(f"Browsing feed for {count} posts...")
            
            # Scroll to load content
            for i in range(min(count, 20)):  # Limit to reasonable number
                report_progress(ctx, i, count, f"Loading post {i+1}/{count}")
                
                try:
                    # Wait for posts to be visible
                    await page.wait_for_selector('.feed-shared-update-v2', timeout=5000)
                    
                    # Extract visible posts
                    new_posts = await page.evaluate('''() => {
                        return Array.from(document.querySelectorAll('.feed-shared-update-v2'))
                            .map(post => {
                                try {
                                    return {
                                        author: post.querySelector('.feed-shared-actor__name')?.innerText?.trim() || 'Unknown',
                                        headline: post.querySelector('.feed-shared-actor__description')?.innerText?.trim() || '',
                                        content: post.querySelector('.feed-shared-text')?.innerText?.trim() || '',
                                        timestamp: post.querySelector('.feed-shared-actor__sub-description')?.innerText?.trim() || '',
                                        likes: post.querySelector('.social-details-social-counts__reactions-count')?.innerText?.trim() || '0'
                                    };
                                } catch (e) {
                                    return null;
                                }
                            })
                            .filter(p => p !== null);
                    }''')
                    
                    # Add new posts to our collection, avoiding duplicates
                    for post in new_posts:
                        if post not in posts:
                            posts.append(post)
                            
                    if len(posts) >= count:
                        break
                        
                    # Scroll down to load more content
                    await page.evaluate('window.scrollBy(0, 800)')
                    await page.wait_for_timeout(1000)  # Wait for content to load
                    
                except Exception as scroll_error:
                    errors.append(f"Error during scroll {i}: {str(scroll_error)}")
                    continue
            
            # Save session cookies
            await session.save_session(page)
            
            return {
                "status": "success",
                "posts": posts[:count],
                "count": len(posts),
                "errors": errors if errors else None
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to browse feed: {str(e)}",
                "posts": posts,
                "errors": errors
            }
        

@mcp.tool()
async def search_linkedin_profiles(query: str, ctx: Context, count: int = 5) -> dict:
    """Search for LinkedIn profiles matching a query"""
    async with BrowserSession(platform='linkedin') as session:
        try:
            search_url = f'https://www.linkedin.com/search/results/people/?keywords={query}'
            page = await session.new_page(search_url)
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
            
            ctx.info(f"Searching for profiles matching: {query}")
            report_progress(ctx, 20, 100, "Loading search results...")
            
            # Wait for search results
            await page.wait_for_selector('.reusable-search__result-container', timeout=10000)
            ctx.info("Search results loaded")
            report_progress(ctx, 50, 100, "Extracting profile data...")
            
            # Extract profile data
            profiles = await page.evaluate('''(count) => {
                const results = [];
                const profileCards = document.querySelectorAll('.reusable-search__result-container');
                
                for (let i = 0; i < Math.min(profileCards.length, count); i++) {
                    const card = profileCards[i];
                    try {
                        const profile = {
                            name: card.querySelector('.entity-result__title-text a')?.innerText?.trim() || 'Unknown',
                            headline: card.querySelector('.entity-result__primary-subtitle')?.innerText?.trim() || '',
                            location: card.querySelector('.entity-result__secondary-subtitle')?.innerText?.trim() || '',
                            profileUrl: card.querySelector('.app-aware-link')?.href || '',
                            connectionDegree: card.querySelector('.dist-value')?.innerText?.trim() || '',
                            snippet: card.querySelector('.entity-result__summary')?.innerText?.trim() || ''
                        };
                        results.push(profile);
                    } catch (e) {
                        console.error("Error extracting profile", e);
                    }
                }
                return results;
            }''', count)
            
            report_progress(ctx, 90, 100, "Saving session...")
            await session.save_session(page)
            report_progress(ctx, 100, 100, "Search complete")
            
            return {
                "status": "success",
                "profiles": profiles,
                "count": len(profiles),
                "query": query
            }
            
        except Exception as e:
            ctx.error(f"Profile search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to search profiles: {str(e)}"
            }
        
@mcp.tool() 
async def view_linkedin_profile(profile_url: str, ctx: Context) -> dict:
    """Visit and extract data from a specific LinkedIn profile"""
    if not ('linkedin.com/in/' in profile_url):
        return {
            "status": "error",
            "message": "Invalid LinkedIn profile URL. Should contain 'linkedin.com/in/'"
        }
        
    async with BrowserSession(platform='linkedin') as session:
        try:
            page = await session.new_page(profile_url)
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            ctx.info(f"Viewing profile: {profile_url}")
            
            # Wait for profile to load
            await page.wait_for_selector('.pv-top-card', timeout=10000)
            await ctx.report_progress(0.5, 1.0)
            
            # Extract profile information
            profile_data = await page.evaluate('''() => {
                const getData = (selector, property = 'innerText') => {
                    const element = document.querySelector(selector);
                    return element ? element[property].trim() : null;
                };
                
                return {
                    name: getData('.pv-top-card--list .text-heading-xlarge'),
                    headline: getData('.pv-top-card--list .text-body-medium'),
                    location: getData('.pv-top-card--list .text-body-small:not(.inline)'),
                    connectionDegree: getData('.pv-top-card__connections-count .t-black--light'),
                    about: getData('.pv-shared-text-with-see-more .inline-show-more-text'),
                    experience: Array.from(document.querySelectorAll('#experience-section .pv-entity__summary-info'))
                        .map(exp => ({
                            title: exp.querySelector('h3')?.innerText?.trim() || '',
                            company: exp.querySelector('.pv-entity__secondary-title')?.innerText?.trim() || '',
                            duration: exp.querySelector('.pv-entity__date-range span:not(.visually-hidden)')?.innerText?.trim() || ''
                        })),
                    education: Array.from(document.querySelectorAll('#education-section .pv-education-entity'))
                        .map(edu => ({
                            school: edu.querySelector('.pv-entity__school-name')?.innerText?.trim() || '',
                            degree: edu.querySelector('.pv-entity__degree-name .pv-entity__comma-item')?.innerText?.trim() || '',
                            field: edu.querySelector('.pv-entity__fos .pv-entity__comma-item')?.innerText?.trim() || '',
                            dates: edu.querySelector('.pv-entity__dates span:not(.visually-hidden)')?.innerText?.trim() || ''
                        }))
                };
            }''')
            
            await ctx.report_progress(1.0, 1.0)
            await session.save_session(page)
            
            return {
                "status": "success",
                "profile": profile_data,
                "url": profile_url
            }
            
        except Exception as e:
            ctx.error(f"Profile viewing failed: {str(e)}")
            return {
                "status": "error", 
                "message": f"Failed to extract profile data: {str(e)}"
            }
        

@mcp.tool()
async def interact_with_linkedin_post(post_url: str, ctx: Context, action: str = "like", comment: str = None) -> dict:
    """Interact with a LinkedIn post (like, comment)"""
    if not ('linkedin.com/posts/' in post_url or 'linkedin.com/feed/update/' in post_url):
        return {
            "status": "error",
            "message": "Invalid LinkedIn post URL"
        }
        
    valid_actions = ["like", "comment", "read"]
    if action not in valid_actions:
        return {
            "status": "error",
            "message": f"Invalid action. Choose from: {', '.join(valid_actions)}"
        }
        
    async with BrowserSession(platform='linkedin', headless=False) as session:
        try:
            page = await session.new_page(post_url)
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            # Wait for post to load
            await page.wait_for_selector('.feed-shared-update-v2', timeout=10000)
            ctx.info(f"Post loaded, performing action: {action}")
            
            # Read post content
            post_content = await page.evaluate('''() => {
                const post = document.querySelector('.feed-shared-update-v2');
                return {
                    author: post.querySelector('.feed-shared-actor__name')?.innerText?.trim() || 'Unknown',
                    content: post.querySelector('.feed-shared-text')?.innerText?.trim() || '',
                    engagementCount: post.querySelector('.social-details-social-counts__reactions-count')?.innerText?.trim() || '0'
                };
            }''')
            
            # Perform the requested action
            if action == "like":
                # Find and click like button if not already liked
                liked = await page.evaluate('''() => {
                    const likeButton = document.querySelector('button.react-button__trigger');
                    const isLiked = likeButton.getAttribute('aria-pressed') === 'true';
                    if (!isLiked) {
                        likeButton.click();
                        return true;
                    }
                    return false;
                }''')
                
                result = {
                    "status": "success",
                    "action": "like",
                    "performed": liked,
                    "message": "Successfully liked the post" if liked else "Post was already liked"
                }
                
            elif action == "comment" and comment:
                # Add comment to the post
                await page.click('button.comments-comment-box__trigger')  # Open comment box
                await page.fill('.ql-editor', comment)
                await page.click('button.comments-comment-box__submit-button')  # Submit comment
                
                # Wait for comment to appear
                await page.wait_for_timeout(2000)
                
                result = {
                    "status": "success",
                    "action": "comment",
                    "message": "Comment posted successfully"
                }
                
            else:  # action == "read"
                result = {
                    "status": "success",
                    "action": "read",
                    "post": post_content
                }
                
            await session.save_session(page)
            return result
            
        except Exception as e:
            ctx.error(f"Post interaction failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to interact with post: {str(e)}"
            }
        
        

@mcp.tool()
async def search_linkedin_jobs(query: str, ctx: Context, location: str = '', filters: dict = None, count: int = 10) -> dict:
    """Search for LinkedIn jobs matching a query and location"""
    filters = filters or {}
    async with BrowserSession(platform='linkedin') as session:
        try:
            # Build the LinkedIn jobs search URL
            base_url = 'https://www.linkedin.com/jobs/search/?keywords=' + query.replace(' ', '%20')
            if location:
                base_url += f'&location={location.replace(" ", "%20")}'
            # Add filters if needed (e.g., remote, experience level)
            # For now, just use query and location
            page = await session.new_page(base_url)

            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error",
                    "message": "Not logged in. Please run login_linkedin tool first"
                }

            ctx.info(f"Searching for jobs: {query} in {location}")
            report_progress(ctx, 20, 100, "Loading job search results...")

            # Wait for job cards to load
            await page.wait_for_selector('.jobs-search-results__list-item', timeout=10000)
            ctx.info("Job search results loaded")
            report_progress(ctx, 50, 100, "Extracting job data...")

            # Extract job data
            jobs = await page.evaluate('''(count) => {
                const results = [];
                const jobCards = document.querySelectorAll('.jobs-search-results__list-item');
                for (let i = 0; i < Math.min(jobCards.length, count); i++) {
                    const card = jobCards[i];
                    try {
                        const job = {
                            title: card.querySelector('.base-search-card__title')?.innerText?.trim() || '',
                            company: card.querySelector('.base-search-card__subtitle')?.innerText?.trim() || '',
                            location: card.querySelector('.job-search-card__location')?.innerText?.trim() || '',
                            posted: card.querySelector('time')?.getAttribute('datetime') || '',
                            jobUrl: card.querySelector('a.base-card__full-link')?.href || '',
                            descriptionSnippet: card.querySelector('.job-search-card__snippet')?.innerText?.trim() || ''
                        };
                        results.push(job);
                    } catch (e) {
                        // skip
                    }
                }
                return results;
            }''', count)

            report_progress(ctx, 90, 100, "Saving session...")
            await session.save_session(page)
            report_progress(ctx, 100, 100, "Job search complete")

            return {
                "status": "success",
                "jobs": jobs,
                "count": len(jobs),
                "query": query,
                "location": location
            }
        except Exception as e:
            ctx.error(f"Job search failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to search jobs: {str(e)}"
            }

@mcp.tool()
async def apply_to_linkedin_job(job_url: str, ctx: Context, resume_path: str = '', cover_letter_path: str = '') -> dict:
    """Apply to a LinkedIn job (Easy Apply only)"""
    if not ('linkedin.com/jobs/view/' in job_url):
        return {
            "status": "error",
            "message": "Invalid LinkedIn job URL. Should contain 'linkedin.com/jobs/view/'"
        }
        
    async with BrowserSession(platform='linkedin', headless=False) as session:
        try:
            page = await session.new_page(job_url)
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            ctx.info(f"Applying to job: {job_url}")
            report_progress(ctx, 20, 100, "Loading job page...")
            
            # Wait for job page to load
            await page.wait_for_selector('.jobs-unified-top-card__job-title', timeout=10000)
            ctx.info("Job page loaded")
            report_progress(ctx, 40, 100, "Looking for Easy Apply button...")
            
            # Check if Easy Apply is available
            easy_apply_button = await page.query_selector('button[aria-label*="Easy Apply"]')
            if not easy_apply_button:
                return {
                    "status": "error",
                    "message": "Easy Apply not available for this job. Manual application required."
                }
            
            # Click Easy Apply button
            await easy_apply_button.click()
            ctx.info("Easy Apply button clicked")
            report_progress(ctx, 60, 100, "Processing application...")
            
            # Wait for application modal
            await page.wait_for_selector('.jobs-easy-apply-modal', timeout=5000)
            
            # Handle application steps (simplified - just submit if possible)
            try:
                # Look for submit button
                submit_button = await page.query_selector('button[aria-label="Submit application"]')
                if submit_button:
                    await submit_button.click()
                    ctx.info("Application submitted")
                    report_progress(ctx, 90, 100, "Application submitted successfully")
                    
                    # Save to applied jobs tracking
                    await save_applied_job_tracking(job_url, page)
                    
                    await session.save_session(page)
                    return {
                        "status": "success",
                        "message": "Successfully applied to job",
                        "job_url": job_url
                    }
                else:
                    return {
                        "status": "partial",
                        "message": "Application started but manual completion required",
                        "job_url": job_url
                    }
            except Exception as apply_error:
                return {
                    "status": "partial",
                    "message": f"Application started but encountered issues: {str(apply_error)}",
                    "job_url": job_url
                }
                
        except Exception as e:
            ctx.error(f"Job application failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to apply to job: {str(e)}"
            }

@mcp.tool()
async def save_linkedin_job(job_url: str, ctx: Context) -> dict:
    """Save a LinkedIn job"""
    if not ('linkedin.com/jobs/view/' in job_url):
        return {
            "status": "error",
            "message": "Invalid LinkedIn job URL. Should contain 'linkedin.com/jobs/view/'"
        }
        
    async with BrowserSession(platform='linkedin') as session:
        try:
            page = await session.new_page(job_url)
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            ctx.info(f"Saving job: {job_url}")
            report_progress(ctx, 20, 100, "Loading job page...")
            
            # Wait for job page to load
            await page.wait_for_selector('.jobs-unified-top-card__job-title', timeout=10000)
            ctx.info("Job page loaded")
            report_progress(ctx, 50, 100, "Looking for save button...")
            
            # Look for save button
            save_button = await page.query_selector('button[aria-label*="Save job"]')
            if not save_button:
                # Try alternative selectors
                save_button = await page.query_selector('.jobs-save-button')
            
            if save_button:
                await save_button.click()
                ctx.info("Job saved")
                report_progress(ctx, 90, 100, "Job saved successfully")
                
                # Save to saved jobs tracking
                await save_saved_job_tracking(job_url, page)
                
                await session.save_session(page)
                return {
                    "status": "success",
                    "message": "Successfully saved job",
                    "job_url": job_url
                }
            else:
                return {
                    "status": "error",
                    "message": "Could not find save button for this job"
                }
                
        except Exception as e:
            ctx.error(f"Job save failed: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to save job: {str(e)}"
            }

# Helper functions for job tracking
async def save_applied_job_tracking(job_url: str, page):
    """Save applied job to local tracking"""
    try:
        # Extract job details
        job_data = await page.evaluate('''() => {
            return {
                title: document.querySelector('.jobs-unified-top-card__job-title')?.innerText?.trim() || '',
                company: document.querySelector('.jobs-unified-top-card__company-name')?.innerText?.trim() || '',
                location: document.querySelector('.jobs-unified-top-card__bullet')?.innerText?.trim() || '',
                date_applied: new Date().toISOString(),
                job_url: window.location.href
            };
        }''')
        
        # Load existing applied jobs
        applied_jobs = []
        try:
            with open('applied_jobs.json', 'r') as f:
                applied_jobs = json.load(f)
        except FileNotFoundError:
            pass
        
        # Add new job if not already present
        if not any(job['job_url'] == job_url for job in applied_jobs):
            applied_jobs.append(job_data)
            
            # Save back to file
            with open('applied_jobs.json', 'w') as f:
                json.dump(applied_jobs, f, indent=2)
                
    except Exception as e:
        logger.error(f"Failed to save applied job tracking: {str(e)}")

async def save_saved_job_tracking(job_url: str, page):
    """Save saved job to local tracking"""
    try:
        # Extract job details
        job_data = await page.evaluate('''() => {
            return {
                title: document.querySelector('.jobs-unified-top-card__job-title')?.innerText?.trim() || '',
                company: document.querySelector('.jobs-unified-top-card__company-name')?.innerText?.trim() || '',
                location: document.querySelector('.jobs-unified-top-card__bullet')?.innerText?.trim() || '',
                date_saved: new Date().toISOString(),
                job_url: window.location.href
            };
        }''')
        
        # Load existing saved jobs
        saved_jobs = []
        try:
            with open('saved_jobs.json', 'r') as f:
                saved_jobs = json.load(f)
        except FileNotFoundError:
            pass
        
        # Add new job if not already present
        if not any(job['job_url'] == job_url for job in saved_jobs):
            saved_jobs.append(job_data)
            
            # Save back to file
            with open('saved_jobs.json', 'w') as f:
                json.dump(saved_jobs, f, indent=2)
                
    except Exception as e:
        logger.error(f"Failed to save saved job tracking: {str(e)}")

@mcp.tool()
async def list_applied_jobs(ctx: Context) -> dict:
    """List jobs you've applied to"""
    try:
        # Load applied jobs from local tracking
        try:
            with open('applied_jobs.json', 'r') as f:
                applied_jobs = json.load(f)
        except FileNotFoundError:
            applied_jobs = []
        
        return {
            "status": "success",
            "applied_jobs": applied_jobs,
            "count": len(applied_jobs)
        }
    except Exception as e:
        ctx.error(f"Failed to list applied jobs: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to list applied jobs: {str(e)}",
            "applied_jobs": []
        }

@mcp.tool()
async def get_job_recommendations(ctx: Context) -> dict:
    """Get job recommendations from LinkedIn"""
    async with BrowserSession(platform='linkedin') as session:
        try:
            # Go to LinkedIn jobs recommendations page
            page = await session.new_page('https://www.linkedin.com/jobs/')
            
            # Check if we're logged in
            if 'login' in page.url:
                return {
                    "status": "error", 
                    "message": "Not logged in. Please run login_linkedin tool first"
                }
                
            ctx.info("Loading job recommendations...")
            report_progress(ctx, 20, 100, "Loading recommendations page...")
            
            # Wait for job cards to load
            await page.wait_for_selector('.jobs-search-results__list-item', timeout=10000)
            ctx.info("Recommendations loaded")
            report_progress(ctx, 50, 100, "Extracting recommended jobs...")
            
            # Extract recommended job data
            recommended_jobs = await page.evaluate('''() => {
                const results = [];
                const jobCards = document.querySelectorAll('.jobs-search-results__list-item');
                for (let i = 0; i < Math.min(jobCards.length, 10); i++) {
                    const card = jobCards[i];
                    try {
                        const job = {
                            title: card.querySelector('.base-search-card__title')?.innerText?.trim() || '',
                            company: card.querySelector('.base-search-card__subtitle')?.innerText?.trim() || '',
                            location: card.querySelector('.job-search-card__location')?.innerText?.trim() || '',
                            posted: card.querySelector('time')?.getAttribute('datetime') || '',
                            jobUrl: card.querySelector('a.base-card__full-link')?.href || '',
                            descriptionSnippet: card.querySelector('.job-search-card__snippet')?.innerText?.trim() || ''
                        };
                        results.push(job);
                    } catch (e) {
                        // skip
                    }
                }
                return results;
            }''')
            
            report_progress(ctx, 90, 100, "Saving session...")
            await session.save_session(page)
            report_progress(ctx, 100, 100, "Recommendations complete")
            
            return {
                "status": "success",
                "recommended_jobs": recommended_jobs,
                "count": len(recommended_jobs)
            }
            
        except Exception as e:
            ctx.error(f"Failed to get job recommendations: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to get job recommendations: {str(e)}",
                "recommended_jobs": []
            }

@mcp.tool()
async def list_saved_jobs(ctx: Context) -> dict:
    """List jobs you've saved"""
    try:
        # Load saved jobs from local tracking
        try:
            with open('saved_jobs.json', 'r') as f:
                saved_jobs = json.load(f)
        except FileNotFoundError:
            saved_jobs = []
        
        return {
            "status": "success",
            "saved_jobs": saved_jobs,
            "count": len(saved_jobs)
        }
    except Exception as e:
        ctx.error(f"Failed to list saved jobs: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to list saved jobs: {str(e)}",
            "saved_jobs": []
        }

if __name__ == "__main__":
    try:
        logger.debug("Starting LinkedIn MCP Server with debug logging")
        
        # Initialize MCP server with simple configuration
        try:
            handle_notification(None, "initialized")  # Pass None for ctx during initialization
            mcp.run(transport='stdio')
        except KeyboardInterrupt:
            handle_notification(None, "cancelled", {"reason": "Server stopped by user"})
            logger.info("Server stopped by user")
        except Exception as e:
            handle_notification(None, "cancelled", {"reason": str(e)})
            logger.error(f"Server error: {str(e)}", exc_info=True)
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)
        sys.exit(1)
        
