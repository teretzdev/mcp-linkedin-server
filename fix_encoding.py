#!/usr/bin/env python3
"""Fix UTF-16 encoding issue in test_suite.py"""

def fix_file_encoding():
    try:
        # Read the file in binary mode
        with open('test_suite.py', 'rb') as f:
            content = f.read()
        
        # Check if it's UTF-16
        if content.startswith(b'\xff\xfe'):  # UTF-16 LE BOM
            print("Detected UTF-16 encoding, converting to UTF-8...")
            # Decode from UTF-16 and encode to UTF-8
            content_utf8 = content.decode('utf-16').encode('utf-8')
            
            # Write back as UTF-8
            with open('test_suite.py', 'wb') as f:
                f.write(content_utf8)
            
            print("Successfully converted test_suite.py from UTF-16 to UTF-8")
            return True
        else:
            print("File is already in UTF-8 or different encoding")
            return False
            
    except Exception as e:
        print(f"Error fixing encoding: {e}")
        return False

if __name__ == "__main__":
    fix_file_encoding() 