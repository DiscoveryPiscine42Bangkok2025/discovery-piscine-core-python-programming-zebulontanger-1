#!/usr/bin/env python3

import sys

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        if sys.argv[i].endswith('ism') == False:
            sys.argv[i] += 'ism'

            print(sys.argv[i])
        else:
            continue
else:
    print('none')