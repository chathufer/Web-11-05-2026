# -*- coding: utf-8 -*-
import re
from collections import Counter

with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

matches = re.findall(r'href="(https://drive\.google\.com/[^"]*)"', text)
print(f'Total drive links in index.html: {len(matches)}')
for k, v in Counter(matches).items():
    print(f'  {k} : {v}')
