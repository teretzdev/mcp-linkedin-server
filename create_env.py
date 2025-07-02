#!/usr/bin/env python3
"""
Create .env file with proper structure for LinkedIn Job Hunter
"""

import os

def create_env_file():
    """Create .env file with basic structure"""
    env_content = """# LinkedIn Credentials
LINKEDIN_USERNAME=
LINKEDIN_PASSWORD=

# OpenAI API Key (for LLM features)
OPENAI_API_KEY=

# Other Configuration
DEBUG=true
"""
    
    try:
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        print("📝 Please update your LinkedIn credentials in the .env file or use the web interface.")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

if __name__ == "__main__":
    create_env_file() 