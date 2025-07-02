#!/usr/bin/env python3
"""
Fix .env file encoding issues
"""

import os
from dotenv import load_dotenv

# Load current environment
load_dotenv()

# Get current credentials
username = os.getenv('LINKEDIN_USERNAME', '')
password = os.getenv('LINKEDIN_PASSWORD', '')

# Create new .env file with proper UTF-8 encoding
with open('.env', 'w', encoding='utf-8') as f:
    f.write(f'LINKEDIN_USERNAME={username}\n')
    f.write(f'LINKEDIN_PASSWORD={password}\n')

print("Fixed .env file with proper UTF-8 encoding")
print(f"Username: {username}")
print(f"Password: {'*' * len(password) if password else 'Not set'}") 