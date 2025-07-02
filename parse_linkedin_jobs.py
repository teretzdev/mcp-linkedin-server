import re
import os

# Path to the scraped LinkedIn HTML file
file_path = r"C:/Users/Shadow/AppData/Local/Block/goose/cache/computer_controller/web_20250630_051207.txt"

try:
    if not os.path.exists(file_path):
        print(f"Error: Scraped file not found at {file_path}.")
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Relaxed regex to find text within any <h3> tags
        job_title_pattern = re.compile(r'<h3[^>]*>(.*?)</h3>', re.IGNORECASE | re.DOTALL)

        found_titles = []
        for match in job_title_pattern.finditer(html_content):
            potential_title_group = match.group(1)
            if potential_title_group:
                # Clean up any inner HTML tags and extra whitespace
                clean_title = re.sub(r'<[^>]+>', '', potential_title_group).strip()
                # Remove common LinkedIn "badge" text like "(New)", "(Promoted)", "(Easy Apply)"
                clean_title = re.sub(r'\s*\\(New|Promoted|Easy Apply)\\s*$', '', clean_title, flags=re.IGNORECASE).strip()
                
                # Filter for "webdeveloper" or related terms
                if ('web' in clean_title.lower() or 'developer' in clean_title.lower() or 'frontend' in clean_title.lower() or 'backend' in clean_title.lower()) and clean_title and clean_title not in found_titles:
                    found_titles.append(clean_title)

        if found_titles:
            print("Found Job Titles (filtered for 'webdeveloper' related terms):")
            for title in found_titles:
                print(f"- {title}")
        else:
            print("No job titles found using the current parsing methods or no 'webdeveloper' related jobs found. The HTML structure might have changed or the regex needs refinement.")

except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
