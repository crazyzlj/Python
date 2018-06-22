#! /usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.zhihu.com/question/25404709
from matplotlib.font_manager import FontManager
import subprocess

fm = FontManager()
mat_fonts = set(f.name for f in fm.ttflist)
#print(mat_fonts)
output = subprocess.check_output('fc-list :lang=zh -f "%{family}\n"', shell=True)
#print( '*' * 10, '系统可用的中文字体', '*' * 10)
#print(output)
zh_fonts = set(f.split(',', 1)[0] for f in output.decode('utf-8').split('\n'))
available = mat_fonts & zh_fonts
print('*' * 10, '可用的字体', '*' * 10)
for f in available:
     print(f)
