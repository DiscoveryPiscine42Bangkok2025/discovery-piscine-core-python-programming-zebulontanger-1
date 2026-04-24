#!/usr/bin/env python3

import sys
import re

if len(sys.argv) > 2:
    txt = sys.argv[2]
    find = sys.argv[1]

    x = re.findall(find, txt)

    print(len(x))

else:
    print('none')