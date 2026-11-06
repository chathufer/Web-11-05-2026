import os

base_dir = r"c:\Users\Chathufer\Downloads\Youtube video dowonloader"

html_files = [
    os.path.join(base_dir, "index.html"),
    os.path.join(base_dir, "public", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "index.html"),
    os.path.join(base_dir, "deploy_vercel", "public", "index.html"),
]

py_files = [
    os.path.join(base_dir, "backend", "website_html.py"),
    os.path.join(base_dir, "deploy_vercel", "backend", "website_html.py"),
]

wa_link_snippet = '<a href="https://chat.whatsapp.com/GwABzhDv3z8CAIXINR1hMG" target="_blank" rel="noopener noreferrer" style="display:block; text-align:center; font-size:12px; color:#25D366; margin-top:10px; font-weight:700; text-decoration:none;"><span style="text-decoration:underline;">💬 Buy via WhatsApp Group</span> &rarr;</a>'

# Monthly
target_mon = """          <button class="btn btn-line trigger-checkout" data-plan="pro_monthly" style="width: 100%;">
            <span>Get Monthly Pass ($1.99)</span>
            <svg class="ic"><use href="#i-arrow-ne"></use></svg>
          </button>"""

repl_mon = target_mon + "\n          " + wa_link_snippet

# Yearly
target_yea = """          <button class="btn btn-line trigger-checkout" data-plan="pro_yearly" style="width: 100%;">
            <span>Get Annual Pass ($14.99)</span>
            <svg class="ic"><use href="#i-arrow-ne"></use></svg>
          </button>"""

repl_yea = target_yea + "\n          " + wa_link_snippet

# Lifetime
target_lft = """          <button class="btn btn-gold trigger-checkout" data-plan="pro_lifetime" style="width: 100%;">
            <span>Get Lifetime License ($24.99)</span>
            <svg class="ic"><use href="#i-arrow"></use></svg>
          </button>"""

repl_lft = target_lft + "\n          " + wa_link_snippet

for f in html_files + py_files:
    if not os.path.exists(f):
        continue
    with open(f, "r", encoding="utf-8") as fp:
        c = fp.read()
    if target_mon in c:
        c = c.replace(target_mon, repl_mon)
    if target_yea in c:
        c = c.replace(target_yea, repl_yea)
    if target_lft in c:
        c = c.replace(target_lft, repl_lft)
    with open(f, "w", encoding="utf-8", newline="\r\n") as fp:
        fp.write(c)
    print(f"[OK] Added direct WhatsApp links to pricing cards in {f}")

print("Done!")
