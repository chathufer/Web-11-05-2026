files = [
    'index.html',
    'public/index.html',
    'deploy_vercel/index.html',
    'deploy_vercel/public/index.html',
    'backend/website_html.py',
    'deploy_vercel/backend/website_html.py'
]
old_str = 'Current Latest: <strong class="dyn-latest-ver">v2.2.0</strong>'
new_str = 'Current Latest: <strong class="dyn-latest-ver">v2.3.0</strong>'
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    if old_str in c:
        c = c.replace(old_str, new_str)
        with open(f, 'w', encoding='utf-8', newline='\r\n') as fp:
            fp.write(c)
        print('[OK] Updated in', f)
print("Finished!")
