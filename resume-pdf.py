#!/usr/bin/env python

import re
import os

with open('resume.md', 'r') as f, open('/tmp/resume.md', 'w') as g:
  t = f.read()
  t = re.sub(r'## Summary.*?##', r'##', t, flags=re.DOTALL)
  t = re.sub(r'<p class="company">(.*?)</p>', r'**\1**\n\\', t, flags=re.DOTALL)
  t = re.sub(r'<p class="position">(.*?)</p>', r'_\1_\n\\', t, flags=re.DOTALL)
  t = re.sub(r'<details.*</details>', '', t, flags=re.DOTALL)
  t = re.sub(r'<div class="bio">.*?</div>', '', t, flags=re.DOTALL)
  t = re.sub(r'<br/>', r'\n\\', t)
  t = re.sub(r'##', r'#', t)
  print(t)
  g.write(t)

os.system('pandoc /tmp/resume.md -o /tmp/resume.pdf --template eisvogel')
os.system('open /tmp/resume.pdf')
