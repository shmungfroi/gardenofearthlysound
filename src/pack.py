"""Pack the live page: inline the built map and layout into the template, write ../index.html."""
import re, os
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'out')
svg = open(os.path.join(OUT, 'map.svg')).read()
inner = re.sub(r'^<svg[^>]*>', '', svg).rsplit('</svg>', 1)[0]
inner = re.sub(r'<g id="chrome">.*?</g>\s*', '', inner, flags=re.S)          # the frame replaces the preview's own chrome
lay = open(os.path.join(OUT, 'layout.json')).read()
t = open(os.path.join(HERE, 'template.html')).read().replace('%%MAP%%', inner).replace('%%LAYOUT%%', lay)
open(os.path.join(ROOT, 'index.html'), 'w').write(t)
print('packed index.html', len(t) // 1024, 'KB')
