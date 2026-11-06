import os
import re
import glob

pattern = re.compile(r'https://drive\.google\.com/file/d/[a-zA-Z0-9_-]+[^\s"\'<>]*')
unique_urls = set()

for ext in ('*.html', '*.py', '*.json'):
    for p in glob.glob(f'**/{ext}', recursive=True):
        if 'scratch' in p or '.git' in p or 'build' in p:
            continue
        try:
            with open(p, 'r', encoding='utf-8') as f:
                content = f.read()
                matches = pattern.findall(content)
                for m in matches:
                    unique_urls.add(m)
        except Exception as e:
            pass

print("Unique Google Drive URLs found:")
for u in sorted(unique_urls):
    print(" ", u)
