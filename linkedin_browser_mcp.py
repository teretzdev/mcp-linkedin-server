from fastmcp import FastMCP, Context
from playwright.async_api import async_playwright
import asyncio
import os
import json
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import time

# Initialize environment variables
load_dotenv()

# Create MCP server with required dependencies
mcp = FastMCP(
    "Social Browser Automation",
    dependencies=["playwright==1.40.0"]
)

# Helper to save cookies between sessions
async def save_cookies(page, platform):
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
        
        os.makedirs('sessions', exist_ok=True, mode=0o700)  # Secure permissions
        
        # Encrypt cookies before saving
        key = os.getenv('COOKIE_ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        encrypted_data = f.encrypt(json.dumps(cookie_data).encode())
        
        with open(f'sessions/{platform}_cookies.json', 'wb') as f:
            f.write(encrypted_data)
            
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
    
    def __init__(self, platform='linkedin', headless=True, launch_timeout=30000):
        self.platform = platform
        self.headless = headless
        self.launch_timeout = launch_timeout
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def __aenter__(self):
        try:
            self.playwright = await asyncio.wait_for(
                async_playwright().start(),
                timeout=self.launch_timeout/1000
            )
            
            for attempt in range(3):  # Retry logic
                try:
                    self.browser = await self.playwright.chromium.launch(
                        headless=self.headless,
                        timeout=self.launch_timeout
                    )
                    break
                except Exception as e:
                    if attempt == 2:  # Last attempt
                        raise Exception(f"Failed to launch browser after 3 attempts: {str(e)}")
                    await asyncio.sleep(1)
            
            self.context = await self.browser.new_context(
                viewport={'width': 1280, 'height': 720},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
            )
            
            # Try to load existing session
            await load_cookies(self.context, self.platform)
            return self
            
        except asyncio.TimeoutError:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            raise Exception(f"Browser session initialization timed out after {self.launch_timeout}ms")
        except Exception as e:
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            raise Exception(f"Failed to initialize browser session: {str(e)}")
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()
        await self.playwright.stop()
        
    async def new_page(self, url=None):
        page = await self.context.new_page()
        if url:
            await page.goto(url, wait_until='networkidle')
        return page
        
    async def save_session(self, page):
        await save_cookies(page, self.platform)

@mcp.tool()
async def login_linkedin(username: str, password: str, ctx: Context) -> dict:
    """Log into LinkedIn using browser automation"""
    async with BrowserSession(platform='linkedin', headless=False) as session:
        page = await session.new_page('https://www.linkedin.com/login')
        
        # Check if already logged in
        if 'feed' in page.url:
            await session.save_session(page)
            return {"status": "success", "message": "Already logged in"}
        
        ctx.info("Filling login form...")
        # Fill login form
        await page.fill('#username', username)
        await page.fill('#password', password)
        await page.click('button[type="submit"]')
        
        # Handle potential challenges (verification, captcha)
        try:
            # Wait for either feed page or challenge page
            await page.wait_for_navigation(timeout=10000)
            
            # Check for common verification screens
            if await page.query_selector('.challenge-dialog'):
                return {
                    "status": "verification_needed",
                    "message": "LinkedIn requires additional verification. Please complete this manually."
                }
                
            # Check if login successful
            if 'feed' in page.url:
                ctx.info("Login successful, saving session...")
                await session.save_session(page)
                return {"status": "success", "message": "Login successful"}
            else:
                error_text = await page.text_content('.alert-content') or "Unknown error"
                return {"status": "error", "message": f"Login failed: {error_text}"}
                
        except Exception as e:
            return {"status": "error", "message": f"Login process error: {str(e)}"}
        
@mcp.tool()
async def login_linkedin_secure(ctx: Context) -> dict:
    """Log into LinkedIn using credentials from environment variables.
    
    Required environment variables:
    - LINKEDIN_USERNAME: Your LinkedIn email/username
    - LINKEDIN_PASSWORD: Your LinkedIn password
    
    Returns:
        dict: Login status and message
    """
    username = os.getenv('LINKEDIN_USERNAME', '').strip()
    password = os.getenv('LINKEDIN_PASSWORD', '').strip()
    
    # Validate credentials
    if not username or not password:
        return {
            "status": "error",
            "message": "Missing LinkedIn credentials in environment variables. Please set LINKEDIN_USERNAME and LINKEDIN_PASSWORD"
        }
        
    # Basic email validation
    if not '@' in username or not '.' in username:
        return {
            "status": "error",
            "message": "Invalid email format in LINKEDIN_USERNAME"
        }
        
    # Password validation
    if len(password) < 8:
        return {
            "status": "error",
            "message": "LinkedIn password must be at least 8 characters"
        }
    
    # Rate limiting check
    rate_limit_file = 'sessions/login_attempts.json'
    try:
        with open(rate_limit_file, 'r') as f:
            attempts = json.load(f)
            last_attempt = attempts.get('last_attempt', 0)
            count = attempts.get('count', 0)
            
            # Reset counter if more than 1 hour has passed
            if time.time() - last_attempt > 3600:
                count = 0
            
            # Check rate limit (max 5 attempts per hour)
            if count >= 5 and time.time() - last_attempt < 3600:
                return {
                    "status": "error",
                    "message": f"Rate limit exceeded. Please try again in {int((3600 - (time.time() - last_attempt))/60)} minutes"
                }
    except FileNotFoundError:
        count = 0
        
    # Update rate limiting
    os.makedirs('sessions', exist_ok=True)
    with open(rate_limit_file, 'w') as f:
        json.dump({
            'last_attempt': time.time(),
            'count': count + 1
        }, f)
    
    ctx.info("Attempting LinkedIn login with credentials from environment...")
    try:
        result = await login_linkedin(username, password, ctx)
        
        # Reset rate limit on successful login
        if result['status'] == 'success':
            with open(rate_limit_file, 'w') as f:
                json.dump({
                    'last_attempt': time.time(),
                    'count': 0
                }, f)
                
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Login failed: {str(e)}"
        }

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
                await ctx.report_progress(i/count, 1.0)
                
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
            await ctx.report_progress(0.2, 1.0)
            
            # Wait for search results
            await page.wait_for_selector('.reusable-search__result-container', timeout=10000)
            ctx.info("Search results loaded")
            
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
            
            await ctx.report_progress(0.9, 1.0)
            await session.save_session(page)
            
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
        
        
