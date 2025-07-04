#!/usr/bin/env python3
"""
Create .env file with proper structure for LinkedIn Job Hunter
"""

import os

def create_env_file():
    """Create .env file with basic structure"""
    env_content = """# LinkedIn Credentials
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password

# Gemini API Key (for AI features)
GEMINI_API_KEY=your_gemini_api_key

# OpenAI API Key (for LLM features)
OPENAI_API_KEY=your_openai_api_key

# Cookie Encryption Key (auto-generated)
COOKIE_ENCRYPTION_KEY=

# Other Configuration
DEBUG=true
HEADLESS=true
TIMEOUT=30000
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("[SUCCESS] .env file created successfully!")
        print("[INFO] Please update your LinkedIn credentials in the .env file or use the web interface.")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file() 