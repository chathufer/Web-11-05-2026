# -*- coding: utf-8 -*-
with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Add alias
target_colors = 'TEXT_MUTED = ("#94A3B8", "#64748B")'
replacement_colors = 'TEXT_MUTED = ("#94A3B8", "#64748B")\nTEXT_MAIN = TEXT_PRIMARY'

assert target_colors in content, "target_colors not found"
content = content.replace(target_colors, replacement_colors, 1)

# 2. Replace TEXT_MAIN with TEXT_PRIMARY in lines
content = content.replace("text_color=TEXT_MAIN,", "text_color=TEXT_PRIMARY,")

with open("app.py", "w", encoding="utf-8") as f:
    f.write(content)

print("[OK] Fixed TEXT_MAIN in app.py")
