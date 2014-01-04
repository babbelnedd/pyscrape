# -*- coding: utf-8 -*-
# __author__ = 'LSC'
# import sys, os, time, shutil
#
# chars = {}
# with open('replace') as f:
#     content = f.readlines()
# for c in content:
#     c = c.split(':')
#     x = c[0]
#
#     try:
#         y = c[1]
#     except:
#         y = ''
#     chars[x] = y
#
# def replace(string):
#     if type(string) == unicode:
#         string = string.encode('utf8')
#     for char in chars.keys():
#         key = char
#         value = chars[key]
#         string = string.replace(key.strip(), value.strip())
#     return string
#
# path = "c:\\DEV\\TMP\\pyscrape\\"
# for d in os.walk(path):
#     d = d[0]
#     if d.endswith('extrafanart'):
#         continue
#     root, folder = os.path.split(d)
#     x = folder.decode('unicode-escape').encode('utf8')
#     orig_folder = x
#     x = replace(x)
#
#     if orig_folder != x:
#         src = unicode(os.path.join(root, orig_folder), 'utf8')
#         dst = unicode(os.path.join(root, x), 'utf8')
#         os.rename(src, dst)
#
#         for sub in os.walk(dst):
#             files = sub[2]
#             for file in files:
#                 src = unicode(os.path.join(dst, file))
#                 f = replace(file)
#                 if f == file:
#                     continue
#                 f = unicode(os.path.join(dst, f))
#                 try:
#                     os.rename(src, f)
#                 except:
#                     pass