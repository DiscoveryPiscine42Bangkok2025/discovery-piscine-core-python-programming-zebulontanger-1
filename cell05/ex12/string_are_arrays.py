#!/usr/bin/env python3
import sys
import re

if len(sys.argv) > 1:
    txt = sys.argv[1]

    x = re.findall('z', txt)

    out = ''

    for i in range(len(x)):
        out += 'z'

    print(out)

else:
    print('none')