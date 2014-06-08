import re
from pprint import pprint

lines = []
f = '/home/lsc/template.xml'
ls = open(f).readlines()
for line in ls:
    single = re.finditer('%[a-z_-]+%', line)
    new_line = line
    for item in single:
        new_line = new_line.replace(item.group(), 'SINGLE_ITEM')
    lines.append(new_line)

# =====================================================

input = ''
for line in ls:
    input += line

group = re.finditer(r"\*[a-zA-Z]+\*", input)

for g in group:
    x = g.group()
    y = x.replace('*', '*/')[:len(x) + 1]

    print y

# =====================================================

print
print
print
for line in lines:
    pprint(line)